from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ── 用户相关 ─────────────────────────────────────────────────────────────────
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserOut(BaseModel):
    id: int
    role: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone_masked: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


# ── 产品相关 ─────────────────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    images: list[str] = []
    industry_id: int
    area: str = Field(..., min_length=1, max_length=64)
    contact_phone: Optional[str] = None


class ProductUpdate(ProductCreate):
    pass


class ProductAdminUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    images: Optional[list[str]] = None
    industry_id: Optional[int] = None
    area: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None
    reject_reason: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    images: list[str] = []
    industry_id: int
    area: str
    contact_phone: Optional[str] = None
    view_count: int
    status: str
    reject_reason: Optional[str] = None
    merchant_id: int
    merchant_name: Optional[str] = None
    industry_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetail(ProductOut):
    industry_name: Optional[str] = None
    merchant_name: Optional[str] = None


# ── 行业 ─────────────────────────────────────────────────────────────────────
class IndustryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ── 活动相关 ─────────────────────────────────────────────────────────────────
class ActivityCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    cover_image: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    content: Optional[str] = None
    max_participants: int = 0


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    content: Optional[str] = None
    max_participants: Optional[int] = None
    status: Optional[str] = None


class ActivityOut(BaseModel):
    id: int
    title: str
    cover_image: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    content: Optional[str] = None
    max_participants: int
    status: str
    registered_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityDetail(ActivityOut):
    registered_count: int


class RegistrationCreate(BaseModel):
    register_type: str = Field(..., pattern="^(personal|merchant)$")
    name: str = Field(..., min_length=1, max_length=64)
    phone: str = Field(..., min_length=7, max_length=20)
    area: str = Field(..., min_length=1, max_length=64)
    interest: Optional[str] = None
    remark: Optional[str] = None


class RegistrationOut(BaseModel):
    id: int
    activity_title: str
    activity_cover: Optional[str] = None
    activity_start_time: datetime
    activity_end_time: datetime
    activity_location: Optional[str] = None
    register_type: str
    name: str
    phone: str
    area: str
    interest: Optional[str] = None
    remark: Optional[str] = None
    registered_at: datetime

    class Config:
        from_attributes = True


# ── 广告相关 ─────────────────────────────────────────────────────────────────
class AdCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    image: str
    link: Optional[str] = None
    merchant_id: Optional[int] = None
    sort_order: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AdOut(BaseModel):
    id: int
    title: str
    image: str
    link: Optional[str] = None
    merchant_id: Optional[int] = None
    merchant_name: Optional[str] = None
    sort_order: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── 首页内容 ─────────────────────────────────────────────────────────────────
class HomeContentUpdate(BaseModel):
    slogan: Optional[str] = None
    announcement: Optional[str] = None


class HomeContentOut(BaseModel):
    slogan: Optional[str] = None
    announcement: Optional[str] = None
    ads: list[dict] = []
    updated_at: Optional[datetime] = None


# ── 商户入驻 ─────────────────────────────────────────────────────────────────
class MerchantApply(BaseModel):
    shop_name: str = Field(..., min_length=1, max_length=128)
    business_license: Optional[str] = None
    contact_phone: str = Field(..., min_length=7, max_length=20)
    address: Optional[str] = None
    description: Optional[str] = None
    area: Optional[str] = None
    industry_name: Optional[str] = None


class MerchantApplicationOut(BaseModel):
    id: int
    user_id: int
    user_nickname: Optional[str] = None
    shop_name: str
    business_license: Optional[str] = None
    contact_phone: str
    address: Optional[str] = None
    description: Optional[str] = None
    area: Optional[str] = None
    industry_name: Optional[str] = None
    status: str
    reject_reason: Optional[str] = None
    applied_at: datetime

    class Config:
        from_attributes = True


# ── 通知 ─────────────────────────────────────────────────────────────────────
class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    content: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── 通用分页 ─────────────────────────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: list[dict]
    total: int
    page: int
    page_size: int
    total_pages: int
