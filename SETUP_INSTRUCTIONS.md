# Setup Instructions for Security Fixes

## Quick Setup

The immediate security fixes have been implemented. Follow these steps to complete the setup:

### 1. Generate Admin Password Hash

Generate a password hash using this one-liner:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password-here'))"
```

Replace `'your-password-here'` with your desired password. Copy the output hash.

### 2. Set Environment Variables

Create a `.env` file in the project root (or set environment variables):

```bash
# Required for production
ADMIN_PASSWORD_HASH=<paste-the-hash-from-step-1>
JWT_SECRET_KEY=<generate-a-random-secret-key>

# Optional
FLASK_ENV=development  # or 'production'
FLASK_DEBUG=false     # set to 'true' only in development
DATABASE_URL=sqlite:///instance/dev.db
```

### 3. Generate JWT Secret Key

Generate a secure random key:

```bash
# On Linux/Mac:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# On Windows PowerShell:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as `JWT_SECRET_KEY`.

### 4. For Production

**IMPORTANT:** Before deploying to production:

1. ✅ Set `FLASK_ENV=production`
2. ✅ Set `FLASK_DEBUG=false` (or don't set it, defaults to false)
3. ✅ Set `ADMIN_PASSWORD_HASH` (required - login will fail without it)
4. ✅ Set `JWT_SECRET_KEY` (required - app will fail to start without it)
5. ✅ Use a production database (PostgreSQL recommended)
6. ✅ Never commit `.env` file to version control

### 5. Test the Setup

1. Start the application:
   ```bash
   python app.py
   ```

2. Test login with your password (email can be anything):
   ```bash
   curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "your-password"}'
   ```

## What Was Fixed

✅ **Authentication Security:**
- Removed hardcoded credentials
- Added password hashing using Werkzeug
- Single password stored in environment variable (email is ignored)

✅ **JWT Security:**
- Enforces JWT_SECRET_KEY in production
- Fails fast if not set in production mode

✅ **Debug Mode:**
- Disabled by default
- Only enabled if `FLASK_DEBUG=true` is explicitly set
- Prevents accidental debug mode in production

✅ **Logging:**
- Added basic logging to `logs/app.log`
- Rotates logs (10MB max, 10 backups)
- Only active when not in debug mode

## Development vs Production

### Development
- Can use default credentials (admin@example.com / password) if `ADMIN_PASSWORD_HASH` not set
- Debug mode can be enabled with `FLASK_DEBUG=true`
- Uses SQLite by default

### Production
- **REQUIRES** `ADMIN_PASSWORD_HASH` environment variable
- **REQUIRES** `JWT_SECRET_KEY` environment variable
- Debug mode is disabled
- Logging is enabled

## Troubleshooting

**Login fails even with correct password:**
- Check that `ADMIN_PASSWORD_HASH` is set correctly
- Verify the hash was generated with the same password
- Email field can be anything - only password matters

**App fails to start in production:**
- Check that `JWT_SECRET_KEY` is set
- Check that `FLASK_ENV=production` is set
- Review error logs in `logs/app.log`

