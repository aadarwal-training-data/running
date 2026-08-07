from running.finite import (
    discrete_log_bruteforce,
    discrete_log_bsgs,
    generated_subgroup,
    legendre_symbol,
    mod_inverse,
    multiplicative_order,
)


def test_modular_inverse_and_quadratic_residues() -> None:
    assert mod_inverse(7, 29) == 25
    assert 7 * mod_inverse(7, 29) % 29 == 1
    assert legendre_symbol(0, 29) == 0
    assert legendre_symbol(4, 29) == 1
    assert legendre_symbol(2, 29) == -1


def test_generator_and_discrete_log_solvers() -> None:
    assert multiplicative_order(2, 29) == 28
    assert len(generated_subgroup(2, 29)) == 28
    target = pow(2, 19, 29)
    assert discrete_log_bruteforce(2, target, 29, 28) == 19
    assert discrete_log_bsgs(2, target, 29, 28) == 19


def test_discrete_log_reports_target_outside_subgroup() -> None:
    assert multiplicative_order(4, 29) == 14
    assert discrete_log_bsgs(4, 2, 29, 14) is None
