from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import activities as activity_models, users as user_models, notifications as notification_models
from app.schemas import ActivityOut, ActivityDetail, RegistrationCreate, RegistrationOut, PaginatedResponse
from app.utils.jwt_utils import decode_access_token

router = APIRouter(prefix="/activities", tags=["活动"])


def _get_user_id(request) -> Optional[int]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header[7:])
        if payload and "user_id" in payload:
            return payload["user_id"]
    return None


# ── 公开接口 ─────────────────────────────────────────────────────────────────
@router.get("", response_model=PaginatedResponse)
async def list_activities(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    """活动列表"""
    q = db.query(activity_models.Activity)

    if status:
        q = q.filter(activity_models.Activity.status == status)
    else:
        # 默认只看未下架的
        q = q.filter(activity_models.Activity.status != activity_models.ActivityStatus.OFF_SHELF)

    total = q.count()
    result = []
    activities = q.order_by(activity_models.Activity.start_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    for a in activities:
        cnt = db.query(func.count(activity_models.ActivityRegistration.id)).filter(
            activity_models.ActivityRegistration.activity_id == a.id
        ).scalar() or 0
        result.append(ActivityOut(
            id=a.id,
            title=a.title,
            cover_image=a.cover_image,
            start_time=a.start_time,
            end_time=a.end_time,
            location=a.location,
            content=a.content,
            max_participants=a.max_participants,
            status=a.status.value,
            registered_count=cnt,
            created_at=a.created_at,
        ))

    from math import ceil
    return PaginatedResponse(
        items=[i.model_dump() for i in result],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if page_size > 0 else 0,
    )


@router.get("/my-registrations", response_model=list[RegistrationOut])
async def my_registrations(request: Request = None, db: Session = Depends(get_db)):
    """我的报名记录"""
    user_id = _get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    registrations = db.query(activity_models.ActivityRegistration).filter(
        activity_models.ActivityRegistration.user_id == user_id
    ).order_by(activity_models.ActivityRegistration.registered_at.desc()).all()

    result = []
    for r in registrations:
        activity = db.query(activity_models.Activity).filter(activity_models.Activity.id == r.activity_id).first()
        result.append(RegistrationOut(
            id=r.id,
            activity_title=activity.title if activity else "未知活动",
            activity_cover=activity.cover_image if activity else None,
            activity_start_time=activity.start_time if activity else r.registered_at,
            activity_end_time=activity.end_time if activity else r.registered_at,
            activity_location=activity.location if activity else None,
            register_type=r.register_type,
            name=r.name,
            phone=r.phone,
            area=r.area,
            interest=r.interest,
            remark=r.remark,
            registered_at=r.registered_at,
        ))
    return result


@router.get("/{activity_id}", response_model=ActivityDetail)
async def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """活动详情"""
    activity = db.query(activity_models.Activity).filter(
        activity_models.Activity.id == activity_id
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    count = db.query(activity_models.ActivityRegistration).filter(
        activity_models.ActivityRegistration.activity_id == activity_id
    ).count()

    return ActivityDetail(
        id=activity.id,
        title=activity.title,
        cover_image=activity.cover_image,
        start_time=activity.start_time,
        end_time=activity.end_time,
        location=activity.location,
        content=activity.content,
        max_participants=activity.max_participants,
        status=activity.status.value,
        registered_count=count,
        created_at=activity.created_at,
    )


# ── 报名接口 ─────────────────────────────────────────────────────────────────
@router.post("/{activity_id}/register", response_model=RegistrationOut)
async def register_activity(
    activity_id: int,
    data: RegistrationCreate,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """报名活动"""
    activity = db.query(activity_models.Activity).filter(
        activity_models.Activity.id == activity_id
    ).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    if activity.status not in (activity_models.ActivityStatus.REGISTERING, activity_models.ActivityStatus.UPCOMING):
        raise HTTPException(status_code=400, detail="当前无法报名")

    # 检查人数限制（使用行级锁防止竞态）
    if activity.max_participants > 0:
        db.execute(
            text("SELECT 1 FROM activities WHERE id = :id FOR UPDATE"),
            {"id": activity_id},
        )
        db.commit()
        count = db.query(activity_models.ActivityRegistration).filter(
            activity_models.ActivityRegistration.activity_id == activity_id
        ).count()
        if count >= activity.max_participants:
            raise HTTPException(status_code=400, detail="名额已满")

    user_id = _get_user_id(request)

    registration = activity_models.ActivityRegistration(
        activity_id=activity_id,
        user_id=user_id,
        **data.model_dump(),
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)

    # 发送通知给商户（如果活动有商户关联，此处简化）
    # 创建通知：报名成功
    notification = notification_models.Notification(
        user_id=user_id or 0,  # 游客无用户ID，通知为空
        type="activity_registered",
        title="报名成功",
        content=f"您已成功报名《{activity.title}》",
    )
    db.add(notification)
    db.commit()

    return RegistrationOut(
        id=registration.id,
        activity_title=activity.title,
        activity_cover=activity.cover_image,
        activity_start_time=activity.start_time,
        activity_end_time=activity.end_time,
        activity_location=activity.location,
        register_type=registration.register_type,
        name=registration.name,
        phone=registration.phone,
        area=registration.area,
        interest=registration.interest,
        remark=registration.remark,
        registered_at=registration.registered_at,
    )
