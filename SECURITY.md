# Security

The Python in this repository is for explanation, visualization, and RFC test
vectors only.

It is **not production cryptography**:

- Python integer arithmetic and branches are not constant-time.
- The examples omit operating-system entropy handling, secret-memory handling,
  fault resistance, and many protocol checks.
- The toy curves are intentionally tiny and can be broken immediately.
- X25519 by itself does not authenticate either peer and is vulnerable to an
  active man-in-the-middle.

Production systems should use a maintained high-level implementation of an
authenticated protocol. They should handle an all-zero DH result, bind the
ordered public keys and transcript into a KDF, derive distinct directional
keys, and use an AEAD with correct nonce management.

Please report errors in the educational material through a private GitHub
security advisory when disclosure would be safer than a public issue.
