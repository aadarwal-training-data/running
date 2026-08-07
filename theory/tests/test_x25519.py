from cryptograph_theory.elliptic import TOY_CURVE, TOY_GENERATOR
from cryptograph_theory.x25519 import (
    CURVE25519_A24,
    CURVE25519_P,
    clamp_scalar_bytes,
    decode_scalar25519,
    montgomery_ladder,
    x25519,
    x25519_base,
)


def test_clamping_shape() -> None:
    clamped = clamp_scalar_bytes(bytes([255]) * 32)
    assert clamped[0] == 248
    assert clamped[31] == 127
    scalar = decode_scalar25519(bytes([255]) * 32)
    assert scalar % 8 == 0
    assert scalar.bit_length() == 255


def test_rfc_7748_scalar_multiplication_vectors() -> None:
    cases = [
        (
            "a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4",
            "e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c",
            "c3da55379de9c6908e94ea4df28d084f32eccf03491c71f754b4075577a28552",
        ),
        (
            "4b66e9d4d1b4673c5ad22691957d6af5c11b6421e0ea01d42ca4169e7918ba0d",
            "e5210f12786811d3f4b7959d0538ae2c31dbe7106fc03c3efc4cd549c715a493",
            "95cbde9476e8907d7aade45cb4b873f88b595a68799fa152e6f8f7647aac7957",
        ),
    ]
    for scalar, u_coordinate, expected in cases:
        assert x25519(bytes.fromhex(scalar), bytes.fromhex(u_coordinate)).hex() == expected


def test_rfc_7748_ecdh_vector() -> None:
    alice_secret = bytes.fromhex(
        "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"
    )
    bob_secret = bytes.fromhex(
        "5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb"
    )
    alice_public = x25519_base(alice_secret)
    bob_public = x25519_base(bob_secret)
    assert alice_public.hex() == (
        "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a"
    )
    assert bob_public.hex() == (
        "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"
    )
    shared = x25519(alice_secret, bob_public)
    assert shared == x25519(bob_secret, alice_public)
    assert shared.hex() == (
        "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742"
    )

def test_zero_input_and_one_iteration_vector() -> None:
    input_value = bytes.fromhex("09" + "00" * 31)
    assert x25519(input_value, input_value).hex() == (
        "422c8e7a6227d7bca1350b3e2bb7279f7897b87bb6854b783c60e80311ae3079"
    )
    assert x25519(input_value, bytes(32)) == bytes(32)


def test_toy_ladder_matches_full_point_arithmetic() -> None:
    toy_a24 = (TOY_CURVE.coefficient - 2) * pow(4, -1, TOY_CURVE.prime) % TOY_CURVE.prime
    for scalar in range(18):
        ladder_u, _ = montgomery_ladder(
            scalar,
            TOY_GENERATOR[0],
            prime=TOY_CURVE.prime,
            a24=toy_a24,
        )
        point = TOY_CURVE.scalar_mul(scalar, TOY_GENERATOR)
        assert ladder_u == (0 if point is None else point[0])

    real_output, _ = montgomery_ladder(
        decode_scalar25519(bytes.fromhex("09" + "00" * 31)),
        9,
        prime=CURVE25519_P,
        a24=CURVE25519_A24,
        bits=255,
    )
    assert real_output.to_bytes(32, "little") == x25519(
        bytes.fromhex("09" + "00" * 31), bytes.fromhex("09" + "00" * 31)
    )
