import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    from cryptograph_theory.elliptic import TOY_CURVE, TOY_GENERATOR
    from cryptograph_theory.x25519 import (
        CURVE25519_A,
        CURVE25519_A24,
        CURVE25519_L,
        CURVE25519_P,
        clamp_scalar_bytes,
        decode_scalar25519,
        montgomery_ladder,
        projective_u,
        x25519,
        x25519_base,
    )

    return (
        CURVE25519_A,
        CURVE25519_A24,
        CURVE25519_L,
        CURVE25519_P,
        Rectangle,
        TOY_CURVE,
        TOY_GENERATOR,
        clamp_scalar_bytes,
        decode_scalar25519,
        math,
        mo,
        montgomery_ladder,
        plt,
        projective_u,
        x25519,
        x25519_base,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4 · Curve25519, clamping, and the Montgomery ladder

    Curve25519 is

    \[
      v^2=u^3+486662u^2+u
      \quad\text{over}\quad
      \mathbb F_{2^{255}-19}.
    \]

    Its base coordinate is $u=9$, its prime subgroup has order
    $\ell\approx2^{252}$, and the full curve order is $8\ell$. X25519 is the
    32-byte function that performs standardized x-only scalar multiplication
    on this curve and its quadratic twist.
    """)
    return


@app.cell
def _(mo):
    ladder_scalar = mo.ui.slider(1, 16, value=13, label="toy scalar $k$", show_value=True)
    x25519_vector = mo.ui.dropdown(
        options={
            "RFC Alice secret": (
                "77076d0a7318a57d3c16c17251b26645"
                "df4c2f87ebc0992ab177fba51db92c2a"
            ),
            "RFC Bob secret": (
                "5dab087e624a8a4b79e17f8b83800ee6"
                "6f3bb1292618b6fd1c2f8b27ff88e0eb"
            ),
            "RFC one-iteration input": "09" + "00" * 31,
        },
        value="RFC Alice secret",
        label="real 32-byte scalar",
    )
    mo.hstack([ladder_scalar, x25519_vector], widths="equal", gap=2)
    return ladder_scalar, x25519_vector


@app.cell
def _(TOY_CURVE, TOY_GENERATOR, ladder_scalar, montgomery_ladder):
    ladder_a24 = (
        (TOY_CURVE.coefficient - 2)
        * pow(4, -1, TOY_CURVE.prime)
        % TOY_CURVE.prime
    )
    ladder_output, ladder_trace = montgomery_ladder(
        ladder_scalar.value,
        TOY_GENERATOR[0],
        prime=TOY_CURVE.prime,
        a24=ladder_a24,
        capture_trace=True,
    )
    ladder_full_point = TOY_CURVE.scalar_mul(ladder_scalar.value, TOY_GENERATOR)
    assert ladder_output == ladder_full_point[0]
    return ladder_a24, ladder_full_point, ladder_output, ladder_trace


@app.cell
def _(ladder_trace, mo):
    ladder_step = mo.ui.slider(
        0,
        len(ladder_trace) - 1,
        value=len(ladder_trace) - 1,
        label="processed-bit step",
        show_value=True,
    )
    mo.output.replace(ladder_step)
    return (ladder_step,)


@app.cell
def _(
    TOY_CURVE,
    TOY_GENERATOR,
    ladder_output,
    ladder_scalar,
    ladder_step,
    ladder_trace,
    mo,
    projective_u,
):
    ladder_state = ladder_trace[ladder_step.value]
    if ladder_state.bit:
        _x0, _z0 = ladder_state.x3, ladder_state.z3
        _x1, _z1 = ladder_state.x2, ladder_state.z2
    else:
        _x0, _z0 = ladder_state.x2, ladder_state.z2
        _x1, _z1 = ladder_state.x3, ladder_state.z3
    ladder_r0_u = projective_u(_x0, _z0, TOY_CURVE.prime)
    ladder_r1_u = projective_u(_x1, _z1, TOY_CURVE.prime)
    _expected_r0 = TOY_CURVE.scalar_mul(ladder_state.prefix, TOY_GENERATOR)
    _expected_r1 = TOY_CURVE.scalar_mul(ladder_state.prefix + 1, TOY_GENERATOR)
    assert ladder_r0_u == (None if _expected_r0 is None else _expected_r0[0])
    assert ladder_r1_u == (None if _expected_r1 is None else _expected_r1[0])

    mo.md(rf"""
    ## A ladder small enough to inspect

    $k={ladder_scalar.value}={ladder_scalar.value:b}_2$. After processing bit
    index `{ladder_state.bit_index}` with value `{ladder_state.bit}`, the prefix
    is $r={ladder_state.prefix}$ and the invariant is

    \[
      R_0=[r]P\quad(u={ladder_r0_u}),
      \qquad
      R_1=[r+1]P\quad(u={ladder_r1_u}).
    \]

    The final toy output is $u([k]P)={ladder_output}$. Only $u$ is carried;
    $P$ and $-P$ deliberately have the same representation.
    """)
    return ladder_r0_u, ladder_r1_u, ladder_state


@app.cell
def _(ladder_r0_u, ladder_r1_u, ladder_state, math, mo, plt):
    _order = 17
    _angles = [2 * math.pi * scalar / _order for scalar in range(_order)]
    _xs = [math.sin(angle) for angle in _angles]
    _ys = [math.cos(angle) for angle in _angles]
    ladder_figure, _axis = plt.subplots(figsize=(6.5, 4.3))
    _axis.scatter(_xs, _ys, color="#94a3b8", s=38)
    for _scalar, (_x, _y) in enumerate(zip(_xs, _ys, strict=True)):
        _axis.text(_x * 1.16, _y * 1.16, str(_scalar), ha="center", va="center")
    _r0 = ladder_state.prefix % _order
    _r1 = (ladder_state.prefix + 1) % _order
    _axis.scatter([_xs[_r0]], [_ys[_r0]], s=170, color="#3b82f6", label=f"R₀ · u={ladder_r0_u}")
    _axis.scatter(
        [_xs[_r1]],
        [_ys[_r1]],
        s=170,
        color="#f59e0b",
        marker="s",
        label=f"R₁ · u={ladder_r1_u}",
    )
    _axis.set_title("The ladder maintains adjacent subgroup multiples")
    _axis.set_aspect("equal")
    _axis.axis("off")
    _axis.legend(frameon=False, loc="center left", bbox_to_anchor=(1, 0.5))
    ladder_figure.tight_layout()
    mo.output.replace(ladder_figure)
    return


@app.cell
def _(clamp_scalar_bytes, decode_scalar25519, x25519_base, x25519_vector):
    x25519_raw_scalar = bytes.fromhex(x25519_vector.value)
    x25519_clamped_scalar = clamp_scalar_bytes(x25519_raw_scalar)
    x25519_scalar_integer = decode_scalar25519(x25519_raw_scalar)
    x25519_public = x25519_base(x25519_raw_scalar)
    _expected = {
        "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a": (
            "8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a"
        ),
        "5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb": (
            "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f"
        ),
        "09" + "00" * 31: (
            "422c8e7a6227d7bca1350b3e2bb7279f7897b87bb6854b783c60e80311ae3079"
        ),
    }
    assert x25519_public.hex() == _expected[x25519_vector.value]
    return (
        x25519_clamped_scalar,
        x25519_public,
        x25519_raw_scalar,
        x25519_scalar_integer,
    )


@app.cell
def _(
    Rectangle,
    mo,
    plt,
    x25519_clamped_scalar,
    x25519_raw_scalar,
):
    def _bit_matrix(data):
        return [[(byte >> bit) & 1 for byte in data] for bit in range(7, -1, -1)]

    x25519_bits_figure, _axes = plt.subplots(2, 1, figsize=(9.0, 3.8), sharex=True)
    for _axis, _data, _title in zip(
        _axes,
        (x25519_raw_scalar, x25519_clamped_scalar),
        ("input bytes", "decoded scalar after clamping"),
        strict=True,
    ):
        _axis.imshow(_bit_matrix(_data), cmap="Greys", vmin=0, vmax=1, aspect="auto")
        _axis.set_yticks(range(8), labels=range(7, -1, -1))
        _axis.set_ylabel("bit in byte")
        _axis.set_title(_title, loc="left")
        for _byte, _bit in ((0, 0), (0, 1), (0, 2), (31, 7), (31, 6)):
            _row = 7 - _bit
            _axis.add_patch(
                Rectangle(
                    (_byte - 0.5, _row - 0.5),
                    1,
                    1,
                    fill=False,
                    edgecolor="#f59e0b",
                    linewidth=2,
                )
            )
    _axes[-1].set_xticks(range(0, 32, 2))
    _axes[-1].set_xlabel("little-endian byte index")
    x25519_bits_figure.tight_layout()
    mo.output.replace(x25519_bits_figure)
    return


@app.cell
def _(
    mo,
    x25519_clamped_scalar,
    x25519_public,
    x25519_raw_scalar,
    x25519_scalar_integer,
):
    mo.md(rf"""
    ## Real X25519 decoding

    | | first byte | final byte |
    |---|---:|---:|
    | input | `{x25519_raw_scalar[0]:02x}` | `{x25519_raw_scalar[31]:02x}` |
    | clamped | `{x25519_clamped_scalar[0]:02x}` | `{x25519_clamped_scalar[31]:02x}` |

    The decoded scalar is

    ```text
    {x25519_scalar_integer}
    ```

    It is divisible by 8, bit 254 is set, and bit 255 is clear. The verified
    RFC public output is

    ```text
    {x25519_public.hex()}
    ```

    Clamping is not reduction modulo $\ell$, does not create entropy, and does
    not make peer keys authenticated.
    """)
    return


@app.cell
def _(mo, x25519, x25519_base):
    _alice_secret = bytes.fromhex(
        "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"
    )
    _bob_secret = bytes.fromhex(
        "5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb"
    )
    _alice_public = x25519_base(_alice_secret)
    _bob_public = x25519_base(_bob_secret)
    _alice_shared = x25519(_alice_secret, _bob_public)
    _bob_shared = x25519(_bob_secret, _alice_public)
    assert _alice_shared == _bob_shared
    assert _alice_shared.hex() == (
        "4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742"
    )
    mo.md(rf"""
    ## RFC 7748 Diffie–Hellman vector

    \[
      \operatorname{{X25519}}(a,B)
      =\operatorname{{X25519}}(b,A).
    \]

    Both sides produce `{_alice_shared.hex()}`.

    This is still raw, unauthenticated DH material: a real protocol handles an
    all-zero result, authenticates the peer, and binds both public keys, roles,
    suite, and transcript into a KDF.
    """)
    return


@app.cell(hide_code=True)
def _(
    CURVE25519_A,
    CURVE25519_A24,
    CURVE25519_L,
    CURVE25519_P,
    ladder_a24,
    mo,
):
    mo.accordion(
        {
            "Exact parameter sheet": mo.md(rf"""
            \[
            p=2^{{255}}-19={CURVE25519_P},
            \qquad A={CURVE25519_A},
            \]

            \[
            \ell={CURVE25519_L},
            \qquad \#E(\mathbb F_p)=8\ell,
            \qquad u(G)=9.
            \]

            The RFC ladder uses $a_{{24}}=(A-2)/4={CURVE25519_A24}$.
            The toy curve uses $a_{{24}}={ladder_a24}$ in $\mathbb F_{{127}}$.
            """),
            "Ladder formulas": mo.md(r"""
            For projective $u=X/Z$, one step computes

            \[
            A_0=X_2+Z_2,\ AA=A_0^2,\quad
            B_0=X_2-Z_2,\ BB=B_0^2,\quad E=AA-BB,
            \]

            \[
            C_0=X_3+Z_3,\quad D_0=X_3-Z_3,\quad
            DA=D_0A_0,\quad CB=C_0B_0,
            \]

            \[
            X_3'=(DA+CB)^2,\quad Z_3'=u_1(DA-CB)^2,
            \]

            \[
            X_2'=AA\,BB,\quad Z_2'=E(AA+a_{24}E).
            \]

            Conditional swaps make each secret bit use the same field-operation
            pattern. Pure Python is nevertheless variable-time.
            """),
            "x-only DLP relation": mo.md(r"""
            In the odd prime-order subgroup,

            \[
              u([a]G)=u([b]G)
              \iff b\equiv\pm a\pmod\ell.
            \]

            Recovering the scalar up to sign is enough to compute every shared
            x-coordinate, because $u(P)=u(-P)$. This connects X25519 public
            values to ECDLP without claiming that ECDLP and CDH are equivalent.
            """),
            "Cofactor and twist": mo.md(r"""
            A received $u$ may describe a point on Curve25519 or on its
            quadratic twist. The curve has cofactor 8; the twist has cofactor
            4 and a large prime component. The ladder intentionally operates on
            both. Small-order inputs can still produce the all-zero output.
            """),
        }
    )
    return


if __name__ == "__main__":
    app.run()
