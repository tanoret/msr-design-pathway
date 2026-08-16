from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Mapping

import streamlit as st

from src.auth_utils import verify_password

_AUTH_OK = "_project_msr_authenticated"
_AUTH_AT = "_project_msr_authenticated_at"
_AUTH_LAST = "_project_msr_last_activity"
_AUTH_FAILURES = "_project_msr_failed_attempts"
_AUTH_LOCKED_UNTIL = "_project_msr_locked_until"
_AUTH_PASSWORD_WIDGET = "_project_msr_password"


@dataclass(frozen=True)
class AuthConfig:
    password_hash: str | None
    plaintext_password: str | None
    session_timeout_minutes: int
    max_attempts: int
    lockout_seconds: int

    @property
    def configured(self) -> bool:
        return bool(self.password_hash or self.plaintext_password)


def _safe_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _secret_auth_mapping() -> Mapping[str, Any]:
    try:
        auth = st.secrets.get("auth", {})
    except Exception:
        return {}
    try:
        return dict(auth)
    except Exception:
        return {}


def load_auth_config() -> AuthConfig:
    """Load authentication settings from environment or Streamlit secrets.

    Environment variables take precedence so container deployments can inject a
    secret without writing a file. Supported values:

    - PROJECT_MSR_PASSWORD_HASH
    - PROJECT_MSR_PASSWORD
    - PROJECT_MSR_SESSION_TIMEOUT_MINUTES
    - PROJECT_MSR_MAX_ATTEMPTS
    - PROJECT_MSR_LOCKOUT_SECONDS

    Equivalent Streamlit secrets live under the [auth] table.
    """
    secret_auth = _secret_auth_mapping()
    password_hash = os.getenv("PROJECT_MSR_PASSWORD_HASH") or secret_auth.get("password_hash")
    plaintext_password = os.getenv("PROJECT_MSR_PASSWORD") or secret_auth.get("password")
    session_timeout = os.getenv("PROJECT_MSR_SESSION_TIMEOUT_MINUTES") or secret_auth.get("session_timeout_minutes")
    max_attempts = os.getenv("PROJECT_MSR_MAX_ATTEMPTS") or secret_auth.get("max_attempts")
    lockout_seconds = os.getenv("PROJECT_MSR_LOCKOUT_SECONDS") or secret_auth.get("lockout_seconds")

    return AuthConfig(
        password_hash=str(password_hash).strip() if password_hash else None,
        plaintext_password=str(plaintext_password) if plaintext_password is not None else None,
        session_timeout_minutes=_safe_int(session_timeout, 720, 5, 10_080),
        max_attempts=_safe_int(max_attempts, 5, 1, 20),
        lockout_seconds=_safe_int(lockout_seconds, 30, 1, 900),
    )


def _session_get(key: str, default: Any = None) -> Any:
    try:
        return st.session_state.get(key, default)
    except Exception:
        return default


def _session_set(key: str, value: Any) -> None:
    st.session_state[key] = value


def clear_authentication() -> None:
    for key in (_AUTH_OK, _AUTH_AT, _AUTH_LAST, _AUTH_FAILURES, _AUTH_LOCKED_UNTIL, _AUTH_PASSWORD_WIDGET):
        try:
            st.session_state.pop(key, None)
        except Exception:
            pass


def is_authenticated(config: AuthConfig, *, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    if not bool(_session_get(_AUTH_OK, False)):
        return False
    last_activity = float(_session_get(_AUTH_LAST, _session_get(_AUTH_AT, now)) or now)
    timeout_seconds = config.session_timeout_minutes * 60
    if now - last_activity > timeout_seconds:
        clear_authentication()
        return False
    _session_set(_AUTH_LAST, now)
    return True


def _locked_seconds_remaining(*, now: float | None = None) -> int:
    now = time.time() if now is None else now
    locked_until = float(_session_get(_AUTH_LOCKED_UNTIL, 0.0) or 0.0)
    if locked_until <= now:
        if locked_until:
            _session_set(_AUTH_LOCKED_UNTIL, 0.0)
            _session_set(_AUTH_FAILURES, 0)
        return 0
    return max(1, int(round(locked_until - now)))


def _record_failure(config: AuthConfig, *, now: float | None = None) -> int:
    now = time.time() if now is None else now
    failures = int(_session_get(_AUTH_FAILURES, 0) or 0) + 1
    _session_set(_AUTH_FAILURES, failures)
    if failures >= config.max_attempts:
        _session_set(_AUTH_LOCKED_UNTIL, now + config.lockout_seconds)
    return failures


def _mark_authenticated(*, now: float | None = None) -> None:
    now = time.time() if now is None else now
    _session_set(_AUTH_OK, True)
    _session_set(_AUTH_AT, now)
    _session_set(_AUTH_LAST, now)
    _session_set(_AUTH_FAILURES, 0)
    _session_set(_AUTH_LOCKED_UNTIL, 0.0)
    try:
        st.session_state.pop(_AUTH_PASSWORD_WIDGET, None)
    except Exception:
        pass


def _render_login_header() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] { display:none !important; }
        .block-container { max-width: 760px !important; padding-top: 7vh !important; }
        div[data-testid="stForm"] {
          border: 1px solid #dbe3ef;
          background: rgba(255,255,255,.96);
          border-radius: 20px;
          box-shadow: 0 18px 50px rgba(35,55,90,.12);
          padding: 1.05rem 1.15rem 1.15rem;
        }
        </style>
        <div class="msr-login-shell">
          <div class="msr-login-mark">MSR</div>
          <div class="msr-login-eyebrow">Restricted planning environment</div>
          <div class="msr-login-title">Project-MSR Secure Access</div>
          <div class="msr-login-copy">Enter the authorized access password to open the integrated engineering, licensing, resource, and financial plan.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_authentication() -> bool:
    """Render a password gate and return True only for an authenticated session."""
    config = load_auth_config()
    if is_authenticated(config):
        return True

    _render_login_header()
    if not config.configured:
        st.error("Access control is not configured for this deployment.")
        st.caption("Set PROJECT_MSR_PASSWORD_HASH or configure [auth].password_hash in Streamlit secrets.")
        return False

    remaining = _locked_seconds_remaining()
    with st.form("project_msr_login", clear_on_submit=False):
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter access password",
            key=_AUTH_PASSWORD_WIDGET,
        )
        submitted = st.form_submit_button("Unlock planner", type="primary", use_container_width=True)

    if remaining:
        st.error(f"Access is temporarily locked. Try again in {remaining} seconds.")
        return False

    if submitted:
        if verify_password(
            password or "",
            password_hash=config.password_hash,
            plaintext_password=config.plaintext_password,
        ):
            _mark_authenticated()
            st.rerun()
        else:
            failures = _record_failure(config)
            attempts_left = max(0, config.max_attempts - failures)
            if attempts_left:
                st.error(f"Incorrect password. {attempts_left} attempt{'s' if attempts_left != 1 else ''} remaining before a temporary lock.")
            else:
                st.error(f"Access is temporarily locked for {config.lockout_seconds} seconds.")
    return False


def render_logout_control() -> None:
    """Show a compact authenticated-session control in the sidebar."""
    st.sidebar.markdown(
        """
        <div class="msr-session-card">
          <div class="msr-session-dot"></div>
          <div><div class="msr-session-title">Secure session</div><div class="msr-session-copy">Planning data unlocked</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Sign out", key="_project_msr_logout", use_container_width=True):
        clear_authentication()
        st.rerun()
