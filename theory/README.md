# cryptograph / theory

[Back to the repository index](../README.md)

**A concise, visual path from finite fields and discrete logarithms to
Curve25519 and X25519.**

This module pairs a short formal note in LaTeX with executable
[marimo](https://marimo.io/) notebooks. The emphasis is the mathematical chain

```text
finite fields → cyclic groups → DLP/ECDLP → ECDH → Curve25519 → X25519
```

and the places where that chain is often oversimplified: subgroup order versus
field size, DLP versus CDH, the cofactor and quadratic twist, x-only arithmetic,
scalar clamping, and the fact that raw Diffie-Hellman is not an authenticated
protocol.

## Start here

1. Read the compiled [`tex/cryptograph-theory.pdf`](tex/cryptograph-theory.pdf)
   or its [`tex/main.tex`](tex/main.tex) source.
2. Run the notebooks in order:

   | Notebook | Question |
   |---|---|
   | [`00_finite_fields.py`](notebooks/00_finite_fields.py) | What does arithmetic modulo a prime look like? |
   | [`01_discrete_logarithms.py`](notebooks/01_discrete_logarithms.py) | Why is exponentiation easy to run forward and hard to reverse? |
   | [`02_elliptic_curve_group.py`](notebooks/02_elliptic_curve_group.py) | How do discrete curve points form a group? |
   | [`03_ecdh.py`](notebooks/03_ecdh.py) | Why do Alice and Bob reach the same point, and where does MITM enter? |
   | [`04_x25519_ladder.py`](notebooks/04_x25519_ladder.py) | How do clamping and the Montgomery ladder produce X25519? |

## Run locally

The project uses Python 3.11+ and [`uv`](https://docs.astral.sh/uv/). From the
repository root:

```bash
cd theory
uv sync --dev
uv run marimo edit notebooks/00_finite_fields.py
```

Useful checks:

```bash
make check       # lint, notebook structure, and tests
make notebooks   # execute every notebook and export HTML
make paper       # compile build/main.pdf and refresh tex/cryptograph-theory.pdf
```

## The formal bridge to Curve25519

For a cyclic group \(\langle G\rangle\) of order \(\ell\), the discrete
logarithm problem is

\[
  Q=[a]G \longmapsto a \pmod \ell.
\]

Curve25519 instantiates this group inside an elliptic curve over
\(\mathbb F_{2^{255}-19}\). X25519 exposes only the Montgomery
\(u\)-coordinate, so \(u(P)=u(-P)\): an honest public key determines its scalar
only up to sign modulo \(\ell\). That ambiguity does not help an attacker avoid
the elliptic-curve discrete logarithm problem or compute the Diffie-Hellman
value

\[
  \bigl(u(G),u([a]G),u([b]G)\bigr) \longmapsto u([ab]G).
\]

The note makes this relationship precise and distinguishes it from the stronger
claim that DLP, CDH, and DDH are equivalent; they are not known to be equivalent
in arbitrary groups. Passive X25519 key agreement rests on an x-only CDH-style
assumption; an ECDLP solver is one sufficient way to break it, not a proof that
the two problems are equivalent.

### What "hard" means here

Let \(n=\lceil\log_2 \ell\rceil\) be the subgroup-order bit length. Forward
scalar multiplication takes \(O(n)\) group operations. Generic classical
inversion takes \(\Theta(\sqrt\ell)=\Theta(2^{n/2})\): Pollard rho supplies the
upper bound, while Shoup's matching lower bound applies only in the generic
group model. Curve25519 therefore has a best-known generic ECDLP cost near
\(2^{126}\), but this is a classical hardness assumption, not an unconditional
complexity lower bound. A sufficiently capable quantum computer could instead
use Shor's polynomial-time algorithm.

## Scope and safety

Everything under `src/cryptograph_theory` is educational reference code. It is
deliberately clear Python, not constant-time production cryptography. For real
applications, use a maintained protocol and library such as TLS 1.3, Noise,
HPKE, or libsodium. See [`SECURITY.md`](../SECURITY.md).

Primary references are [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748.html),
Bernstein's [Curve25519 paper](https://cr.yp.to/ecdh/curve25519-20060209.pdf),
[RFC 5869](https://www.rfc-editor.org/rfc/rfc5869.html), and
[RFC 9180](https://www.rfc-editor.org/rfc/rfc9180.html). The complexity
discussion uses Shoup's
[generic-group lower bound](https://www.shoup.net/papers/dlbounds1.pdf),
Gordon's
[number-field-sieve analysis](https://www.dmgordon.org/papers/log.pdf), and
Shor's
[quantum discrete-log algorithm](https://arxiv.org/abs/quant-ph/9508027).
