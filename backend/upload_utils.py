"""
Validación compartida para las fotos que se suben en tickets, quejas y
partes de avería del portal del vecino.
"""

import os

from fastapi import HTTPException, UploadFile

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
TAMANIO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB


def validar_imagen(foto: UploadFile) -> None:
    """
    Lanza HTTPException(400) si la imagen no tiene una extensión permitida
    o supera el tamaño máximo. No hace nada si foto es None/vacío (el
    campo es opcional en todos los formularios que la usan).
    """
    if not foto or not foto.filename:
        return
    ext = os.path.splitext(foto.filename)[1].lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(400, "Formato de imagen no válido.")
    if foto.size is not None and foto.size > TAMANIO_MAXIMO_BYTES:
        raise HTTPException(
            400,
            f"La imagen supera el tamaño máximo permitido"
            f"({TAMANIO_MAXIMO_BYTES // (1024 * 1024)} MB).",
        )
