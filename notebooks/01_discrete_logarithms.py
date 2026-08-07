import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt

    from running.finite import discrete_log_bruteforce, discrete_log_bsgs

    return discrete_log_bsgs, discrete_log_bruteforce, math, mo, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1 · The discrete logarithm problem

    For a cyclic group $\mathcal G=\langle g\rangle$ of order $r$, forward
    evaluation maps an exponent to a group element:

    \[
      x\longmapsto g^x.
    \]

    The **DLP** reverses that map: given $g$ and $h$, find
    $x\in\mathbb Z/r\mathbb Z$ with $h=g^x$. Elliptic curves use the same
    problem in additive notation: $Q=[x]G$.
    """)
    return


@app.cell
def _(mo):
    dlp_secret = mo.ui.slider(0, 27, value=19, label="hidden exponent $x$", show_value=True)
    dlp_algorithm = mo.ui.dropdown(
        options=["brute force", "baby-step–giant-step"],
        value="baby-step–giant-step",
        label="attack",
    )
    mo.hstack([dlp_secret, dlp_algorithm], widths="equal", gap=2)
    return dlp_algorithm, dlp_secret


@app.cell
def _(
    discrete_log_bsgs,
    discrete_log_bruteforce,
    dlp_algorithm,
    dlp_secret,
    math,
    mo,
):
    dlp_prime = 29
    dlp_generator = 2
    dlp_order = 28
    dlp_target = pow(dlp_generator, dlp_secret.value, dlp_prime)

    if dlp_algorithm.value == "brute force":
        dlp_solution = discrete_log_bruteforce(
            dlp_generator, dlp_target, dlp_prime, dlp_order
        )
        dlp_work = dlp_solution + 1 if dlp_solution is not None else dlp_order
        _method_note = "one candidate exponent per multiplication"
    else:
        dlp_solution = discrete_log_bsgs(
            dlp_generator, dlp_target, dlp_prime, dlp_order
        )
        _width = math.ceil(math.sqrt(dlp_order))
        dlp_work = 2 * _width
        _method_note = rf"two tables of width about $\lceil\sqrt{{28}}\rceil={_width}$"

    mo.md(rf"""
    ## A tiny instance

    \[
      2^x\equiv {dlp_target}\pmod{{29}}
      \quad\Longrightarrow\quad
      x={dlp_solution}\pmod{{28}}.
    \]

    The selected method uses roughly **{dlp_work} group operations** here:
    {_method_note}. Forward square-and-multiply needs only a number of
    operations proportional to the bit length of $x$.
    """)
    return dlp_generator, dlp_order, dlp_prime, dlp_solution, dlp_target


@app.cell
def _(dlp_order, dlp_secret, math, mo, plt):
    _angles = [2 * math.pi * exponent / dlp_order for exponent in range(dlp_order)]
    _xs = [math.sin(angle) for angle in _angles]
    _ys = [math.cos(angle) for angle in _angles]
    dlp_orbit_figure, _axis = plt.subplots(figsize=(6.6, 4.6))
    _axis.scatter(_xs, _ys, color="#94a3b8", s=40)
    _chosen = dlp_secret.value
    _axis.scatter([_xs[_chosen]], [_ys[_chosen]], color="#f59e0b", s=170, zorder=3)
    for _exponent, (_x, _y) in enumerate(zip(_xs, _ys, strict=True)):
        if _exponent % 2 == 0 or _exponent == _chosen:
            _axis.text(_x * 1.14, _y * 1.14, str(_exponent), ha="center", va="center")
    _axis.annotate(
        "hidden exponent",
        xy=(_xs[_chosen], _ys[_chosen]),
        xytext=(1.25, 0.75),
        arrowprops={"arrowstyle": "->", "color": "#f59e0b"},
    )
    _axis.set_title("The exponent labels are hidden from the DLP solver")
    _axis.set_aspect("equal")
    _axis.axis("off")
    dlp_orbit_figure.tight_layout()
    mo.output.replace(dlp_orbit_figure)
    return


@app.cell
def _(math, mo, plt):
    _bit_sizes = list(range(8, 257, 8))
    _forward = [math.log2(bits) for bits in _bit_sizes]
    _generic = [bits / 2 for bits in _bit_sizes]
    _brute = list(_bit_sizes)
    dlp_complexity_figure, _axis = plt.subplots(figsize=(7.4, 4.2))
    _axis.plot(_bit_sizes, _forward, label="forward scalar multiplication", linewidth=2)
    _axis.plot(_bit_sizes, _generic, label="BSGS / Pollard rho", linewidth=2)
    _axis.plot(_bit_sizes, _brute, label="exhaustive search", linewidth=2)
    _axis.axvline(252, color="#64748b", linestyle="--", linewidth=1)
    _axis.annotate(
        r"Curve25519 subgroup: $\ell\approx2^{252}$" "\n" r"generic work $\approx2^{126}$",
        xy=(252, 126),
        xytext=(130, 165),
        arrowprops={"arrowstyle": "->", "color": "#64748b"},
    )
    _axis.set_xlabel(r"subgroup size $\log_2 r$ (bits)")
    _axis.set_ylabel(r"$\log_2$ group operations")
    _axis.set_xlim(0, 265)
    _axis.set_ylim(0, 265)
    _axis.grid(alpha=0.2)
    _axis.legend(frameon=False, loc="upper left")
    dlp_complexity_figure.tight_layout()
    mo.vstack(
        [
            mo.md("## Forward versus reverse work"),
            dlp_complexity_figure,
            mo.md(r"""
            The square-root line is why a subgroup near $2^{252}$ targets
            roughly 126–128 bits of classical security—not 252 or 255 bits.
            """),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "DLP, CDH, and DDH": mo.md(r"""
            Given $g,g^a,g^b$:

            - **DLP** recovers an exponent such as $a$.
            - **CDH** computes $g^{ab}$.
            - **DDH** decides whether a supplied $T$ equals $g^{ab}$.

            Solver implications run

            \[
              \mathsf{DLP}\Longrightarrow\mathsf{CDH}
              \Longrightarrow\mathsf{DDH},
            \]

            but the problems are not known to be equivalent in arbitrary
            groups. Recovering $a$ certainly breaks CDH; CDH hardness is still
            a distinct assumption.
            """),
            "Representation matters": mo.md(r"""
            Multiplicative finite-field DLP admits index-calculus-style
            algorithms that beat generic square-root attacks. No analogous
            general attack is known for well-chosen elliptic curves. Equal
            field bit lengths therefore do not imply equal security.
            """),
        }
    )
    return


if __name__ == "__main__":
    app.run()
