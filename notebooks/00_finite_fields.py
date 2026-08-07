import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt

    from running.finite import (
        generated_subgroup,
        mod_inverse,
        multiplicative_order,
    )

    return generated_subgroup, math, mo, mod_inverse, multiplicative_order, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 0 · Finite fields and cyclic groups

    Curve25519 arithmetic happens in a finite field. Start with the small
    version: integers wrap modulo a prime, every nonzero value has an inverse,
    and repeated multiplication traces a cyclic subgroup.
    """)
    return


@app.cell
def _(mo):
    field_prime = mo.ui.dropdown(
        options=[7, 11, 17, 29], value=29, label="prime $p$"
    )
    return (field_prime,)


@app.cell
def _(field_prime, mo):
    field_a = mo.ui.slider(
        1, field_prime.value - 1, value=min(7, field_prime.value - 1),
        label="$a$", show_value=True
    )
    field_b = mo.ui.slider(
        1, field_prime.value - 1, value=min(12, field_prime.value - 1),
        label="$b$", show_value=True
    )
    field_generator = mo.ui.slider(
        1, field_prime.value - 1, value=min(2, field_prime.value - 1),
        label="candidate $g$", show_value=True
    )
    field_operation = mo.ui.dropdown(
        options=["addition", "multiplication", "division", "exponentiation"],
        value="multiplication",
        label="operation",
    )
    mo.hstack(
        [field_prime, field_a, field_b, field_generator, field_operation],
        widths="equal",
        gap=1,
    )
    return field_a, field_b, field_generator, field_operation


@app.cell
def _(field_a, field_b, field_operation, field_prime, mo, mod_inverse):
    _p = field_prime.value
    _a = field_a.value
    _b = field_b.value
    if field_operation.value == "addition":
        field_result = (_a + _b) % _p
        field_expression = rf"{_a}+{_b}\equiv {field_result}\pmod{{{_p}}}"
    elif field_operation.value == "multiplication":
        field_result = (_a * _b) % _p
        field_expression = rf"{_a}\cdot {_b}\equiv {field_result}\pmod{{{_p}}}"
    elif field_operation.value == "division":
        field_result = _a * mod_inverse(_b, _p) % _p
        field_expression = (
            rf"{_a}/{_b}={_a}\cdot {_b}^{{-1}}"
            rf"\equiv {field_result}\pmod{{{_p}}}"
        )
    else:
        field_result = pow(_a, _b, _p)
        field_expression = rf"{_a}^{{{_b}}}\equiv {field_result}\pmod{{{_p}}}"

    mo.md(rf"""
    ## Arithmetic wraps, but remains exact

    \[
      {field_expression}.
    \]

    In $\mathbb F_p$, division is multiplication by a modular inverse—not
    floating-point division.
    """)
    return (field_result,)


@app.cell
def _(field_a, field_b, field_prime, field_result, math, mo, plt):
    _p = field_prime.value
    _angles = [2 * math.pi * value / _p for value in range(_p)]
    _xs = [math.sin(angle) for angle in _angles]
    _ys = [math.cos(angle) for angle in _angles]
    field_clock, _axis = plt.subplots(figsize=(6.8, 4.2))
    _axis.scatter(_xs, _ys, color="#8b949e", s=34, zorder=2)
    for _value, (_x, _y) in enumerate(zip(_xs, _ys, strict=True)):
        _axis.text(_x * 1.13, _y * 1.13, str(_value), ha="center", va="center")
    _colors = [(field_a.value, "#3b82f6", "$a$"),
               (field_b.value, "#f59e0b", "$b$"),
               (field_result, "#22c55e", "result")]
    for _value, _color, _label in _colors:
        _axis.scatter([_xs[_value]], [_ys[_value]], color=_color, s=120, label=_label, zorder=3)
    _axis.set_aspect("equal")
    _axis.axis("off")
    _axis.legend(loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)
    _axis.set_title(f"Arithmetic on a { _p }-position modular clock")
    field_clock.tight_layout()
    mo.output.replace(field_clock)
    return


@app.cell
def _(
    field_generator,
    field_prime,
    generated_subgroup,
    mo,
    multiplicative_order,
    plt,
):
    _p = field_prime.value
    _g = field_generator.value
    field_order = multiplicative_order(_g, _p)
    field_orbit = generated_subgroup(_g, _p)
    _positions = list(range(field_order))
    field_orbit_figure, _axis = plt.subplots(figsize=(7.2, 2.6))
    _axis.plot(_positions, field_orbit, marker="o", color="#3b82f6")
    _axis.set_xlabel("exponent $k$")
    _axis.set_ylabel(r"$g^k\;\mathrm{mod}\;p$")
    _axis.set_xticks(_positions)
    _axis.grid(alpha=0.2)
    field_orbit_figure.tight_layout()
    mo.vstack(
        [
            mo.md(
                rf"""
                ## The generated subgroup

                $\operatorname{{ord}}({_g})={field_order}$ in
                $\mathbb F_{{{_p}}}^\times$. Its powers visit
                `{field_orbit}` before returning to the identity $1$.
                """
            ),
            field_orbit_figure,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "Formal definitions": mo.md(r"""
            A **field** supports addition, subtraction, multiplication, and
            division by every nonzero element. For prime $p$,
            $\mathbb F_p=\mathbb Z/p\mathbb Z$ is a field.

            For a group element $g$,

            \[
            \operatorname{ord}(g)=\min\{n>0:g^n=e\},\qquad
            \langle g\rangle=\{e,g,g^2,\ldots\}.
            \]

            Lagrange's theorem says $\operatorname{ord}(g)$ divides the size of
            the finite ambient group. Security therefore depends on subgroup
            factorization, not merely on the field's bit length.
            """)
        }
    )
    return


if __name__ == "__main__":
    app.run()
