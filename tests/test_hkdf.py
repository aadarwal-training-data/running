from running.hkdf import derive_directional_keys, hkdf_expand, hkdf_extract


def test_rfc_5869_sha256_case_1() -> None:
    input_key_material = bytes.fromhex("0b" * 22)
    salt = bytes.fromhex("000102030405060708090a0b0c")
    info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
    pseudorandom_key = hkdf_extract(salt, input_key_material)
    assert pseudorandom_key.hex() == (
        "077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5"
    )
    assert hkdf_expand(pseudorandom_key, info, 42).hex() == (
        "3cb25f25faacd57a90434f64d0362f2a"
        "2d2d0a90cf1a5a4c5db02d56ecc4c5bf"
        "34007208d5b887185865"
    )


def test_direction_and_transcript_separation() -> None:
    shared = bytes.fromhex("42" * 32)
    alice_public = bytes.fromhex("a1" * 32)
    bob_public = bytes.fromhex("b2" * 32)
    alice_to_bob, bob_to_alice = derive_directional_keys(
        shared,
        alice_public,
        bob_public,
        transcript=b"handshake one",
    )
    changed, _ = derive_directional_keys(
        shared,
        alice_public,
        bob_public,
        transcript=b"handshake two",
    )
    assert alice_to_bob != bob_to_alice
    assert alice_to_bob != changed
