# Conference Discovery API - Usage Guide

## Quick Start

**Base URL**: `http://localhost:5000`  
**Documentation**: `http://localhost:5000/swagger-ui/`

---

## Authentication

### Login (Get Admin Token)
**Endpoint**: `POST /login`

**Request Body**:
```json
{
  "email": "example@gmail.com",
  "password": "password"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Usage**: Include token in subsequent requests:
```
Authorization: Bearer <access_token>
```

---

## Public Endpoints (No Auth Required)

### 1. List Conferences
**Endpoint**: `GET /conferences`

**Query Parameters**:
- `q` (optional): Search by name or acronym
- `country` (optional): Filter by country
- `sort_by` (optional): Sort by `name`, `created_at`, or `start_date`
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Example Request**:
```
GET /conferences?q=AI&country=France&sort_by=name&page=1&per_page=10
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "International Conference on AI",
    "organizers": "IEEE, ACM",
    "location": "https://maps.google.com/?q=Paris,France",
    "featured_papers": ["Deep Learning Advances", "Neural Networks"],
    "featured_workshops": "Workshop on Machine Learning",
    "status": "scheduled",
    "created_at": "2025-12-31T10:00:00"
  }
]
```

### 2. Get Conference Details
**Endpoint**: `GET /conferences/<id>`

**Example**: `GET /conferences/1`

**Response**: Same structure as list item above

### 3. Submit Conference
**Endpoint**: `POST /submissions`

**Request Body** (all fields required):
```json
{
  "name": "International AI Conference 2025",
  "organizers": "IEEE Computer Society, ACM SIGAI",
  "location": "https://maps.google.com/?q=Paris,France",
  "papers": [
    {
      "title": "Advances in Deep Learning",
      "authors": ["Geoffrey Hinton", "LeCun"]
    },
    {
      "title": "Neural Network Architectures", 
      "authors": ["Bengio"]
    }
  ],
  "featured_workshops": "Workshop on Ethical AI"
}
```

**Response**:
```json
{
  "name": "International AI Conference 2025",
  "organizers": "IEEE Computer Society, ACM SIGAI",
  "location": "https://maps.google.com/?q=Paris,France",
  "papers": [
    {
      "title": "Advances in Deep Learning",
      "authors": ["Geoffrey Hinton", "LeCun"]
    },
    {
      "title": "Neural Network Architectures",
      "authors": ["Bengio"]
    }
  ],
  "featured_workshops": "Workshop on Ethical AI"
}
```

**Status**: 201 Created

---

## Admin Endpoints (Auth Required)

### 4. View Submissions
**Endpoint**: `GET /admin/submissions?status=<status>`

**Query Parameters**:
- `status` (optional): `pending`, `approved`, or `rejected` (default: pending)

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
[
  {
    "id": 1,
    "type": "new_conference",
    "payload": {
      "name": "...",
      "organizers": "...",
      "location": "...",
      "featured_papers": [...],
      "featured_workshops": "..."
    },
    "status": "pending",
    "submitted_at": "2025-12-31T10:00:00"
  }
]
```

### 5. Approve Submission
**Endpoint**: `POST /admin/approve`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (Required):
```json
{
  "submission_id": 1
}
```

**Response**:
```json
{
  "message": "Conference created with papers and authors",
  "conference_id": 1,
  "authors_processed": [
    {
      "name": "Geoffrey Hinton",
      "h_index": 178
    }
  ]
}
```

### 6. Reject Submission
**Endpoint**: `POST /admin/reject`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (Required):
```json
{
  "submission_id": 2
}
```

**Response**:
```json
{
  "message": "Submission rejected",
  "id": 2
}
```

### 7. Update Conference
**Endpoint**: `PUT /admin/conferences/<conference_id>`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (all fields optional):
```json
{
  "name": "Updated Conference Name",
  "description": "New description",
  "organizers": "Updated organizers",
  "location": "https://maps.google.com/?q=Berlin,Germany",
  "featured_papers": ["New Paper 1", "New Paper 2"],
  "featured_workshops": "Updated workshops"
}
```

**Response**: Updated conference object

### 8. Delete Conference
**Endpoint**: `DELETE /admin/conferences/<conference_id>`

**Headers**: `Authorization: Bearer <token>`

**Example**: `DELETE /admin/conferences/5`

**Response**:
```json
{
  "message": "Conference deleted",
  "id": 5
}
```

---

## Author Endpoints (H-Index Integration)

These endpoints allow viewing authors, their papers, and their h-indices fetched from Semantic Scholar.

### 9. List All Authors
**Endpoint**: `GET /authors`

Returns all authors sorted by h-index (descending).

**Response**:
```json
[
  {
    "id": 1,
    "name": "Geoffrey Hinton",
    "h_index": 178,
    "affiliation": "University of Toronto",
    "last_updated": "2025-12-31T10:00:00"
  },
  ...
]
```

### 10. Get Author Details
**Endpoint**: `GET /authors/<id>`

**Response**: Same as list item above.

### 11. Search Authors
**Endpoint**: `GET /authors/search?name=<query>`

**Query Parameters**:
- `name` (required): Name to search for

**Response**: List of matching authors.

### 12. Get Author Papers
**Endpoint**: `GET /authors/<id>/papers`

Returns all papers associated with the author.

**Response**:
```json
{
  "author": { ... },
  "papers": [
    {
      "id": 15,
      "title": "Deep Learning Fundamentals",
      "conference_name": "ICML 2025"
    }
  ],
  "total_papers": 1
}
```

### 13. Refresh H-Index (Admin Only)
**Endpoint**: `POST /authors/<id>/refresh`

Manually trigger a re-fetch of the author's h-index from Semantic Scholar.

**Headers**: `Authorization: Bearer <token>`

---

## Complete Workflow Example

### Scenario: User submits conference → Admin approves

**Step 1**: User submits conference (no auth)
```bash
curl -X POST http://localhost:5000/submissions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Summit 2025",
    "organizers": "Tech Corp",
    "location": "https://maps.google.com/?q=London,UK",
    "featured_papers": ["AI Ethics"],
    "featured_workshops": "Future of AI"
  }'
```

**Step 2**: Admin logs in
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "example@gmail.com",
    "password": "password"
  }'
```

**Step 3**: Admin views pending submissions
```bash
curl -X GET http://localhost:5000/admin/submissions?status=pending \
  -H "Authorization: Bearer <token>"
```

**Step 4**: Admin approves submission (creates conference)
```bash
curl -X POST http://localhost:5000/admin/approve/1 \
  -H "Authorization: Bearer <token>"
```

**Step 5**: Public can now view the conference
```bash
curl -X GET http://localhost:5000/conferences
```

---

## Error Responses

### 400 Bad Request
```json
{
  "message": "Validation error",
  "errors": {
    "name": ["Field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "message": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
  "message": "Admin required"
}
```

### 404 Not Found
```json
{
  "code": 404,
  "status": "Not Found"
}
```

---

## Data Validation Rules

### Submission Schema
- `name`: Required, 1-200 characters
- `organizers`: Required, any length
- `location`: Required, 1-500 characters (Google Maps URL recommended)
- `featured_papers`: Required, array of strings
- `featured_workshops`: Required, any length

### Auth Schema
- `email`: Required, valid email format
- `password`: Required, minimum 1 character

### Conference Query
- `sort_by`: Must be one of: `name`, `created_at`, `start_date`
- `page`: Minimum 1
- `per_page`: Between 1 and 100

---

## Tips

1. **Testing**: Use Swagger UI at `/swagger-ui/` for interactive testing
2. **Pagination**: Always use pagination for large datasets
3. **Location Format**: Use Google Maps URLs for consistency
4. **Token Expiry**: JWT tokens expire after a set time (re-login if needed)
5. **Status Codes**: 
   - 200: Success
   - 201: Created
   - 400: Bad request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not found
