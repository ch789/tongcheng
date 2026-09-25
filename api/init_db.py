"""数据库初始化脚本：建表 + 种子数据"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal
from app.models import users, products, activities, ads, merchants, home
from app.models.users import User, UserRole
from app.models.products import Product
from app.models.industries import Industry
from app.models.home import HomeContent
from app.utils.password import hash_password


def init_db():
    """创建所有表"""
    from app.models import __init__ as models_init  # noqa: F401 - 触发所有模型注册
    from sqlalchemy import inspect
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    print(f"已有表: {existing_tables}")

    # 创建所有表
    users.Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")


def seed_data():
    """插入种子数据"""
    db = SessionLocal()

    try:
        # 1. 创建管理员账号
        admin = db.query(User).filter(User.phone == "admin").first()
        if not admin:
            admin = User(
                phone="admin",
                password_hash=hash_password("admin123"),
                nickname="管理员",
                role=UserRole.ADMIN,
            )
            db.add(admin)
            print("✅ 管理员账号创建: admin / admin123")

        # 2. 创建行业字典
        default_industries = [
            "餐饮美食", "装修建材", "家政服务", "教育培训",
            "法律服务", "医疗健康", "汽车服务", "商贸批发",
            "休闲娱乐", "房产服务", "美容美发", "物流快递",
        ]
        for name in default_industries:
            existing = db.query(Industry).filter(Industry.name == name).first()
            if not existing:
                db.add(Industry(name=name))
        print(f"✅ 行业字典初始化完成（{len(default_industries)}个行业）")

        # 3. 创建默认首页内容
        home_content = db.query(HomeContent).first()
        if not home_content:
            home_content = HomeContent(
                slogan="团结老乡资源，服务在津邯郸人\n找商户、找活动、找同乡服务，一站搞定",
                announcement="天津邯郸人咨询服务平台正式上线！欢迎在津邯郸老乡注册使用。",
            )
            db.add(home_content)
            print("✅ 首页默认内容初始化完成")

        db.commit()
        print("\n🎉 数据库初始化完成！")
        print("\n登录信息：")
        print("  管理员：admin / admin123")
        print("  H5前端：http://localhost:3000")
        print("  管理后台：http://localhost:3001/admin/login")
        print("  API文档：http://localhost:8000/docs")

    except Exception as e:
        db.rollback()
        print(f"❌ 种子数据初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    seed_data()
