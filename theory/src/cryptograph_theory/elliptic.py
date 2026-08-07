"""A tiny Montgomery-curve group implementation for exhaustive experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import TypeAlias

from .finite import is_prime, mod_inverse

Point: TypeAlias = tuple[int, int] | None


@dataclass(frozen=True)
class MontgomeryCurve:
    """The curve ``v^2 = u^3 + A*u^2 + u`` over ``F_p``.

    This affine implementation is intentionally small and variable-time. It is
    suitable only for toy fields.
    """

    prime: int
    coefficient: int

    def __post_init__(self) -> None:
        if not is_prime(self.prime) or self.prime == 2:
            raise ValueError("prime must be an odd prime")
        if (self.coefficient * self.coefficient - 4) % self.prime == 0:
            raise ValueError("singular Montgomery curve")

    def rhs(self, u: int) -> int:
        u %= self.prime
        return (u**3 + self.coefficient * u * u + u) % self.prime

    def is_on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        u, v = point
        return (v * v - self.rhs(u)) % self.prime == 0

    def negate(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0] % self.prime, (-point[1]) % self.prime

    def add(self, left: Point, right: Point) -> Point:
        """Add two points using the affine Montgomery group law."""
        if not self.is_on_curve(left) or not self.is_on_curve(right):
            raise ValueError("both operands must lie on the curve")
        if left is None:
            return right
        if right is None:
            return left

        u1, v1 = left
        u2, v2 = right
        p = self.prime

        if u1 == u2 and (v1 + v2) % p == 0:
            return None

        if left == right:
            if v1 % p == 0:
                return None
            numerator = 3 * u1 * u1 + 2 * self.coefficient * u1 + 1
            slope = numerator * mod_inverse(2 * v1, p) % p
        else:
            slope = (v2 - v1) * mod_inverse(u2 - u1, p) % p

        u3 = (slope * slope - self.coefficient - u1 - u2) % p
        v3 = (slope * (u1 - u3) - v1) % p
        result = (u3, v3)
        if not self.is_on_curve(result):
            raise ArithmeticError("group-law result left the curve")
        return result

    def scalar_mul(self, scalar: int, point: Point) -> Point:
        """Compute ``[scalar]point`` with double-and-add."""
        if not self.is_on_curve(point):
            raise ValueError("point must lie on the curve")
        if scalar < 0:
            return self.scalar_mul(-scalar, self.negate(point))
        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            remaining >>= 1
        return result

    def points(self) -> list[Point]:
        """Enumerate every point, including the identity, for a small field."""
        if self.prime > 10_000:
            raise ValueError("point enumeration is only intended for toy fields")
        square_roots: dict[int, list[int]] = {}
        for v in range(self.prime):
            square_roots.setdefault(v * v % self.prime, []).append(v)
        finite = [
            (u, v)
            for u in range(self.prime)
            for v in square_roots.get(self.rhs(u), [])
        ]
        return [None, *finite]

    def point_order(self, point: Point) -> int:
        """Return a point's order, using Hasse's bound as a search limit."""
        if not self.is_on_curve(point):
            raise ValueError("point must lie on the curve")
        if point is None:
            return 1
        upper_bound = self.prime + 1 + 2 * isqrt(self.prime) + 2
        current: Point = None
        for order in range(1, upper_bound + 1):
            current = self.add(current, point)
            if current is None:
                return order
        raise ArithmeticError("point order exceeded Hasse's bound")

    def multiples(self, point: Point) -> list[Point]:
        """Return ``[0]P, [1]P, ...`` through one full cycle."""
        order = self.point_order(point)
        return [self.scalar_mul(scalar, point) for scalar in range(order)]


TOY_CURVE = MontgomeryCurve(prime=127, coefficient=5)
TOY_GENERATOR: Point = (18, 55)
TOY_SUBGROUP_ORDER = 17
TOY_COFACTOR = 8
