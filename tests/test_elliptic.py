from collections import Counter
from random import Random

from running.elliptic import TOY_CURVE, TOY_GENERATOR


def test_toy_curve_parameters_and_subgroup() -> None:
    assert len(TOY_CURVE.points()) == 136
    assert TOY_CURVE.is_on_curve(TOY_GENERATOR)
    assert TOY_CURVE.point_order(TOY_GENERATOR) == 17
    assert TOY_CURVE.scalar_mul(17, TOY_GENERATOR) is None
    assert TOY_CURVE.scalar_mul(5, TOY_GENERATOR) == (122, 73)
    assert TOY_CURVE.scalar_mul(9, TOY_GENERATOR) == (124, 74)
    assert TOY_CURVE.scalar_mul(11, TOY_GENERATOR) == (70, 64)


def test_toy_curve_point_order_distribution() -> None:
    distribution = Counter(TOY_CURVE.point_order(point) for point in TOY_CURVE.points())
    assert distribution == {1: 1, 2: 3, 4: 4, 17: 16, 34: 48, 68: 64}


def test_ecdh_equality() -> None:
    alice_public = TOY_CURVE.scalar_mul(5, TOY_GENERATOR)
    bob_public = TOY_CURVE.scalar_mul(9, TOY_GENERATOR)
    assert TOY_CURVE.scalar_mul(5, bob_public) == (70, 64)
    assert TOY_CURVE.scalar_mul(5, bob_public) == TOY_CURVE.scalar_mul(9, alice_public)


def test_sampled_group_laws() -> None:
    points = TOY_CURVE.points()
    random = Random(25519)
    for _ in range(100):
        left, middle, right = random.choices(points, k=3)
        assert TOY_CURVE.add(left, middle) == TOY_CURVE.add(middle, left)
        assert TOY_CURVE.add(TOY_CURVE.add(left, middle), right) == TOY_CURVE.add(
            left, TOY_CURVE.add(middle, right)
        )


def test_cofactor_clearing() -> None:
    order_68_point = (5, 1)
    assert TOY_CURVE.point_order(order_68_point) == 68
    cleared = TOY_CURVE.scalar_mul(8, order_68_point)
    assert cleared is not None
    assert TOY_CURVE.point_order(cleared) == 17
    assert TOY_CURVE.scalar_mul(8, (0, 0)) is None
