import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt

    from cryptograph_theory.finite import discrete_log_bruteforce, discrete_log_bsgs

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
def _(mo):
    complexity_bits = mo.ui.slider(
        8,
        512,
        step=4,
        value=252,
        label=r"group-order bit length $n=\lceil\log_2 r\rceil$",
        show_value=True,
    )
    return (complexity_bits,)


@app.cell
def _(complexity_bits, math, mo, plt):
    _n = complexity_bits.value
    _bit_sizes = list(range(8, 513, 4))

    # The vertical axis is logarithmic: y=k means approximately 2^k operations.
    _forward = [math.log2(2 * bits) for bits in _bit_sizes]
    _generic = [bits / 2 for bits in _bit_sizes]
    _brute = list(_bit_sizes)

    dlp_complexity_figure, _axis = plt.subplots(figsize=(7.6, 4.4))
    _axis.plot(
        _bit_sizes,
        _forward,
        label=r"forward: square-and-multiply $O(n)$",
        linewidth=2.4,
    )
    _axis.plot(
        _bit_sizes,
        _generic,
        label=r"generic reverse: Pollard rho $O(2^{n/2})$",
        linewidth=2.4,
    )
    _axis.plot(
        _bit_sizes,
        _brute,
        label=r"naive reverse: brute force $O(2^n)$",
        linewidth=2.4,
    )
    _axis.axvline(_n, color="#f59e0b", linestyle="--", linewidth=1.5)
    _axis.scatter(
        [_n, _n, _n],
        [math.log2(2 * _n), _n / 2, _n],
        color="#f59e0b",
        edgecolor="white",
        linewidth=0.8,
        s=42,
        zorder=3,
    )
    _axis.axvline(252, color="#64748b", linestyle=":", linewidth=1)
    _axis.text(
        252,
        0.97,
        r" Curve25519 $\ell\approx2^{252}$",
        rotation=90,
        va="top",
        ha="right",
        color="#64748b",
        transform=_axis.get_xaxis_transform(),
    )
    _axis.set_title("Polynomial forward work versus exponential reverse work")
    _axis.set_xlabel(r"input scale $n=\lceil\log_2 r\rceil$ (bits)")
    _axis.set_ylabel(r"work exponent $k$ in about $2^k$ group operations")
    _axis.set_xlim(0, 520)
    _axis.set_ylim(0, 520)
    _axis.grid(alpha=0.2)
    _axis.legend(frameon=False, loc="upper left")
    dlp_complexity_figure.tight_layout()

    _forward_bound = 2 * _n
    _generic_exponent = _n / 2
    _generic_label = f"{_generic_exponent:g}"
    mo.vstack(
        [
            mo.md("## The computational asymmetry"),
            complexity_bits,
            dlp_complexity_figure,
            mo.md(rf"""
            At $n={_n}$, square-and-multiply takes at most about
            $2n={_forward_bound}$ group operations. A generic classical DLP
            attack instead takes about $2^{{{_generic_label}}}$ operations with
            Pollard rho, while naive search takes about $2^{{{_n}}}$.

            This is the cryptographic gap: **polynomial work** for the honest
            direction, but **exponential work** for the best generic classical
            reverse attack. At Curve25519's $n\approx252$, the generic reverse
            cost is about $2^{{126}}$: about 126 bits against generic ECDLP
            attacks, conventionally grouped near the 128-bit classical level,
            rather than 252 or 255 bits.
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
            "What is actually proved?": mo.md(r"""
            Let $r\approx2^n$. In the **generic-group model**, any classical
            algorithm that only uses the abstract group operations needs
            $\Omega(\sqrt r)=\Omega(2^{n/2})$ operations to solve DLP with
            meaningful probability. Pollard rho meets that scale using little
            memory; baby-step–giant-step uses $O(\sqrt r)$ time and memory.

            This is not an unconditional proof that DLP is hard in every
            concrete group. Multiplicative finite-field DLP has
            index-calculus-style algorithms that exploit the representation
            and beat the generic square-root bound. No comparable general
            attack is known for well-chosen elliptic curves, so equal field bit
            lengths do not imply equal security.
            """),
            "From DLP to Curve25519": mo.md(r"""
            Elliptic curves replace exponentiation by scalar multiplication:

            \[
              x\longmapsto [x]G,
              \qquad [x]G\longmapsto x\quad\text{(ECDLP)}.
            \]

            Curve25519's main prime-order subgroup has
            $\ell\approx2^{252}$, so generic ECDLP work is about
            $\sqrt\ell\approx2^{126}$. X25519 exposes a $u$-coordinate and its
            key-agreement assumption is CDH-like: solving ECDLP would certainly
            break it, although protocol security is not literally the claim
            that every session requires recovering a long-term scalar.
            """),
            "The quantum boundary": mo.md(r"""
            Shor's quantum algorithm solves finite-field DLP and elliptic-curve
            DLP in polynomial time on a sufficiently large, fault-tolerant
            quantum computer. The asymmetry plotted above is therefore a
            **classical** hardness story. Curve25519 is excellent classical
            cryptography, but it is not post-quantum cryptography.
            """),
        }
    )
    return


if __name__ == "__main__":
    app.run()
