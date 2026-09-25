from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File as FastapiFile
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
import os

from app.database import get_db
from app.models import products as product_models, users as user_models, activities as activity_models, merchants as merchant_models, home as home_models, ads as ads_models, notifications as notification_models, industries as industry_models
from app.models.products import ProductStatus
from app.schemas import (
    ProductOut, IndustryOut, PaginatedResponse,
    ActivityOut, ActivityCreate, ActivityUpdate,
    AdOut, AdCreate, HomeContentUpdate, HomeContentOut,
    MerchantApplicationOut, MerchantApply,
    NotificationOut, ProductAdminUpdate,
)
from app.utils.jwt_utils import decode_access_token
from app.utils.file_utils import upload_file, upload_file_compressed, mask_phone

router = APIRouter(prefix="", tags=["后台管理"])


# ── 文件上传 ─────────────────────────────────────────────────────────────────
@router.post("/upload")
async def upload_image(
    file: UploadFile = FastapiFile(...),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """上传图片，返回访问 URL"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    from app.utils.file_utils import upload_file
    path = await upload_file(file, sub_dir="admin")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    return {"url": f"{BASE_URL}{path}", "path": path}


@router.post("/upload-compressed")
async def upload_image_compressed(
    file: UploadFile = FastapiFile(...),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """上传图片（支持超限自动压缩），返回访问 URL 及是否经过压缩"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    path, was_compressed = await upload_file_compressed(file, sub_dir="admin")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    return {"url": f"{BASE_URL}{path}", "path": path, "compressed": was_compressed}


def require_admin(user_id: int, db: Session):
    """验证管理员权限，失败抛异常"""
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user or user.role != user_models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无权限访问")
    return user


def get_current_user_id(request: Request = None) -> Optional[int]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header[7:])
        if payload and "user_id" in payload:
            return payload["user_id"]
    return None


# ── 首页内容管理 ─────────────────────────────────────────────────────────────
@router.get("/home", response_model=HomeContentOut)
async def get_home_content(db: Session = Depends(get_db)):
    home = db.query(home_models.HomeContent).first()
    slogan = home.slogan if home else None
    announcement = home.announcement if home else None
    updated_at = home.updated_at if home else None

    # 同时返回广告列表
    ads = db.query(ads_models.Ad).filter(
        ads_models.Ad.status == ads_models.AdStatus.ACTIVE
    ).order_by(ads_models.Ad.sort_order.asc()).all()
    ads_data = [
        {"id": a.id, "title": a.title, "image": a.image, "link": a.link, "sort_order": a.sort_order}
        for a in ads
    ]

    return HomeContentOut(slogan=slogan, announcement=announcement, ads=ads_data, updated_at=updated_at)


@router.put("/home", response_model=HomeContentOut)
async def update_home_content(
    data: HomeContentUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    home = db.query(home_models.HomeContent).first()
    if not home:
        home = home_models.HomeContent()
        db.add(home)

    if data.slogan is not None:
        home.slogan = data.slogan
    if data.announcement is not None:
        home.announcement = data.announcement

    db.commit()
    db.refresh(home)
    return HomeContentOut(slogan=home.slogan, announcement=home.announcement, updated_at=home.updated_at)


# ── 产品管理 ─────────────────────────────────────────────────────────────────
@router.get("/products", response_model=PaginatedResponse)
async def list_products_admin(
    db: Session = Depends(get_db),
    keyword: str = Query(default=""),
    industry_id: Optional[int] = Query(default=None),
    area: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    request: Request = None,
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    q = db.query(product_models.Product)
    if keyword:
        q = q.filter(or_(
            product_models.Product.title.ilike(f"%{keyword}%"),
            product_models.Product.description.ilike(f"%{keyword}%"),
        ))
    if industry_id:
        q = q.filter(product_models.Product.industry_id == industry_id)
    if area:
        q = q.filter(product_models.Product.area == area)
    if status:
        q = q.filter(product_models.Product.status == status)

    total = q.count()
    items = q.order_by(product_models.Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    from math import ceil
    return PaginatedResponse(
        items=[{k: v for k, v in p.__dict__.items() if not k.startswith("_")} for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if page_size > 0 else 0,
    )


@router.put("/products/{product_id}/review")
async def review_product(
    product_id: int,
    data: dict,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """审核产品：approve 或 reject + reason"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    product = db.query(product_models.Product).filter(product_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    action = data.get("action")
    if action == "approve":
        product.status = product_models.ProductStatus.APPROVED
        product.reject_reason = None
    elif action == "reject":
        product.status = product_models.ProductStatus.REJECTED
        product.reject_reason = data.get("reason", "内容不符合要求")
    elif action == "off_shelf":
        product.status = product_models.ProductStatus.OFF_SHELF
    elif action == "on_shelf":
        product.status = product_models.ProductStatus.APPROVED
        product.reject_reason = None
    else:
        raise HTTPException(status_code=400, detail="无效的审核操作")

    db.commit()

    # 发送通知给商户
    if action in ("approve", "reject"):
        merchant = db.query(user_models.User).filter(user_models.User.id == product.merchant_id).first()
        if merchant:
            notif_type = "product_review"
            title = "产品审核结果"
            content = f"您的产品《{product.title}》已{'通过' if action == 'approve' else '驳回'}审核。"
            if action == "reject":
                content += f"\n驳回原因：{product.reject_reason}"
            notif = notification_models.Notification(
                user_id=product.merchant_id,
                type=notif_type,
                title=title,
                content=content,
            )
            db.add(notif)
            db.commit()

    return {"message": "审核成功"}


@router.post("/products", response_model=ProductOut)
async def create_product_admin(
    data: ProductAdminUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """管理员新增产品"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    product = product_models.Product(
        merchant_id=user_id,
        title=data.title or "",
        description=data.description,
        images=data.images or [],
        industry_id=data.industry_id or 0,
        area=data.area or "",
        contact_phone=data.contact_phone,
        status=ProductStatus.APPROVED if not data.status else ProductStatus(data.status),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    industry = db.query(industry_models.Industry).filter_by(id=product.industry_id).first()
    return ProductOut(
        id=product.id,
        title=product.title,
        description=product.description,
        images=product.images or [],
        industry_id=product.industry_id,
        area=product.area,
        contact_phone=product.contact_phone,
        view_count=product.view_count,
        status=product.status.value,
        reject_reason=product.reject_reason,
        merchant_id=product.merchant_id,
        merchant_name="管理员",
        industry_name=industry.name if industry else None,
        created_at=product.created_at,
    )


@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product_admin(
    product_id: int,
    data: ProductAdminUpdate,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """管理员编辑产品"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    product = db.query(product_models.Product).filter(product_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    industry = db.query(industry_models.Industry).filter_by(id=product.industry_id).first()
    return ProductOut(
        id=product.id,
        title=product.title,
        description=product.description,
        images=product.images or [],
        industry_id=product.industry_id,
        area=product.area,
        contact_phone=product.contact_phone,
        view_count=product.view_count,
        status=product.status.value,
        reject_reason=product.reject_reason,
        merchant_id=product.merchant_id,
        merchant_name=product.merchant.nickname if product.merchant else None,
        industry_name=industry.name if industry else None,
        created_at=product.created_at,
    )


@router.delete("/products/{product_id}")
async def delete_product_admin(
    product_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """管理员删除产品"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    product = db.query(product_models.Product).filter(product_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    db.delete(product)
    db.commit()
    return {"message": "删除成功"}


# ── 行业字典 ─────────────────────────────────────────────────────────────────
@router.get("/industries", response_model=list[IndustryOut])
async def list_industries(db: Session = Depends(get_db)):
    return db.query(industry_models.Industry).order_by(industry_models.Industry.id).all()


@router.post("/industries")
async def create_industry(data: dict, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="行业名称不能为空")

    existing = db.query(industry_models.Industry).filter(industry_models.Industry.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="该行业已存在")

    industry = industry_models.Industry(name=name)
    db.add(industry)
    db.commit()
    db.refresh(industry)
    return industry


# ── 广告管理 ─────────────────────────────────────────────────────────────────
@router.get("/ads", response_model=list[AdOut])
async def list_ads_admin(db: Session = Depends(get_db)):
    return db.query(ads_models.Ad).order_by(ads_models.Ad.sort_order.asc()).all()


@router.post("/ads", response_model=AdOut)
async def create_ad(data: dict, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    ad = ads_models.Ad(
        title=data.get("title", ""),
        image=data.get("image", ""),
        link=data.get("link"),
        merchant_id=data.get("merchant_id"),
        sort_order=data.get("sort_order", 0),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        status=ads_models.AdStatus.ACTIVE,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


@router.put("/ads/{ad_id}")
async def update_ad(ad_id: int, data: dict, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    ad = db.query(ads_models.Ad).filter(ads_models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")

    if "title" in data:
        ad.title = data["title"]
    if "image" in data:
        ad.image = data["image"]
    if "link" in data:
        ad.link = data["link"]
    if "sort_order" in data:
        ad.sort_order = data["sort_order"]
    if "status" in data:
        ad.status = data["status"]
    if "start_time" in data:
        ad.start_time = data["start_time"]
    if "end_time" in data:
        ad.end_time = data["end_time"]

    db.commit()
    db.refresh(ad)
    return ad


@router.delete("/ads/{ad_id}")
async def delete_ad(ad_id: int, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    ad = db.query(ads_models.Ad).filter(ads_models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")

    db.delete(ad)
    db.commit()
    return {"message": "删除成功"}


# ── 活动管理 ─────────────────────────────────────────────────────────────────
@router.get("/activities", response_model=PaginatedResponse)
async def list_activities_admin(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    request: Request = None,
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    q = db.query(activity_models.Activity)
    total = q.count()
    items = q.order_by(activity_models.Activity.start_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for a in items:
        count = db.query(activity_models.ActivityRegistration).filter(
            activity_models.ActivityRegistration.activity_id == a.id
        ).count()
        result.append({
            "id": a.id,
            "title": a.title,
            "cover_image": a.cover_image,
            "start_time": a.start_time,
            "end_time": a.end_time,
            "location": a.location,
            "content": a.content,
            "max_participants": a.max_participants,
            "status": a.status.value,
            "registered_count": count,
            "created_at": a.created_at,
        })

    from math import ceil
    return PaginatedResponse(items=result, total=total, page=page, page_size=page_size, total_pages=ceil(total / page_size) if page_size > 0 else 0)


@router.post("/activities", response_model=ActivityOut)
async def create_activity(data: ActivityCreate, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    activity = activity_models.Activity(**data.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.put("/activities/{activity_id}", response_model=ActivityOut)
async def update_activity(activity_id: int, data: ActivityUpdate, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    activity = db.query(activity_models.Activity).filter(activity_models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/activities/{activity_id}")
async def delete_activity(activity_id: int, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    activity = db.query(activity_models.Activity).filter(activity_models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    db.delete(activity)
    db.commit()
    return {"message": "删除成功"}


@router.get("/activities/{activity_id}/registrations")
async def get_activity_registrations(
    activity_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """获取活动报名列表"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    registrations = db.query(activity_models.ActivityRegistration).filter(
        activity_models.ActivityRegistration.activity_id == activity_id
    ).order_by(activity_models.ActivityRegistration.registered_at.desc()).all()

    activity = db.query(activity_models.Activity).filter(activity_models.Activity.id == activity_id).first()
    result = []
    for r in registrations:
        result.append({
            "id": r.id,
            "activity_title": activity.title if activity else "",
            "register_type": r.register_type,
            "name": r.name,
            "phone": r.phone,
            "area": r.area,
            "interest": r.interest,
            "remark": r.remark,
            "registered_at": r.registered_at,
        })
    return result


# ── 用户管理 ─────────────────────────────────────────────────────────────────
@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    db: Session = Depends(get_db),
    role: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    request: Request = None,
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    q = db.query(user_models.User)
    if role:
        q = q.filter(user_models.User.role == role)

    total = q.count()
    items = q.order_by(user_models.User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    from math import ceil
    result = []
    for u in items:
        result.append({
            "id": u.id,
            "role": u.role.value,
            "nickname": u.nickname,
            "avatar_url": u.avatar_url,
            "phone_masked": mask_phone(u.phone) if u.phone else None,
            "is_disabled": u.is_disabled,
            "created_at": u.created_at,
        })

    return PaginatedResponse(items=result, total=total, page=page, page_size=page_size, total_pages=ceil(total / page_size) if page_size > 0 else 0)


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: int, data: dict, request: Request = None, db: Session = Depends(get_db)):
    """修改用户角色"""
    admin_id = get_current_user_id(request)
    if not admin_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(admin_id, db)

    if user_id == admin_id:
        raise HTTPException(status_code=403, detail="不能修改自己的角色")

    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    new_role = data.get("role")
    if new_role not in ("visitor", "user", "merchant", "admin"):
        raise HTTPException(status_code=400, detail="无效的角色")

    old_role = user.role.value
    user.role = new_role
    db.commit()

    # 如果从商户降级为普通用户，同步更新商户申请状态
    if old_role == "merchant" and new_role != "merchant":
        app = db.query(merchant_models.MerchantApplication).filter(
            merchant_models.MerchantApplication.user_id == user_id
        ).first()
        if app and app.status == merchant_models.MerchantStatus.APPROVED:
            app.status = merchant_models.MerchantStatus.REJECTED
            app.reject_reason = "商户权限已被管理员收回"
            db.commit()

    return {"message": f"用户角色已更新为 {new_role}"}


@router.put("/users/{user_id}/disable")
async def toggle_user_disable(user_id: int, data: dict, request: Request = None, db: Session = Depends(get_db)):
    """禁用/启用用户"""
    admin_id = get_current_user_id(request)
    if not admin_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(admin_id, db)

    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_disabled = data.get("is_disabled", not user.is_disabled)
    db.commit()
    return {"message": f"用户已{'禁用' if user.is_disabled else '启用'}"}


# ── 商户入驻审核 ─────────────────────────────────────────────────────────────
@router.get("/merchants", response_model=list[MerchantApplicationOut])
async def list_merchant_applications(db: Session = Depends(get_db), request: Request = None):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(user_id, db)

    apps = db.query(merchant_models.MerchantApplication).order_by(
        merchant_models.MerchantApplication.applied_at.desc()
    ).all()

    result = []
    for app in apps:
        user = db.query(user_models.User).filter(user_models.User.id == app.user_id).first()
        result.append(MerchantApplicationOut(
            id=app.id,
            user_id=app.user_id,
            user_nickname=user.nickname if user else None,
            shop_name=app.shop_name,
            business_license=app.business_license,
            contact_phone=app.contact_phone,
            address=app.address,
            description=app.description,
            area=app.area,
            industry_name=app.industry_name,
            status=app.status.value,
            reject_reason=app.reject_reason,
            applied_at=app.applied_at,
        ))
    return result


@router.put("/merchants/{merchant_id}/review")
async def review_merchant(merchant_id: int, data: dict, request: Request = None, db: Session = Depends(get_db)):
    """审核商户入驻申请"""
    admin_id = get_current_user_id(request)
    if not admin_id:
        raise HTTPException(status_code=401, detail="未登录")
    require_admin(admin_id, db)

    app = db.query(merchant_models.MerchantApplication).filter(merchant_models.MerchantApplication.id == merchant_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="申请不存在")

    action = data.get("action")
    if action == "approve":
        app.status = merchant_models.MerchantStatus.APPROVED
        # 升级用户角色
        user = db.query(user_models.User).filter(user_models.User.id == app.user_id).first()
        if user:
            user.role = user_models.UserRole.MERCHANT
    elif action == "reject":
        app.status = merchant_models.MerchantStatus.REJECTED
        app.reject_reason = data.get("reason", "申请不符合要求")
    else:
        raise HTTPException(status_code=400, detail="无效的审核操作")

    db.commit()

    # 发送通知
    user = db.query(user_models.User).filter(user_models.User.id == app.user_id).first()
    if user:
        title = "商户入驻审核结果"
        content = f"您的商户入驻申请已{'通过' if action == 'approve' else '驳回'}。"
        if action == "reject":
            content += f"\n驳回原因：{app.reject_reason}"
        notif = notification_models.Notification(
            user_id=app.user_id,
            type="merchant_review",
            title=title,
            content=content,
        )
        db.add(notif)
        db.commit()

    return {"message": "审核成功"}


@router.post("/merchants/apply", response_model=MerchantApplicationOut)
async def apply_merchant(data: MerchantApply, request: Request = None, db: Session = Depends(get_db)):
    """会员商户提交入驻申请"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user or user.role == user_models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无权限申请商户入驻")

    existing = db.query(merchant_models.MerchantApplication).filter(
        merchant_models.MerchantApplication.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已有入驻申请，请勿重复提交")

    app = merchant_models.MerchantApplication(
        user_id=user_id,
        shop_name=data.shop_name,
        business_license=data.business_license,
        contact_phone=data.contact_phone,
        address=data.address,
        description=data.description,
        area=data.area,
        industry_name=data.industry_name,
        status=merchant_models.MerchantStatus.PENDING_REVIEW,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("/merchants/my", response_model=MerchantApplicationOut | None)
async def get_my_merchant(request: Request = None, db: Session = Depends(get_db)):
    """获取当前用户的商户申请状态"""
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    app = db.query(merchant_models.MerchantApplication).filter(
        merchant_models.MerchantApplication.user_id == user_id
    ).order_by(merchant_models.MerchantApplication.applied_at.desc()).first()
    if not app:
        return None
    user = db.query(user_models.User).filter(user_models.User.id == app.user_id).first()
    return MerchantApplicationOut(
        id=app.id,
        user_id=app.user_id,
        user_nickname=user.nickname if user else None,
        shop_name=app.shop_name,
        business_license=app.business_license,
        contact_phone=app.contact_phone,
        address=app.address,
        description=app.description,
        area=app.area,
        industry_name=app.industry_name,
        status=app.status.value,
        reject_reason=app.reject_reason,
        applied_at=app.applied_at,
    )


# ── 通知管理 ─────────────────────────────────────────────────────────────────
@router.get("/notifications")
async def list_notifications(
    db: Session = Depends(get_db),
    unread: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    request: Request = None,
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    q = db.query(notification_models.Notification).filter(
        notification_models.Notification.user_id == user_id
    )
    if unread:
        q = q.filter(notification_models.Notification.is_read == False)

    total = q.count()
    items = q.order_by(notification_models.Notification.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    from math import ceil
    return {
        "items": [NotificationOut.model_validate(n).model_dump() for n in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": ceil(total / page_size) if page_size > 0 else 0,
    }


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, request: Request = None, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    notif = db.query(notification_models.Notification).filter(
        notification_models.Notification.id == notification_id,
        notification_models.Notification.user_id == user_id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="通知不存在")

    notif.is_read = True
    db.commit()
    return {"message": "已标记为已读"}


@router.put("/notifications/read-all")
async def mark_all_read(request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录")

    db.query(notification_models.Notification).filter(
        notification_models.Notification.user_id == user_id,
        notification_models.Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "全部已读"}
