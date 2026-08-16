# Project-MSR Planner 4.2.1 release notes

Release date: 2026-08-16

Version 4.2.1 adds a fail-closed password gate to the complete 4.2 engineering, licensing, resource, schedule, and cost-planning application.

## Access-control changes

- Added a server-side password gate before database loading or planner rendering.
- Added PBKDF2-SHA256 password hashing and constant-time verification.
- Added Streamlit secrets and environment-variable configuration.
- Added temporary lockout after repeated failed attempts.
- Added idle-session expiration and a Sign out control.
- Added a password-rotation utility and deployment guide.
- Added a locally usable hashed secret for the requested release password; no plaintext password is stored in the package.
- Preserved the complete v4.2.0 database and all planning, pathway, resource, cost, schedule, graph, and export functionality.

## Verification

- Python compilation passed.
- Database-integrity and scenario tests passed.
- Authentication hash and verification tests passed.
- Forty-four automated tests passed.
- Secured application control-flow smoke testing passed.
