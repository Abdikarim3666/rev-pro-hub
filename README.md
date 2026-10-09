# REV Pro-Hub — English public platform starter

**Research • Evidence • Vision • Professional Hub**

This is a runnable first backend version of REV Pro-Hub. It includes a public landing page, registration, login/logout, user dashboard, public resource/module pages, a restricted-module approval gate, and an administrator page to approve accounts and assign roles. Passwords are hashed; sessions use HTTP-only cookies; new registrations start as public visitors and cannot grant themselves privileged roles.

## Access model (Option 1)
- Anyone can browse public pages and register.
- A new account can use public pages immediately.
- Administrator approval and an assigned eligible role are required to enter the restricted module demo.
- The administrator can activate/deactivate accounts, approve access, and assign roles.
- The first administrator is created from environment variables on first startup if the specified email does not already exist.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set administrator environment variables before starting the app. At minimum set `REV_ADMIN_EMAIL` and a strong `REV_ADMIN_PASSWORD`; also set a long random `REV_SECRET_KEY`.
6. Start: `python app.py`
7. Open `http://127.0.0.1:5000` in your browser and sign in with the configured administrator account.

## Important before public deployment
This is a starter, not a fully production-hardened service. Before opening it to the public, deploy behind HTTPS on a maintained host; set `REV_HTTPS_ONLY=1`; use a strong secret and unique admin password; configure backups and persistent database storage; add email verification and password reset; add CSRF protection, login rate limiting, security monitoring, privacy/terms pages, and a tested recovery plan. SQLite may be fine for a small pilot but a managed PostgreSQL database is preferable as usage grows. Do not upload confidential patient-level data or sensitive research records until access controls, auditing, consent, data protection, and hosting arrangements have been reviewed.

## Current scope and limitations
The Research, Public Health & QI, Data, Report, Training, and Exam areas are represented as navigation and a restricted-access demo, not yet fully implemented production modules. There is no email delivery, email verification, password reset, file upload, exam engine, project database, or real statistical processing yet. Dashboard figures are live counts of starter-app users/roles, except module counts which are illustrative. A user may register and use public resources; role and approval must be changed by an administrator for restricted access.
