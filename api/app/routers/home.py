from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import users as user_models, ads as ads_models, home as home_models
from app.schemas import HomeContentOut, AdOut
from app.utils.jwt_utils import decode_access_token

router = APIRouter(prefix="/home", tags=["首页"])


def _get_user_id(request) -> Optional[int]:
    """从请求头获取当前用户 ID（可选，首页大部分内容不需要登录）"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header[7:])
        if payload and "user_id" in payload:
            return payload["user_id"]
    return None


@router.get("", response_model=HomeContentOut)
async def get_home(db: Session = Depends(get_db), request=None):
    """获取首页内容：Slogan、公告、轮播广告"""
    # 首页内容
    home = db.query(home_models.HomeContent).first()
    slogan = home.slogan if home else None
    announcement = home.announcement if home else None
    updated_at = home.updated_at if home else None

    # 活跃广告（按排序取前5个）
    ads = (
        db.query(ads_models.Ad)
        .filter(ads_models.Ad.status == ads_models.AdStatus.ACTIVE)
        .order_by(ads_models.Ad.sort_order.asc())
        .limit(5)
        .all()
    )
    ads_data = []
    for ad in ads:
        ads_data.append({
            "id": ad.id,
            "title": ad.title,
            "image": ad.image,
            "link": ad.link,
            "sort_order": ad.sort_order,
        })

    return HomeContentOut(
        slogan=slogan,
        announcement=announcement,
        ads=ads_data,
        updated_at=updated_at,
    )
