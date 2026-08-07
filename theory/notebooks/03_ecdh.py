import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import hashlib

    import marimo as mo
    import matplotlib.pyplot as plt

    from cryptograph_theory.elliptic import TOY_CURVE, TOY_GENERATOR
    from cryptograph_theory.hkdf import derive_directional_keys

    return TOY_CURVE, TOY_GENERATOR, derive_directional_keys, hashlib, mo, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3 · ECDH, active attackers, and key derivation

    The group identity

    \[
      [a]([b]G)=[ab]G=[b]([a]G)
    \]

    gives unauthenticated key agreement. It does not tell Alice whose public
    point she received. Toggle the attacker to see the exact gap between
    passive secrecy and an authenticated protocol.
    """)
    return


@app.cell
def _(mo):
    protocol_mode = mo.ui.dropdown(
        options=["direct exchange", "active man-in-the-middle"],
        value="direct exchange",
        label="network",
    )
    protocol_alice = mo.ui.slider(1, 16, value=5, label="Alice $a$", show_value=True)
    protocol_bob = mo.ui.slider(1, 16, value=9, label="Bob $b$", show_value=True)
    protocol_mallory_alice = mo.ui.slider(
        1, 16, value=7, label="Mallory→Alice $m_A$", show_value=True
    )
    protocol_mallory_bob = mo.ui.slider(
        1, 16, value=3, label="Mallory→Bob $m_B$", show_value=True
    )
    protocol_transcript = mo.ui.text(
        value="client=alice; server=bob; suite=toy-v1",
        label="transcript / context",
        full_width=True,
    )
    mo.vstack(
        [
            mo.hstack(
                [
                    protocol_mode,
                    protocol_alice,
                    protocol_bob,
                    protocol_mallory_alice,
                    protocol_mallory_bob,
                ],
                widths="equal",
                gap=1,
            ),
            protocol_transcript,
        ]
    )
    return (
        protocol_alice,
        protocol_bob,
        protocol_mallory_alice,
        protocol_mallory_bob,
        protocol_mode,
        protocol_transcript,
    )


@app.cell
def _(
    TOY_CURVE,
    TOY_GENERATOR,
    protocol_alice,
    protocol_bob,
    protocol_mallory_alice,
    protocol_mallory_bob,
    protocol_mode,
):
    protocol_alice_public = TOY_CURVE.scalar_mul(protocol_alice.value, TOY_GENERATOR)
    protocol_bob_public = TOY_CURVE.scalar_mul(protocol_bob.value, TOY_GENERATOR)
    protocol_under_attack = protocol_mode.value == "active man-in-the-middle"

    if protocol_under_attack:
        protocol_to_alice = TOY_CURVE.scalar_mul(
            protocol_mallory_alice.value, TOY_GENERATOR
        )
        protocol_to_bob = TOY_CURVE.scalar_mul(protocol_mallory_bob.value, TOY_GENERATOR)
    else:
        protocol_to_alice = protocol_bob_public
        protocol_to_bob = protocol_alice_public

    protocol_alice_shared = TOY_CURVE.scalar_mul(protocol_alice.value, protocol_to_alice)
    protocol_bob_shared = TOY_CURVE.scalar_mul(protocol_bob.value, protocol_to_bob)
    return (
        protocol_alice_public,
        protocol_alice_shared,
        protocol_bob_public,
        protocol_bob_shared,
        protocol_to_alice,
        protocol_to_bob,
        protocol_under_attack,
    )


@app.cell
def _(
    TOY_CURVE,
    protocol_alice_public,
    protocol_alice_shared,
    protocol_bob_public,
    protocol_bob_shared,
    protocol_mallory_alice,
    protocol_mallory_bob,
    protocol_under_attack,
):
    if protocol_under_attack:
        protocol_mallory_with_alice = TOY_CURVE.scalar_mul(
            protocol_mallory_alice.value, protocol_alice_public
        )
        protocol_mallory_with_bob = TOY_CURVE.scalar_mul(
            protocol_mallory_bob.value, protocol_bob_public
        )
        assert protocol_mallory_with_alice == protocol_alice_shared
        assert protocol_mallory_with_bob == protocol_bob_shared
    else:
        protocol_mallory_with_alice = None
        protocol_mallory_with_bob = None
    return protocol_mallory_with_alice, protocol_mallory_with_bob


@app.cell
def _(
    mo,
    protocol_alice_public,
    protocol_alice_shared,
    protocol_bob_public,
    protocol_bob_shared,
    protocol_mallory_with_alice,
    protocol_mallory_with_bob,
    protocol_to_alice,
    protocol_to_bob,
    protocol_under_attack,
):
    _match = protocol_alice_shared == protocol_bob_shared
    _attacker_detail = (
        rf"""
        Mallory independently matches Alice at `{protocol_mallory_with_alice}`
        and Bob at `{protocol_mallory_with_bob}`. Alice and Bob do **not**
        share a secret.
        """
        if protocol_under_attack
        else "The public values were delivered without substitution."
    )
    mo.md(rf"""
    ## Public exchange and resulting secrets

    | | Alice's side | Bob's side |
    |---|---:|---:|
    | honest public point | `{protocol_alice_public}` | `{protocol_bob_public}` |
    | received point | `{protocol_to_alice}` | `{protocol_to_bob}` |
    | computed secret | `{protocol_alice_shared}` | `{protocol_bob_shared}` |

    Alice and Bob match: **{_match}**.

    {_attacker_detail}
    """)
    return


@app.cell
def _(mo, plt, protocol_alice_shared, protocol_bob_shared, protocol_under_attack):
    protocol_figure, _axis = plt.subplots(figsize=(8.0, 2.6))
    _axis.set_xlim(-0.5, 2.5)
    _axis.set_ylim(-0.7, 0.8)
    _axis.axis("off")
    _box = {"boxstyle": "round,pad=0.5", "facecolor": "#f8fafc", "edgecolor": "#94a3b8"}
    _axis.text(0, 0, "Alice", ha="center", va="center", bbox=_box)
    _axis.text(2, 0, "Bob", ha="center", va="center", bbox=_box)
    if protocol_under_attack:
        _mallory_box = dict(_box)
        _mallory_box.update({"facecolor": "#fff7ed", "edgecolor": "#f59e0b"})
        _axis.text(1, 0, "Mallory", ha="center", va="center", bbox=_mallory_box)
        _axis.annotate("", xy=(0.2, 0), xytext=(0.8, 0), arrowprops={"arrowstyle": "<->"})
        _axis.annotate("", xy=(1.2, 0), xytext=(1.8, 0), arrowprops={"arrowstyle": "<->"})
        _axis.text(0.5, 0.28, f"secret {protocol_alice_shared}", ha="center", color="#c2410c")
        _axis.text(1.5, 0.28, f"secret {protocol_bob_shared}", ha="center", color="#c2410c")
        _axis.text(1, -0.48, "two authenticated endpoints are missing", ha="center")
    else:
        _axis.annotate("", xy=(0.2, 0), xytext=(1.8, 0), arrowprops={"arrowstyle": "<->"})
        _axis.text(
            1,
            0.28,
            f"matching secret {protocol_alice_shared}",
            ha="center",
            color="#15803d",
        )
    protocol_figure.tight_layout()
    mo.output.replace(protocol_figure)
    return


@app.cell
def _(
    derive_directional_keys,
    hashlib,
    mo,
    protocol_alice_public,
    protocol_alice_shared,
    protocol_bob_public,
    protocol_bob_shared,
    protocol_transcript,
):
    def _encode_point(point):
        if point is None:
            return bytes(4)
        return point[0].to_bytes(2, "big") + point[1].to_bytes(2, "big")

    _alice_material = hashlib.sha256(_encode_point(protocol_alice_shared)).digest()
    _bob_material = hashlib.sha256(_encode_point(protocol_bob_shared)).digest()
    _alice_public_bytes = _encode_point(protocol_alice_public)
    _bob_public_bytes = _encode_point(protocol_bob_public)
    _transcript = protocol_transcript.value.encode()
    protocol_alice_keys = derive_directional_keys(
        _alice_material,
        _alice_public_bytes,
        _bob_public_bytes,
        transcript=_transcript,
        context=b"cryptograph/theory/toy-ecdh/v1",
    )
    protocol_bob_keys = derive_directional_keys(
        _bob_material,
        _alice_public_bytes,
        _bob_public_bytes,
        transcript=_transcript,
        context=b"cryptograph/theory/toy-ecdh/v1",
    )
    mo.md(rf"""
    ## Transcript-bound directional keys

    | Derived key | Alice's view | Bob's view |
    |---|---|---|
    | Alice→Bob | `{protocol_alice_keys[0].hex()[:20]}…` | `{protocol_bob_keys[0].hex()[:20]}…` |
    | Bob→Alice | `{protocol_alice_keys[1].hex()[:20]}…` | `{protocol_bob_keys[1].hex()[:20]}…` |

    Views match: **{protocol_alice_keys == protocol_bob_keys}**. The two
    directions differ: **{protocol_alice_keys[0] != protocol_alice_keys[1]}**.

    Change the transcript field: the key prefixes change even if the group
    point does not. Real protocols bind ordered public keys, roles, suite
    identifiers, and the complete transcript rather than inventing this toy
    encoding.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Primitive boundaries

    | Component | What it supplies |
    |---|---|
    | scalar multiplication | one-way group action |
    | X25519 | unauthenticated shared-secret computation |
    | HKDF | context-bound key derivation |
    | signature / certificate / PSK | peer authentication |
    | AEAD | message confidentiality and integrity |
    | TLS / Noise / HPKE | reviewed protocol composition |

    Ephemeral authenticated keys can provide forward secrecy. X25519 alone
    does not provide identity, freshness, erasure, or post-quantum security.
    """)
    return


if __name__ == "__main__":
    app.run()
