from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

PBKDF2_PREFIX = "pbkdf2_sha256"
DEFAULT_PBKDF2_ITERATIONS = 390_000
DEFAULT_SALT_BYTES = 18


class PasswordHashError(ValueError):
    """Raised when a stored password hash has an unsupported or invalid format."""


@dataclass(frozen=True)
class PasswordHashParts:
    algorithm: str
    iterations: int
    salt_hex: str
    digest_hex: str


def _validate_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    if not password:
        raise ValueError("password must not be empty")
    return password


def parse_password_hash(encoded: str) -> PasswordHashParts:
    if not isinstance(encoded, str) or not encoded.strip():
        raise PasswordHashError("password hash is empty")
    fields = encoded.strip().split("$")
    if len(fields) != 4:
        raise PasswordHashError("password hash must contain four '$'-separated fields")
    algorithm, iterations_text, salt_hex, digest_hex = fields
    if algorithm != PBKDF2_PREFIX:
        raise PasswordHashError(f"unsupported password hash algorithm: {algorithm}")
    try:
        iterations = int(iterations_text)
    except ValueError as exc:
        raise PasswordHashError("password hash iterations must be an integer") from exc
    if iterations < 100_000:
        raise PasswordHashError("password hash iteration count is below the minimum")
    try:
        salt = bytes.fromhex(salt_hex)
        digest = bytes.fromhex(digest_hex)
    except ValueError as exc:
        raise PasswordHashError("password hash salt or digest is not valid hexadecimal") from exc
    if len(salt) < 16:
        raise PasswordHashError("password hash salt is too short")
    if len(digest) != hashlib.sha256().digest_size:
        raise PasswordHashError("password hash digest has an unexpected length")
    return PasswordHashParts(algorithm, iterations, salt_hex.lower(), digest_hex.lower())


def hash_password(
    password: str,
    *,
    iterations: int = DEFAULT_PBKDF2_ITERATIONS,
    salt: bytes | None = None,
) -> str:
    """Return a PBKDF2-SHA256 password hash suitable for Streamlit secrets."""
    password = _validate_password(password)
    if iterations < 100_000:
        raise ValueError("iterations must be at least 100000")
    salt = salt if salt is not None else secrets.token_bytes(DEFAULT_SALT_BYTES)
    if len(salt) < 16:
        raise ValueError("salt must be at least 16 bytes")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{PBKDF2_PREFIX}${iterations}${salt.hex()}${digest.hex()}"


def verify_password_hash(candidate: str, encoded_hash: str) -> bool:
    """Verify a candidate password against a PBKDF2-SHA256 encoded hash."""
    if not isinstance(candidate, str):
        return False
    try:
        parts = parse_password_hash(encoded_hash)
    except PasswordHashError:
        return False
    salt = bytes.fromhex(parts.salt_hex)
    expected = bytes.fromhex(parts.digest_hex)
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        candidate.encode("utf-8"),
        salt,
        parts.iterations,
    )
    return hmac.compare_digest(actual, expected)


def verify_password(
    candidate: str,
    *,
    password_hash: str | None = None,
    plaintext_password: str | None = None,
) -> bool:
    """Verify against a preferred hash or a deployment-provided plaintext secret."""
    if password_hash:
        return verify_password_hash(candidate, password_hash)
    if plaintext_password is None or not isinstance(candidate, str):
        return False
    return hmac.compare_digest(candidate.encode("utf-8"), plaintext_password.encode("utf-8"))
