from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File as FastapiFile
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.database import get_db
from app.models import products as product_models, users as user_models, activities as activity_models, industries as industry_models
from app.schemas import (
    ProductCreate, ProductOut, ProductDetail,
    IndustryOut, PaginatedResponse,
)
from app.utils.jwt_utils import decode_access_token
from app.utils.file_utils import upload_file

router = APIRouter(prefix="/products", tags=["产品"])


def _get_user_id(request) -> Optional[int]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header[7:])
        if payload and "user_id" in payload:
            return payload["user_id"]
    return None


# ── 公开接口 ─────────────────────────────────────────────────────────────────
@router.get("/industries", response_model=list[IndustryOut])
async def list_industries(db: Session = Depends(get_db)):
    """获取行业列表"""
    industries = db.query(industry_models.Industry).order_by(industry_models.Industry.id).all()
    return industries


@router.get("", response_model=PaginatedResponse)
async def list_products(
    db: Session = Depends(get_db),
    keyword: str = Query(default=""),
    industry_id: Optional[int] = Query(default=None),
    area: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
):
    """产品列表（支持关键词、行业、区域筛选）"""
    q = db.query(product_models.Product).filter(
        product_models.Product.status == product_models.ProductStatus.APPROVED
    )

    if keyword:
        q = q.filter(
            or_(
                product_models.Product.title.ilike(f"%{keyword}%"),
                product_models.Product.description.ilike(f"%{keyword}%"),
            )
        )
    if industry_id:
        q = q.filter(product_models.Product.industry_id == industry_id)
    if area:
        q = q.filter(product_models.Product.area == area)

    total = q.count()
    items = q.order_by(product_models.Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for p in items:
        result.append(ProductOut(
            id=p.id,
            title=p.title,
            description=p.description,
            images=p.images or [],
            industry_id=p.industry_id,
            area=p.area,
            contact_phone=p.contact_phone,
            view_count=p.view_count,
            status=p.status.value,
            reject_reason=p.reject_reason,
            merchant_id=p.merchant_id,
            merchant_name=p.merchant.nickname if p.merchant else None,
            industry_name=p.industry.name if p.industry else None,
            created_at=p.created_at,
        ))

    from math import ceil
    return PaginatedResponse(
        items=[i.model_dump() for i in result],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if page_size > 0 else 0,
    )


@router.get("/my", response_model=list[ProductOut])
async def my_products(request: Request = None, db: Session = Depends(get_db)):
    """我的产品列表"""
    user_id = _get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    products = db.query(product_models.Product).filter(
        product_models.Product.merchant_id == user_id
    ).order_by(product_models.Product.created_at.desc()).all()

    result = []
    for p in products:
        industry = db.query(industry_models.Industry).filter_by(id=p.industry_id).first()
        result.append(ProductOut(
            id=p.id,
            title=p.title,
            description=p.description,
            images=p.images or [],
            industry_id=p.industry_id,
            area=p.area,
            contact_phone=p.contact_phone,
            view_count=p.view_count,
            status=p.status.value,
            reject_reason=p.reject_reason,
            merchant_id=p.merchant_id,
            merchant_name=p.merchant.nickname if p.merchant else None,
            industry_name=industry.name if industry else None,
            created_at=p.created_at,
        ))
    return result


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """产品详情，自动 +1 浏览量"""
    product = db.query(product_models.Product).filter(
        product_models.Product.id == product_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    if product.status != product_models.ProductStatus.APPROVED:
        raise HTTPException(status_code=403, detail="该产品暂未公开")

    # 浏览量 +1
    product.view_count += 1
    db.commit()

    return ProductDetail(
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
        industry_name=product.industry.name if product.industry else None,
        created_at=product.created_at,
    )


# ── 商户接口（需登录） ───────────────────────────────────────────────────────
@router.post("", response_model=ProductOut)
async def create_product(
    data: ProductCreate,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """商户发布产品（待审核）"""
    user_id = _get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if user.role not in (user_models.UserRole.MERCHANT, user_models.UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="只有会员商户可以发布产品")

    product = product_models.Product(
        merchant_id=user_id,
        **data.model_dump(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)

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
        merchant_name=user.nickname,
        industry_name=db.query(industry_models.Industry).filter_by(id=product.industry_id).first().name if db.query(industry_models.Industry).filter_by(id=product.industry_id).first() else None,
        created_at=product.created_at,
    )


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    data: ProductCreate,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """编辑产品（仅作者本人或管理员）"""
    user_id = _get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    product = db.query(product_models.Product).filter(product_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    if product.merchant_id != user_id:
        raise HTTPException(status_code=403, detail="无权编辑该产品")

    # 重置为待审核
    product.status = product_models.ProductStatus.PENDING_REVIEW
    product.title = data.title
    product.description = data.description
    product.industry_id = data.industry_id
    product.area = data.area
    product.contact_phone = data.contact_phone
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


@router.delete("/{product_id}")
async def delete_product(product_id: int, request: Request = None, db: Session = Depends(get_db)):
    """删除产品"""
    user_id = _get_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")

    product = db.query(product_models.Product).filter(product_models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    if product.merchant_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除该产品")

    db.delete(product)
    db.commit()
    return {"message": "删除成功"}
