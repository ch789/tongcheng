from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import httpx
import os
import random
import time
from datetime import timedelta

from app.database import get_db
from app.models import users as user_models
from app.schemas import LoginResponse, UserOut, ProfileUpdate
from app.utils.password import verify_password
from app.utils.jwt_utils import create_access_token, decode_access_token
from app.config import WECHAT_TOKEN_URL, WECHAT_APPID, WECHAT_SECRET

router = APIRouter(prefix="/auth", tags=["认证"])

# 短信验证码缓存: {phone: (code, expire_timestamp)}
_sms_codes: dict[str, tuple[str, float]] = {}
_SMS_CODE_TTL_SECONDS = 300  # 5分钟有效期


# 测试手机号固定验证码
_TEST_SMS_CODES = {
    "13800001111": "123456",
    "13800002222": "123456",
}


def _generate_sms_code(length: int = 6) -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def _get_sms_code(phone: str) -> str | None:
    entry = _sms_codes.get(phone)
    if entry is None:
        return None
    code, expire_at = entry
    if time.time() > expire_at:
        _sms_codes.pop(phone, None)
        return None
    return code


def get_current_user(request: Request = None, db: Session = Depends(get_db)):
    """从请求头中解析 JWT，返回当前用户"""
    auth_header = request.headers.get("Authorization", "") if request else ""
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = auth_header[7:]
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Token 无效")
    user = db.query(user_models.User).filter(user_models.User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if user.is_disabled:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    return user


async def _get_wechat_openid(code: str) -> str | None:
    """调用微信接口换取 openid"""
    if not WECHAT_APPID or not WECHAT_SECRET:
        return None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(WECHAT_TOKEN_URL, params={
                "appid": WECHAT_APPID,
                "secret": WECHAT_SECRET,
                "js_code": code,
                "grant_type": "authorization_code",
            }, timeout=10.0)
            data = resp.json()
            if "openid" in data:
                return data["openid"]
            return None
    except Exception:
        return None


@router.post("/wechat/login", response_model=LoginResponse)
async def wechat_login(request: Request, db: Session = Depends(get_db)):
    """微信授权登录"""
    body = await request.json()
    code = body.get("code", "")
    if not code:
        raise HTTPException(status_code=400, detail="缺少 code 参数")

    openid = await _get_wechat_openid(code)
    if not openid:
        raise HTTPException(status_code=400, detail="微信授权失败，请确认微信 AppID 和 Secret 已正确配置")

    user = db.query(user_models.User).filter(user_models.User.openid == openid).first()
    if not user:
        user = user_models.User(openid=openid, role=user_models.UserRole.USER)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return LoginResponse(access_token=token, user_id=user.id, role=user.role.value)


@router.post("/sms/send")
async def send_sms(request: Request, db: Session = Depends(get_db)):
    """发送短信验证码（开发环境直接返回验证码，生产环境走短信服务商）"""
    body = await request.json()
    phone = body.get("phone", "")
    if not phone:
        raise HTTPException(status_code=400, detail="缺少手机号")

    # 测试手机号固定验证码
    if phone in _TEST_SMS_CODES:
        code = _TEST_SMS_CODES[phone]
    else:
        code = _generate_sms_code()

    _sms_codes[phone] = (code, time.time() + _SMS_CODE_TTL_SECONDS)

    # TODO: 接入短信服务商，通过短信发送 code
    return {"message": "验证码已发送", "code": code}  # dev 模式返回验证码供前端显示


@router.post("/phone/login", response_model=LoginResponse)
async def phone_login(request: Request, db: Session = Depends(get_db)):
    """手机号+验证码登录"""
    body = await request.json()
    phone = body.get("phone", "")
    code = body.get("code", "")

    if not phone or not code:
        raise HTTPException(status_code=400, detail="缺少手机号或验证码")

    stored_code = _get_sms_code(phone)
    if not stored_code or stored_code != code:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    user = db.query(user_models.User).filter(user_models.User.phone == phone).first()
    if not user:
        user = user_models.User(phone=phone, role=user_models.UserRole.USER)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return LoginResponse(access_token=token, user_id=user.id, role=user.role.value)


@router.post("/password/register", response_model=LoginResponse)
async def password_register(request: Request, db: Session = Depends(get_db)):
    """账号密码注册（备用登录方式）"""
    body = await request.json()
    phone = body.get("phone", "")
    password = body.get("password", "")
    nickname = body.get("nickname", "")

    if not phone or not password:
        raise HTTPException(status_code=400, detail="缺少手机号或密码")

    from app.utils.password import hash_password
    user = db.query(user_models.User).filter(user_models.User.phone == phone).first()
    if user:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    user = user_models.User(
        phone=phone,
        password_hash=hash_password(password),
        nickname=nickname or f"老乡_{phone[-4:]}",
        role=user_models.UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return LoginResponse(access_token=token, user_id=user.id, role=user.role.value)


@router.post("/password/login", response_model=LoginResponse)
async def password_login(request: Request, db: Session = Depends(get_db)):
    """账号密码登录（管理后台等场景）"""
    body = await request.json()
    phone = body.get("phone", "")
    password = body.get("password", "")

    if not phone or not password:
        raise HTTPException(status_code=400, detail="缺少手机号或密码")

    from app.utils.password import verify_password
    user = db.query(user_models.User).filter(user_models.User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=401, detail="账号不存在")
    if not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="密码错误")
    if user.is_disabled:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return LoginResponse(access_token=token, user_id=user.id, role=user.role.value)


@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: user_models.User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserOut(
        id=current_user.id,
        role=current_user.role.value,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        phone_masked=current_user.phone[:3] + "****" + current_user.phone[-4:] if current_user.phone else None,
        created_at=current_user.created_at,
    )


@router.put("/profile", response_model=UserOut)
async def update_profile(
    data: ProfileUpdate,
    current_user: user_models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人信息"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    db.commit()
    db.refresh(current_user)
    return UserOut(
        id=current_user.id,
        role=current_user.role.value,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        phone_masked=current_user.phone[:3] + "****" + current_user.phone[-4:] if current_user.phone else None,
        created_at=current_user.created_at,
    )
