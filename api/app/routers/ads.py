from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import ads as ads_models
from app.models.users import User, UserRole
from app.schemas import AdOut
from app.utils.jwt_utils import decode_access_token

router = APIRouter(prefix="/ads", tags=["广告"])


def _get_user_id(request) -> Optional[int]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header[7:])
        if payload and "user_id" in payload:
            return payload["user_id"]
    return None


@router.get("", response_model=list[AdOut])
async def list_ads(
    db: Session = Depends(get_db),
    status: str = Query(default="active"),
):
    """广告列表（商户申请列表或公开列表）"""
    q = db.query(ads_models.Ad)
    if status:
        q = q.filter(ads_models.Ad.status == status)
    ads = q.order_by(ads_models.Ad.sort_order.asc()).all()

    result = []
    for ad in ads:
        result.append(AdOut(
            id=ad.id,
            title=ad.title,
            image=ad.image,
            link=ad.link,
            merchant_id=ad.merchant_id,
            merchant_name=ad.merchant.nickname if ad.merchant else None,
            sort_order=ad.sort_order,
            start_time=ad.start_time,
            end_time=ad.end_time,
            status=ad.status.value,
            created_at=ad.created_at,
        ))
    return result


@router.post("/apply", response_model=AdOut)
async def apply_ad(data: dict, request: Request = None, db: Session = Depends(get_db)):
    """会员商户提交广告申请"""
    user_id = _get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role not in (UserRole.MERCHANT, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="只有会员商户可以申请广告")

    ad = ads_models.Ad(
        title=data.get("title", ""),
        image=data.get("image", ""),
        link=data.get("link"),
        merchant_id=user_id,
        sort_order=data.get("sort_order", 0),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        status=ads_models.AdStatus.PENDING_REVIEW,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)

    return AdOut(
        id=ad.id,
        title=ad.title,
        image=ad.image,
        link=ad.link,
        merchant_id=ad.merchant_id,
        merchant_name=user.nickname,
        sort_order=ad.sort_order,
        start_time=ad.start_time,
        end_time=ad.end_time,
        status=ad.status.value,
        created_at=ad.created_at,
    )
