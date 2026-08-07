"""Readable, variable-time X25519 reference code based on RFC 7748.

Never use this module for production cryptography.
"""

from __future__ import annotations

from dataclasses import dataclass

CURVE25519_P = 2**255 - 19
CURVE25519_A = 486662
CURVE25519_A24 = 121665  # (A - 2) / 4, matching the RFC 7748 formulas below
CURVE25519_L = 2**252 + 27742317777372353535851937790883648493
CURVE25519_COFACTOR = 8
CURVE25519_BASE_U = 9


@dataclass(frozen=True)
class LadderState:
    """One post-update state of a Montgomery ladder."""

    bit_index: int
    bit: int
    prefix: int
    x2: int
    z2: int
    x3: int
    z3: int


def clamp_scalar_bytes(scalar: bytes) -> bytes:
    """Return the RFC 7748 X25519 scalar-decoding bit pattern."""
    if len(scalar) != 32:
        raise ValueError("an X25519 scalar must contain exactly 32 bytes")
    decoded = bytearray(scalar)
    decoded[0] &= 248
    decoded[31] &= 127
    decoded[31] |= 64
    return bytes(decoded)


def decode_scalar25519(scalar: bytes) -> int:
    return int.from_bytes(clamp_scalar_bytes(scalar), "little")


def decode_u25519(encoded_u: bytes) -> int:
    """Decode an X25519 input coordinate, including the required high-bit mask."""
    if len(encoded_u) != 32:
        raise ValueError("an X25519 u-coordinate must contain exactly 32 bytes")
    decoded = bytearray(encoded_u)
    decoded[31] &= 127
    return int.from_bytes(decoded, "little") % CURVE25519_P


def _conditional_swap(swap: int, left: int, right: int) -> tuple[int, int]:
    """Educational conditional swap; Python does not make this constant-time."""
    return (right, left) if swap else (left, right)


def projective_u(x: int, z: int, prime: int) -> int | None:
    """Convert ``X:Z`` to affine ``u``, or ``None`` for the identity."""
    if z % prime == 0:
        return None
    return x * pow(z, prime - 2, prime) % prime


def montgomery_ladder(
    scalar: int,
    u: int,
    *,
    prime: int,
    a24: int,
    bits: int | None = None,
    capture_trace: bool = False,
) -> tuple[int, list[LadderState]]:
    """Return the affine u-coordinate of ``[scalar]P`` and an optional trace."""
    if scalar < 0:
        raise ValueError("scalar must be nonnegative")
    bit_count = bits if bits is not None else max(1, scalar.bit_length())
    x1 = u % prime
    x2, z2 = 1, 0
    x3, z3 = x1, 1
    swap = 0
    prefix = 0
    trace: list[LadderState] = []

    for bit_index in range(bit_count - 1, -1, -1):
        bit = (scalar >> bit_index) & 1
        swap ^= bit
        x2, x3 = _conditional_swap(swap, x2, x3)
        z2, z3 = _conditional_swap(swap, z2, z3)
        swap = bit

        a = (x2 + z2) % prime
        aa = a * a % prime
        b = (x2 - z2) % prime
        bb = b * b % prime
        e = (aa - bb) % prime
        c = (x3 + z3) % prime
        d = (x3 - z3) % prime
        da = d * a % prime
        cb = c * b % prime
        x3 = (da + cb) ** 2 % prime
        z3 = x1 * (da - cb) ** 2 % prime
        x2 = aa * bb % prime
        z2 = e * (aa + a24 * e) % prime

        prefix = (prefix << 1) | bit
        if capture_trace:
            trace.append(LadderState(bit_index, bit, prefix, x2, z2, x3, z3))

    x2, x3 = _conditional_swap(swap, x2, x3)
    z2, z3 = _conditional_swap(swap, z2, z3)
    affine = projective_u(x2, z2, prime)
    return (0 if affine is None else affine), trace


def x25519(scalar: bytes, encoded_u: bytes) -> bytes:
    """Evaluate X25519 as specified in RFC 7748."""
    decoded_scalar = decode_scalar25519(scalar)
    decoded_u = decode_u25519(encoded_u)
    result, _ = montgomery_ladder(
        decoded_scalar,
        decoded_u,
        prime=CURVE25519_P,
        a24=CURVE25519_A24,
        bits=255,
    )
    return result.to_bytes(32, "little")


def x25519_base(scalar: bytes) -> bytes:
    return x25519(scalar, CURVE25519_BASE_U.to_bytes(32, "little"))
