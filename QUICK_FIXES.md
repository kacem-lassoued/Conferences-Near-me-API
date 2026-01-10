# Quick Fixes Guide

## Critical Fixes to Apply Immediately

### 1. Fix Dockerfile Entry Point
✅ **FIXED** - Changed `run.py` to `app.py` in Dockerfile

### 2. Create Environment Variables File
✅ **CREATED** - Added `.env.example` file

### 3. Fix Admin Authentication (URGENT)

**Current Issue:** Hardcoded credentials in `resources/auth.py`

**Fix:**
1. Create a User model (if not exists)
2. Use password hashing
3. Store credentials in environment variables or database

**Quick Fix (Temporary):**
```python
# resources/auth.py - TEMPORARY FIX
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Store hashed password (run once to generate)
# hash = generate_password_hash("your-secure-password")
# Store in environment variable: ADMIN_PASSWORD_HASH

@blp.route("/login")
class Login(MethodView):
    @blp.arguments(AuthSchema)
    def post(self, user_data):
        email = user_data.get("email")
        password = user_data.get("password")
        
        # Get from environment
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        admin_password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
        
        if not admin_password_hash:
            # First time setup - generate hash
            return {"error": "Admin password not configured"}, 500
        
        if email == admin_email and check_password_hash(admin_password_hash, password):
            access_token = create_access_token(
                identity="admin",
                additional_claims={"role": "admin"}
            )
            return {"access_token": access_token}
        
        return {"message": "Invalid credentials"}, 401
```

### 4. Disable Debug Mode in Production

**Fix in app.py:**
```python
# app.py - Line 76
if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
```

### 5. Enforce JWT Secret Key

**Fix in app.py:**
```python
# app.py - Line 31
jwt_secret = os.environ.get("JWT_SECRET_KEY")
if not jwt_secret:
    if os.environ.get("FLASK_ENV") == "production":
        raise ValueError("JWT_SECRET_KEY must be set in production")
    jwt_secret = "dev-secret-change-in-production"
app.config["JWT_SECRET_KEY"] = jwt_secret
```

### 6. Add Pagination Metadata

**Fix in resources/conference.py:**
```python
# resources/conference.py - Line 43-45
pagination = query.paginate(page=page, per_page=per_page, error_out=False)

return {
    "items": pagination.items,
    "pagination": {
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
}
```

### 7. Fix Schema Naming Conflicts

**Fix in schemas.py:**
```python
# schemas.py - Add explicit names
class PaperSchema(Schema):
    class Meta:
        schema_name = "PaperResponse"  # Explicit name
    
class AuthorSchema(Schema):
    class Meta:
        schema_name = "AuthorResponse"  # Explicit name
```

### 8. Add Database Indexes

**Fix in models:**
```python
# models/conference.py
class Conference(db.Model):
    # ... existing fields ...
    
    # Add indexes
    __table_args__ = (
        db.Index('idx_conference_name', 'name'),
        db.Index('idx_conference_country', 'country'),
        db.Index('idx_conference_start_date', 'start_date'),
    )
```

### 9. Add Logging

**Add to app.py:**
```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Conference Discovery API startup')
```

### 10. Add Health Check Endpoint

**Add to app.py:**
```python
@app.route("/health")
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity
        db.session.execute(db.text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }, 200
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, 503
```

## Next Steps

1. ✅ Apply Dockerfile fix
2. ✅ Create .env.example
3. ⚠️ Fix authentication (URGENT)
4. ⚠️ Disable debug mode
5. ⚠️ Add logging
6. ⚠️ Add health check
7. ⚠️ Fix pagination
8. ⚠️ Add database indexes
9. ⚠️ Implement tests
10. ⚠️ Add rate limiting


