"""图片压缩工具：将大图压缩至目标尺寸，保持宽高比，输出为 JPEG"""
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image


# 目标最大边长（px）；超出此尺寸时自动压缩
TARGET_MAX_SIDE = 1600
# 压缩后的 JPEG 质量（1–100）
JPEG_QUALITY = 85


def compress_image(
    file_bytes: bytes,
    max_bytes: Optional[int] = None,
) -> Tuple[bytes, str]:
    """
    对 PNG/GIF/WEBP 等大图进行压缩，返回 (压缩后 bytes, content_type)。

    - 若图片原始尺寸未超过 TARGET_MAX_SIDE，仍按 JPEG_QUALITY 重新编码以减小体积。
    - max_bytes 为目标上限（字节）；达到后不再二次压缩。
    - 若图片极小或已满足要求，直接原样返回。
    """
    try:
        img = Image.open(BytesIO(file_bytes))
    except Exception:
        # 无法解析为图片，原样返回
        return file_bytes, "application/octet-stream"

    original_size = len(file_bytes)

    # 判断是否需要压缩
    needs_resize = img.width > TARGET_MAX_SIDE or img.height > TARGET_MAX_SIDE
    should_compress = max_bytes is None or original_size > max_bytes

    if not needs_resize and not should_compress:
        # 原图已满足要求，直接返回
        ct = _image_content_type(img)
        return file_bytes, ct

    # 处理动图：只取第一帧
    if img.format == "GIF" and getattr(img, "n_frames", 1) > 1:
        img.seek(0)

    # 转换为 RGB（去除透明通道，兼容 JPEG）
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # 按比例缩放
    if needs_resize:
        ratio = TARGET_MAX_SIDE / max(img.width, img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    compressed = buf.getvalue()

    # 二次压缩：若仍超过 max_bytes，降低质量重压缩
    if max_bytes and len(compressed) > max_bytes:
        quality = max(10, JPEG_QUALITY - int((len(compressed) - max_bytes) / (original_size / 100)))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        compressed = buf.getvalue()

    return compressed, "image/jpeg"


def _image_content_type(img: Image.Image) -> str:
    fmt = (img.format or "JPEG").upper()
    mapping = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "GIF": "image/gif",
        "WEBP": "image/webp",
        "BMP": "image/bmp",
    }
    return mapping.get(fmt, "image/jpeg")
