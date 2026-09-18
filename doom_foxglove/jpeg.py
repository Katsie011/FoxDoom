"""Encode a 320x200 RGB framebuffer as JPEG bytes for foxglove.CompressedImage."""

from __future__ import annotations

import io

import numpy as np
from PIL import Image

from doom_foxglove import SCREEN_HEIGHT, SCREEN_WIDTH


def encode_jpeg(rgb: np.ndarray, *, quality: int = 70) -> bytes:
    if rgb.ndim == 3 and rgb.shape[0] in (3, 4) and rgb.shape[-1] not in (3, 4):
        rgb = np.transpose(rgb, (1, 2, 0))
    if rgb.dtype != np.uint8:
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    if rgb.ndim == 2:
        image = Image.fromarray(rgb, mode="L").convert("RGB")
    else:
        if rgb.shape[2] == 4:
            rgb = rgb[:, :, :3]
        image = Image.fromarray(rgb, mode="RGB")
    if image.size != (SCREEN_WIDTH, SCREEN_HEIGHT):
        image = image.resize((SCREEN_WIDTH, SCREEN_HEIGHT), Image.BILINEAR)
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()
