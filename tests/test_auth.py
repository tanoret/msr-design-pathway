from __future__ import annotations

import pytest

from src.auth_utils import (
    PasswordHashError,
    hash_password,
    parse_password_hash,
    verify_password,
    verify_password_hash,
)


def test_password_hash_round_trip() -> None:
    encoded = hash_password("test-password-alpha", salt=bytes.fromhex("00112233445566778899aabbccddeeff00"))
    assert verify_password_hash("test-password-alpha", encoded)
    assert not verify_password_hash("TEST-PASSWORD-ALPHA", encoded)
    assert not verify_password_hash("wrong-password", encoded)


def test_password_hash_uses_pbkdf2_sha256() -> None:
    encoded = hash_password("test-password", salt=b"0123456789abcdef")
    parts = parse_password_hash(encoded)
    assert parts.algorithm == "pbkdf2_sha256"
    assert parts.iterations >= 100_000
    assert len(bytes.fromhex(parts.salt_hex)) >= 16
    assert len(bytes.fromhex(parts.digest_hex)) == 32


def test_malformed_hash_fails_closed() -> None:
    assert not verify_password_hash("anything", "not-a-valid-hash")
    with pytest.raises(PasswordHashError):
        parse_password_hash("not-a-valid-hash")


def test_hash_takes_precedence_over_plaintext_secret() -> None:
    encoded = hash_password("correct", salt=b"fedcba9876543210")
    assert verify_password("correct", password_hash=encoded, plaintext_password="different")
    assert not verify_password("different", password_hash=encoded, plaintext_password="different")


def test_plaintext_deployment_secret_is_constant_time_compatible() -> None:
    assert verify_password("test-password-alpha", plaintext_password="test-password-alpha")
    assert not verify_password("wrong", plaintext_password="test-password-alpha")
    assert not verify_password("anything")
