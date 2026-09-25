import os
from datetime import datetime, timedelta
from typing import Optional

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7天

# 微信
WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")
WECHAT_TOKEN_URL = "https://api.weixin.qq.com/sns/jscode2session"

# 短信（预留）
SMS_CONFIG = {
    "provider": os.getenv("SMS_PROVIDER", "alibaba"),
    "access_key_id": os.getenv("SMS_ACCESS_KEY_ID", ""),
    "access_key_secret": os.getenv("SMS_ACCESS_KEY_SECRET", ""),
    "sign_name": os.getenv("SMS_SIGN_NAME", "同城老乡服务平台"),
    "template_code": os.getenv("SMS_TEMPLATE_CODE", "SMS_xxxxxxxx"),
}

# 文件上传
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# 基础URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
