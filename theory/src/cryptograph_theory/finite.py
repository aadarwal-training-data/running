"""Small finite-field and discrete-logarithm helpers for teaching."""

from __future__ import annotations

from math import ceil, isqrt


def is_prime(n: int) -> bool:
    """Return whether ``n`` is prime, using trial division for small examples."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    limit = isqrt(n)
    return all(n % divisor for divisor in range(3, limit + 1, 2))


def mod_inverse(value: int, modulus: int) -> int:
    """Return the multiplicative inverse of ``value`` modulo ``modulus``."""
    try:
        return pow(value % modulus, -1, modulus)
    except ValueError as error:
        raise ValueError(f"{value} has no inverse modulo {modulus}") from error


def legendre_symbol(value: int, prime: int) -> int:
    """Return -1, 0, or 1 according to quadratic-residue membership."""
    residue = value % prime
    if residue == 0:
        return 0
    symbol = pow(residue, (prime - 1) // 2, prime)
    return -1 if symbol == prime - 1 else symbol


def multiplicative_order(generator: int, prime: int) -> int:
    """Return the order of ``generator`` in the multiplicative group mod ``prime``."""
    generator %= prime
    if generator == 0:
        raise ValueError("zero is not in the multiplicative group")
    value = 1
    for order in range(1, prime):
        value = value * generator % prime
        if value == 1:
            return order
    raise ArithmeticError("order search exceeded the group size")


def generated_subgroup(generator: int, prime: int) -> list[int]:
    """List powers of ``generator`` until the identity repeats."""
    order = multiplicative_order(generator, prime)
    return [pow(generator, exponent, prime) for exponent in range(order)]


def discrete_log_bruteforce(
    generator: int,
    target: int,
    prime: int,
    order: int | None = None,
) -> int | None:
    """Solve a tiny multiplicative DLP by exhaustive search."""
    subgroup_order = order or multiplicative_order(generator, prime)
    value = 1
    for exponent in range(subgroup_order):
        if value == target % prime:
            return exponent
        value = value * generator % prime
    return None

def discrete_log_bsgs(
    generator: int,
    target: int,
    prime: int,
    order: int | None = None,
) -> int | None:
    """Solve a multiplicative DLP with baby-step--giant-step.

    The result is an exponent modulo the order of ``generator``. ``None`` means
    that ``target`` was not found in the selected subgroup.
    """
    subgroup_order = order or multiplicative_order(generator, prime)
    width = ceil(subgroup_order**0.5)

    babies: dict[int, int] = {}
    value = 1
    for small in range(width):
        babies.setdefault(value, small)
        value = value * generator % prime

    giant_factor = mod_inverse(pow(generator, width, prime), prime)
    candidate = target % prime
    for giant in range(width + 1):
        if candidate in babies:
            exponent = giant * width + babies[candidate]
            if exponent < subgroup_order and pow(generator, exponent, prime) == target % prime:
                return exponent
        candidate = candidate * giant_factor % prime
    return None
