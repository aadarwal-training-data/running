import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt

    from cryptograph_theory.elliptic import TOY_CURVE, TOY_GENERATOR

    return TOY_CURVE, TOY_GENERATOR, math, mo, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2 · Elliptic-curve groups and ECDLP

    This notebook uses the tiny Montgomery curve

    \[
      E/\mathbb F_{127}:\quad v^2=u^3+5u^2+u.
    \]

    It has $136=8\cdot17$ points. The base point $G=(18,55)$ has prime
    order $17$. The example mirrors Curve25519's cofactor-times-prime shape,
    but it is intentionally breakable.
    """)
    return


@app.cell
def _(mo):
    ec_alice = mo.ui.slider(1, 16, value=5, label="Alice's $a$", show_value=True)
    ec_bob = mo.ui.slider(1, 16, value=9, label="Bob's $b$", show_value=True)
    ec_show_all = mo.ui.switch(value=True, label="show all finite curve points")
    ec_clear_point = mo.ui.dropdown(
        options={
            "order 2 · (0, 0)": (0, 0),
            "order 4 · (10, 42)": (10, 42),
            "order 68 · (5, 1)": (5, 1),
        },
        value="order 68 · (5, 1)",
        label="point for cofactor clearing",
    )
    mo.hstack([ec_alice, ec_bob, ec_show_all, ec_clear_point], widths="equal", gap=1)
    return ec_alice, ec_bob, ec_clear_point, ec_show_all


@app.cell
def _(TOY_CURVE, TOY_GENERATOR, ec_alice, ec_bob, mo):
    ec_alice_public = TOY_CURVE.scalar_mul(ec_alice.value, TOY_GENERATOR)
    ec_bob_public = TOY_CURVE.scalar_mul(ec_bob.value, TOY_GENERATOR)
    ec_shared_left = TOY_CURVE.scalar_mul(ec_alice.value, ec_bob_public)
    ec_shared_right = TOY_CURVE.scalar_mul(ec_bob.value, ec_alice_public)
    ec_shared_scalar = ec_alice.value * ec_bob.value % 17
    mo.md(rf"""
    ## Toy ECDH

    \[
      A=[{ec_alice.value}]G={ec_alice_public},\qquad
      B=[{ec_bob.value}]G={ec_bob_public}.
    \]

    \[
      [{ec_alice.value}]B
      =[{ec_bob.value}]A
      =[{ec_shared_scalar}]G
      ={ec_shared_left}.
    \]

    Both calculations match: **{ec_shared_left == ec_shared_right}**.
    """)
    return ec_alice_public, ec_bob_public, ec_shared_left, ec_shared_scalar


@app.cell
def _(
    TOY_CURVE,
    TOY_GENERATOR,
    ec_alice_public,
    ec_bob_public,
    ec_shared_left,
    ec_show_all,
    mo,
    plt,
):
    _finite = [point for point in TOY_CURVE.points() if point is not None]
    _subgroup = [point for point in TOY_CURVE.multiples(TOY_GENERATOR) if point is not None]
    ec_curve_figure, _axis = plt.subplots(figsize=(7.6, 4.8))
    if ec_show_all.value:
        _axis.scatter(
            [point[0] for point in _finite],
            [point[1] for point in _finite],
            s=14,
            color="#94a3b8",
            alpha=0.45,
            label="all finite points",
        )
    _axis.scatter(
        [point[0] for point in _subgroup],
        [point[1] for point in _subgroup],
        s=55,
        facecolors="none",
        edgecolors="#334155",
        label=r"prime-order subgroup $\langle G\rangle$",
    )
    _selected = [
        (TOY_GENERATOR, "G", "#334155", "o", (8, 10)),
        (ec_alice_public, "A", "#3b82f6", "o", (-20, 16)),
        (ec_bob_public, "B", "#f59e0b", "s", (-20, -22)),
        (ec_shared_left, "S", "#22c55e", "D", (9, 10)),
    ]
    for _point, _label, _color, _marker, _offset in _selected:
        _axis.scatter(
            [_point[0]], [_point[1]], s=115, color=_color, marker=_marker,
            edgecolors="white", linewidths=0.8, zorder=4
        )
        _axis.annotate(
            _label,
            xy=_point,
            xytext=_offset,
            textcoords="offset points",
            color=_color,
            weight="bold",
        )
    _axis.set_xlim(-3, 130)
    _axis.set_ylim(-3, 130)
    _axis.set_xlabel("$u$")
    _axis.set_ylabel("$v$")
    _axis.set_title("A finite-field curve is a discrete point cloud")
    _axis.grid(alpha=0.15)
    _axis.legend(frameon=False, loc="upper center", ncol=2)
    ec_curve_figure.tight_layout()
    mo.output.replace(ec_curve_figure)
    return


@app.cell
def _(ec_alice, ec_bob, ec_shared_scalar, math, mo, plt):
    _order = 17
    _angles = [2 * math.pi * scalar / _order for scalar in range(_order)]
    _xs = [math.sin(angle) for angle in _angles]
    _ys = [math.cos(angle) for angle in _angles]
    ec_subgroup_figure, _axis = plt.subplots(figsize=(6.5, 4.3))
    _axis.scatter(_xs, _ys, color="#94a3b8", s=42)
    for _scalar, (_x, _y) in enumerate(zip(_xs, _ys, strict=True)):
        _axis.text(_x * 1.16, _y * 1.16, f"{_scalar}G", ha="center", va="center")
    _marks = [
        (ec_alice.value, "A", "#3b82f6", "o"),
        (ec_bob.value, "B", "#f59e0b", "s"),
        (ec_shared_scalar, "S", "#22c55e", "D"),
    ]
    for _scalar, _label, _color, _marker in _marks:
        _axis.scatter(
            [_xs[_scalar]], [_ys[_scalar]], s=150, color=_color,
            marker=_marker, label=_label, zorder=3
        )
    _axis.set_title("Scalar multiplication walks around a cyclic subgroup")
    _axis.set_aspect("equal")
    _axis.axis("off")
    _axis.legend(frameon=False, loc="center left", bbox_to_anchor=(1, 0.5))
    ec_subgroup_figure.tight_layout()
    mo.output.replace(ec_subgroup_figure)
    return


@app.cell
def _(TOY_CURVE, ec_clear_point, mo):
    ec_selected_point = ec_clear_point.value
    ec_selected_order = TOY_CURVE.point_order(ec_selected_point)
    ec_cleared_point = TOY_CURVE.scalar_mul(8, ec_selected_point)
    ec_cleared_order = TOY_CURVE.point_order(ec_cleared_point)
    mo.md(rf"""
    ## Cofactor clearing

    The selected point $P={ec_selected_point}$ has order
    ${ec_selected_order}$. Multiplying by the cofactor gives

    \[
      [8]P={ec_cleared_point},
      \qquad
      \operatorname{{ord}}([8]P)={ec_cleared_order}.
    \]

    A small-order point may collapse to the identity; a point with a prime
    component lands in the order-17 subgroup. This is why clamping helps with
    cofactor components but does not authenticate a peer or make all-zero
    results impossible.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "The affine Montgomery group law": mo.md(r"""
            For distinct noninverse points $P=(u_1,v_1)$ and $Q=(u_2,v_2)$:

            \[
            \lambda=(v_2-v_1)(u_2-u_1)^{-1},
            \quad
            u_3=\lambda^2-A-u_1-u_2,
            \quad
            v_3=\lambda(u_1-u_3)-v_1.
            \]

            For doubling,
            $\lambda=(3u_1^2+2Au_1+1)(2v_1)^{-1}$. All arithmetic is
            modulo $p$. The point at infinity is the identity and
            $(u,v)+(u,-v)=\mathcal O$.
            """),
            "ECDLP": mo.md(r"""
            In the subgroup $\langle G\rangle$ of order $17$, the ECDLP is

            \[
              (G,Q=[x]G)\longmapsto x\pmod{17}.
            \]

            This is the ordinary discrete logarithm problem written with the
            additive elliptic-curve operation.
            """),
        }
    )
    return


if __name__ == "__main__":
    app.run()
