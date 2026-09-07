Backend:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npx ng serve
```

Use Node.js `22.22.3+` or `24.15.0+` for this Angular project.

## Demo accounts
- admin@buildtrack.com / Admin@123
- manager@buildtrack.com / Manager@123
- engineer@buildtrack.com / Engineer@123
- contractor@buildtrack.com / Contractor@123
- worker@buildtrack.com / Worker@123
- client@buildtrack.com / Client@123
## Create Account / Forgot Password

Create Account:
1. Open http://localhost:4200/register
2. Fill Full Name, Email, Mobile Number, Employee ID, Role and Password.
3. Password must contain uppercase, lowercase, number and special character.
4. Public ADMIN registration is blocked. Use the seeded admin account for admin login.

Forgot Password:
1. Open http://localhost:4200/forgot-password
2. Enter a registered email.
3. In local development, because SMTP is not configured, the reset link appears on the page and is also printed in the backend terminal.
4. Open the reset link, set a new strong password and log in again.
5. For production, configure SMTP and set BUILDTRACK_EXPOSE_RESET_LINK=0.

## Real SMTP email setup for Forgot Password

This build supports real email delivery through SMTP. Edit `backend/.env` and fill in:

```env
FRONTEND_BASE_URL=http://localhost:4200
BUILDTRACK_EXPOSE_RESET_LINK=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=BuildTrack
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

Restart the backend after editing `.env`.
See `SMTP_EMAIL_SETUP_GUIDE.md` for details.


## Presentation demo data

This package includes demo records inside `backend/buildtrack.db` so you can present the project immediately:
5 demo projects, 4 demo workers, demo contractors, resources, machinery, allocations, attendance, milestones and notifications.

The backend also auto-recreates the demo records on SQLite startup if they are missing.

To disable this later, add this in `backend/.env`:

```env
BUILDTRACK_PRESENTATION_DEMO_DATA=0
```
