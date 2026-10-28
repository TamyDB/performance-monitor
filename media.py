"""Authenticated media envelope; an embedded key is not a secret from extraction."""
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b'PCDIAG1\0'


def encrypt(data: bytes, key: bytes) -> bytes:
    nonce = os.urandom(12)
    return MAGIC + nonce + AESGCM(key).encrypt(nonce, data, MAGIC)


def decrypt(payload: bytes, key: bytes) -> bytes:
    if len(payload) < len(MAGIC) + 28 or not payload.startswith(MAGIC):
        raise ValueError('Recurso de vídeo inválido')
    offset = len(MAGIC)
    return AESGCM(key).decrypt(payload[offset:offset + 12], payload[offset + 12:], MAGIC)
