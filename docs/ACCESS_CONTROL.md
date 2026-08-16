# Project-MSR access control

Version 4.2.2 retains a password gate in front of the Streamlit application. The gate is evaluated before the bundled planning database is opened, scenario calculations are run, or any planner page is rendered.

## Authentication behavior

- Password-only access gate with a centered secure-access screen.
- Password verification is performed server-side.
- PBKDF2-SHA256 password hashes are supported and preferred.
- Plaintext passwords are accepted only through protected deployment secrets or environment variables.
- Five failed attempts trigger a 30-second session lock by default.
- Authenticated sessions expire after 12 hours of inactivity by default.
- A Sign out control clears the authenticated Streamlit session.
- Missing authentication configuration fails closed; the planner is not displayed.

## Local package

The release package includes `.streamlit/secrets.toml` with a PBKDF2-SHA256 hash for the requested release password. The plaintext password is not stored in the application source or secrets file.

Run locally with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The `.streamlit/secrets.toml` file is ignored by Git and should remain uncommitted.

## Streamlit Community Cloud

Because `.streamlit/secrets.toml` is intentionally excluded from Git, copy its `[auth]` block into the Streamlit Community Cloud application settings under **Secrets** before starting the application.

The supported secrets format is:

```toml
[auth]
password_hash = "pbkdf2_sha256$..."
session_timeout_minutes = 720
max_attempts = 5
lockout_seconds = 30
```

The same values can be supplied as environment variables:

- `PROJECT_MSR_PASSWORD_HASH`
- `PROJECT_MSR_PASSWORD`
- `PROJECT_MSR_SESSION_TIMEOUT_MINUTES`
- `PROJECT_MSR_MAX_ATTEMPTS`
- `PROJECT_MSR_LOCKOUT_SECONDS`

If both a password hash and plaintext password are configured, the password hash takes precedence.

## Rotate the password

Generate a new local hash without storing the plaintext password:

```bash
python scripts/set_password.py
```

For an automated deployment:

```bash
python scripts/set_password.py --password "a-new-strong-password" --output /tmp/secrets.toml
```

Copy the resulting `[auth]` block into the deployment secret manager and restart the application.

## Security boundary

The login gate protects the deployed Streamlit user interface. It does not make files confidential when the source repository itself is public. If the database must remain confidential, deploy from a private repository or move the `data/project_msr_database.*.json` files to private storage that is mounted or injected only at runtime.
