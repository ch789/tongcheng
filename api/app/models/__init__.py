"""所有模型一次导入，确保 SQLAlchemy 自动发现并注册"""
from app.models.users import User, UserRole
from app.models.products import Product, ProductStatus
from app.models.industries import Industry
from app.models.activities import Activity, ActivityStatus, ActivityRegistration
from app.models.ads import Ad, AdStatus
from app.models.merchants import MerchantApplication, MerchantStatus
from app.models.home import HomeContent
from app.models.notifications import Notification

__all__ = [
    "User", "UserRole",
    "Product", "ProductStatus",
    "Industry",
    "Activity", "ActivityStatus", "ActivityRegistration",
    "Ad", "AdStatus",
    "MerchantApplication", "MerchantStatus",
    "HomeContent",
    "Notification",
]
