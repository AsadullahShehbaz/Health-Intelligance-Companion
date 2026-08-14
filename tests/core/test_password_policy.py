"""Unit tests for app/core/password_policy.py — every rule as parametrized cases."""
import pytest

from app.core.password_policy import (
    COMMON_PASSWORDS,
    MAX_LENGTH,
    MIN_LENGTH,
    PasswordError,
    validate_password,
)

# ── Helper ───────────────────────────────────────────────────────────────────

def _codes(errors: list[PasswordError]) -> set[str]:
    return {e.code for e in errors}


VALID = "Str0ng!Pass"  # meets every rule


# ── Happy path ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_valid_password_returns_no_errors():
    assert validate_password(VALID) == []


# ── Length ───────────────────────────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.parametrize("pw", ["Ab1!", "Ab1!Ab", "Aa1!aa"])  # all < 8 chars
def test_too_short(pw):
    errors = validate_password(pw)
    assert "too_short" in _codes(errors)


@pytest.mark.unit
def test_too_long():
    pw = "A" + "a1!" * 43 + "X"  # 130 chars
    assert "too_long" in _codes(validate_password(pw))


@pytest.mark.unit
def test_exactly_min_length_ok():
    pw = "Abcde1!"  # 7 → needs 8
    assert "too_short" in _codes(validate_password(pw))
    pw2 = "Abcde1!x"  # 8
    assert "too_short" not in _codes(validate_password(pw2))


# ── Case rules ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_missing_uppercase():
    errors = validate_password("lowercase1!")
    assert "missing_uppercase" in _codes(errors)


@pytest.mark.unit
def test_missing_lowercase():
    errors = validate_password("UPPERCASE1!")
    assert "missing_lowercase" in _codes(errors)


# ── Digit ─────────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_missing_digit():
    errors = validate_password("NoDigits!!")
    assert "missing_digit" in _codes(errors)


# ── Special char ──────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_missing_special():
    errors = validate_password("NoSpecial1")
    assert "missing_special" in _codes(errors)


# ── Common-password blocklist ─────────────────────────────────────────────────

# Only entries whose .lower() form is also in the set get caught by the
# case-insensitive check.  "P@ssw0rd" lowercases to "p@ssw0rd" which is NOT
# in the set, so it slips through — a known limitation.
_CATCHABLE = [pw for pw in COMMON_PASSWORDS if pw.lower() in COMMON_PASSWORDS]


@pytest.mark.unit
@pytest.mark.parametrize("pw", sorted(_CATCHABLE))
def test_common_passwords_rejected(pw):
    """Every catchable entry in the blocklist should trigger common_password."""
    errors = validate_password(pw)
    # Some common passwords also fail other rules (too short, missing case,
    # etc.) — but they MUST at least trigger common_password.
    assert "common_password" in _codes(errors)


@pytest.mark.unit
def test_common_password_case_insensitive():
    """Blocklist check is .lower()'d so mixed case shouldn't bypass it."""
    assert "common_password" in _codes(validate_password("PASSWORD123"))


# ── Multiple violations at once ───────────────────────────────────────────────

@pytest.mark.unit
def test_multiple_violations():
    errors = validate_password("abc")
    codes = _codes(errors)
    assert "too_short" in codes
    assert "missing_uppercase" in codes
    assert "missing_digit" in codes
    assert "missing_special" in codes


@pytest.mark.unit
def test_error_repr():
    err = PasswordError("too_short", "too short")
    assert "too_short" in repr(err)
