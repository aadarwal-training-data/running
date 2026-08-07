"""Minimal HKDF-SHA-256 helpers for the protocol-composition notebook."""

from __future__ import annotations

import hashlib
import hmac

HASH_LEN = hashlib.sha256().digest_size


def hkdf_extract(salt: bytes | None, input_key_material: bytes) -> bytes:
    """HKDF-Extract from RFC 5869 using SHA-256."""
    effective_salt = bytes(HASH_LEN) if salt is None else salt
    return hmac.new(effective_salt, input_key_material, hashlib.sha256).digest()


def hkdf_expand(pseudorandom_key: bytes, info: bytes, length: int) -> bytes:
    """HKDF-Expand from RFC 5869 using SHA-256."""
    if not 0 <= length <= 255 * HASH_LEN:
        raise ValueError("length exceeds HKDF's 255-block limit")
    output = bytearray()
    previous = b""
    counter = 1
    while len(output) < length:
        previous = hmac.new(
            pseudorandom_key,
            previous + info + bytes([counter]),
            hashlib.sha256,
        ).digest()
        output.extend(previous)
        counter += 1
    return bytes(output[:length])


def hkdf(
    input_key_material: bytes,
    *,
    length: int,
    salt: bytes | None = None,
    info: bytes = b"",
) -> bytes:
    return hkdf_expand(hkdf_extract(salt, input_key_material), info, length)


def _length_prefix(value: bytes) -> bytes:
    return len(value).to_bytes(4, "big") + value


def derive_directional_keys(
    shared_secret: bytes,
    alice_public: bytes,
    bob_public: bytes,
    *,
    transcript: bytes = b"",
    context: bytes = b"running/x25519/v1",
) -> tuple[bytes, bytes]:
    """Illustrate transcript-bound derivation of Alice→Bob and Bob→Alice keys."""
    salt = hashlib.sha256(context).digest()
    info = b"".join(
        _length_prefix(value)
        for value in (context, alice_public, bob_public, transcript)
    )
    key_material = hkdf(shared_secret, length=64, salt=salt, info=info)
    return key_material[:32], key_material[32:]
