import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE
from app.utils.compress_image import compress_image


async def upload_file(file: UploadFile, sub_dir: str = "") -> str:
    """上传图片到本地，返回相对路径"""
    subdir = sub_dir or "default"
    dest_dir = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(dest_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WEBP 格式")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过5MB")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(dest_dir, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return f"/uploads/{subdir}/{filename}"


async def upload_file_compressed(file: UploadFile, sub_dir: str = "") -> Tuple[str, bool]:
    """
    上传图片：若超过 MAX_UPLOAD_SIZE 则先压缩再保存。
    返回 (相对路径, 是否经过压缩)。
    """
    subdir = sub_dir or "default"
    dest_dir = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(dest_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WEBP 格式")

    file_bytes = await file.read()
    was_compressed = False

    if len(file_bytes) > MAX_UPLOAD_SIZE:
        compressed_bytes, _ = compress_image(file_bytes, max_bytes=MAX_UPLOAD_SIZE)
        if len(compressed_bytes) > MAX_UPLOAD_SIZE:
            # 压缩后仍然超限，抛出明确错误
            raise HTTPException(
                status_code=400,
                detail=f"图片过大且无法压缩至 5MB 以内，请更换更小的图片",
            )
        file_bytes = compressed_bytes
        was_compressed = True

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(dest_dir, filename)
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return f"/uploads/{subdir}/{filename}", was_compressed


def mask_phone(phone: str) -> str:
    """手机号脱敏：138****1234"""
    if not phone or len(phone) < 7:
        return phone or ""
    return phone[:3] + "****" + phone[-4:]
