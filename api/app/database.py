import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/handanzh"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """启动时自动建表 + 幂等播种（容器每次启动自愈）"""
    from app.models import __init__ as models_pkg  # noqa: F401 - 触发全模型注册（含 home/industries/notifications）
    Base.metadata.create_all(bind=engine)
    seed_if_empty()


def seed_if_empty():
    """幂等种子：仅当缺失时插入，重启不重复插、不报错。逻辑与 init_db.py:seed_data 保持一致。"""
    from app.models import users, industries, home  # noqa: F401 - 确保相关表已注册
    from app.models.users import User, UserRole
    from app.models.industries import Industry
    from app.models.home import HomeContent
    from app.utils.password import hash_password

    db = SessionLocal()
    try:
        # 1) 管理员账号（以 phone="admin" 作为幂等判据）
        if not db.query(User).filter(User.phone == "admin").first():
            db.add(User(
                phone="admin",
                password_hash=hash_password("admin123"),
                nickname="管理员",
                role=UserRole.ADMIN,
            ))

        # 2) 行业字典
        default_industries = [
            "餐饮美食", "装修建材", "家政服务", "教育培训",
            "法律服务", "医疗健康", "汽车服务", "商贸批发",
            "休闲娱乐", "房产服务", "美容美发", "物流快递",
        ]
        for name in default_industries:
            if not db.query(Industry).filter(Industry.name == name).first():
                db.add(Industry(name=name))

        # 3) 首页默认内容
        if not db.query(HomeContent).first():
            db.add(HomeContent(
                slogan="团结同乡资源，服务在外老乡\n找商户、找活动、找同乡服务，一站搞定",
                announcement="同城老乡服务平台正式上线！欢迎在外的老乡注册使用。",
            ))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
