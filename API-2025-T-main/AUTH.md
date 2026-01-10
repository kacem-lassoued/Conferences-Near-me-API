# Authentication (JWT)

This project includes a basic JWT-based authentication using `flask-jwt-extended`.

- Default credentials: `admin` / `password` (override with `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables)
- JWT secret: set `JWT_SECRET_KEY` environment variable to a strong secret in production.

Example (PowerShell) — obtain a token:

```powershell
$body = @{ username = 'admin'; password = 'password' } | ConvertTo-Json
$resp = Invoke-RestMethod -Uri http://localhost:5000/login -Method POST -Body $body -ContentType 'application/json'
$resp.access_token
```

Call the protected endpoint with the token (PowerShell):

```powershell
Invoke-RestMethod -Uri http://localhost:5000/protected -Method GET -Headers @{ Authorization = "Bearer $($resp.access_token)" }
```

Or using `curl` (bash):

```bash
# Login
curl -s -X POST http://localhost:5000/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"password"}'

# Use returned token
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:5000/protected
```

Replace `<ACCESS_TOKEN>` with the token value returned from `/login`.
