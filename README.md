# REV Pro-Hub — Stage 1 deployment starter

**Research • Evidence • Vision • Professional Hub**

This English-language starter includes a public landing page, registration, login/logout, user dashboard, public resource/module pages, a restricted-module approval gate, and an administrator page to approve accounts and assign roles.

## Access model (Option 1)
- Anyone can browse public pages and register.
- Newly registered accounts can use public resources immediately.
- Administrator approval and an eligible assigned role are required to access the restricted-module demo.
- Administrators can activate/deactivate accounts, approve access, and assign roles.
- New registrations cannot assign themselves privileged roles.
- Passwords are hashed and session cookies are configured as HTTP-only and SameSite=Lax.

## Deploy using Render Blueprint
1. Create a GitHub account if you do not already have one.
2. Create a **private** GitHub repository named `rev-pro-hub` and upload the contents of this folder (not the ZIP file itself).
3. Sign in to Render and choose **New → Blueprint**; connect the repository and deploy the `render.yaml` configuration.
4. When prompted for `REV_ADMIN_EMAIL`, enter the email you want to use for the first administrator. For `REV_ADMIN_PASSWORD`, create a unique, long password and store it safely. Never share it in chat or commit it to GitHub.
5. Render will provide a public `onrender.com` address after deployment. Test registration, sign-in, admin approval, logout, and persistence after a redeploy.
6. Only connect a custom domain after the application is tested; Render can provide HTTPS for the deployed site.

The blueprint requests a persistent disk for the SQLite database. Hosting providers can change their plan requirements and pricing; review the provider's current terms before deploying. Do not upload confidential patient-level or sensitive research data.

## Local run
1. Install Python 3.10 or newer.
2. Create/activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Set environment variables `REV_ADMIN_EMAIL`, `REV_ADMIN_PASSWORD`, and a long random `REV_SECRET_KEY`.
5. Run `python app.py` and open `http://127.0.0.1:5000`.

## Scope and important limitations
This is a Stage 1 development starter, not a completed production system or a deployment that has already gone live. Before public launch, add and test CSRF protection, login rate limiting, email verification, password reset, privacy/terms pages, audit logging, database backup/recovery, and security monitoring. Verify the administrator setup and recovery process. A persistent database and routine backups are required. Sensitive clinical/research data should not be stored until a data-protection review and appropriate access controls are implemented.

The Research, Public Health & QI, Data, Report, Training, and Exam areas are currently navigation and restricted-access demo pages, not fully implemented modules. There is no email delivery, email verification, password reset, file upload, exam engine, project database, or real statistical processing yet. Some homepage figures are illustrative; do not present them as actual platform activity.
