from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_smorest import abort

def role_required(*allowed_roles):
    """
    Decorator to check if user has required role.
    Students (no token) can access GET methods.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Allow students (no auth) onlsy for GET methods
            from flask import request
            if request.method == "GET":
                try:
                    verify_jwt_in_request(optional=True)
                except:
                    # No token provided - student access for GET is allowed
                    pass
                return fn(*args, **kwargs)
            
            # For non-GET methods, require authentication
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "student")
            
            if user_role not in allowed_roles:
                abort(403, message=f"Access denied. Required roles: {', '.join(allowed_roles)}")
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Decorator for admin-only access"""
    return role_required("admin")(fn)


def admin_or_chef_required(fn):
    """Decorator for admin or dept_chef access"""
    return role_required("admin", "dept_chef")(fn)