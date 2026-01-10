# System Guidethrough & Architecture Documentation

This document provides a comprehensive explanation of the Conference Discovery System, specifically focusing on the newly integrated **H-Index Verification Engine**.

---

## 1. System Architecture

The project is built as a **Flask REST API** using a modular "Blueprint" structure. It connects to a **SQLite database** (via SQLAlchemy) and interacts with external services (**Semantic Scholar**) to validate academic metrics.

### Core Components
*   **Flask App**: The central web server.
*   **SQLAlchemy ORM**: Manages database interactions.
*   **Semantic Scholar Service**: A dedicated module (`services/scholar_service.py`) that acts as a bridge to external academic data.
*   **JWT Auth**: Handles admin authentication.

---

## 2. The "Immediate Fetch" Submission Workflow

The unique feature of this system is how it handles submissions. Unlike traditional systems that validate data later, this system enriches data **at the moment of submission**.

### Step-by-Step Data Flow

1.  **User Submission** (`POST /submissions`)
    *   An anonymous user sends a JSON payload containing conference details and a list of papers/authors.
    *   *Example Input*: `{"name": "AI Conf", "papers": [{"title": "My Paper", "authors": ["Andrew Ng"]}]}`

2.  **The Interception Layer**
    *   Before saving anything to the database, the `submission.py` resource intercepts the request.
    *   It iterates through every author name provided in the payload.

3.  **External Verification (The "Scholar Service")**
    *   For each author, the system calls `services.scholar_service.get_author_h_index(name)`.
    *   **Search**: It queries the Semantic Scholar API for an author matching the name.
    *   **Retrieval**: If found, it fetches the author's **ID**, **Affiliation**, and **H-Index**.
    *   **Caching**: To improve performance, successful lookups are cached in memory.

4.  **Enrichment**
    *   The system *injects* this fetched data back into the submission payload.
    *   It adds a new field `enriched_authors` to the paper object.
    *   *Resulting Data*: `{"name": "Andrew Ng", "h_index": 153, "semantic_scholar_id": "144388777"}`

5.  **Pending State**
    *   The system saves this *enriched* payload into the `pending_submissions` table.
    *   **Crucially**, the h-index is now frozen in this record. It is waiting for admin eyes.

---

## 3. Administrative Review & Persistence

1.  **Admin Review** (`GET /admin/pending`)
    *   The admin logs in and requests pending submissions.
    *   They see the conference details *plus* the h-indexes that were automatically fetched. This helps them judge the quality of the conference immediately.

2.  **Approval & Persistence** (`POST /admin/approve/<id>`)
    *   When the admin approves, the system moves data from "Pending" to "Permanent" tables.
    *   It reads the `enriched_authors` data directly from the pending payload.
    *   It creates:
        *   **Conference** record.
        *   **Paper** records (linked to Conference).
        *   **Author** records (linked to Papers).
    *   *Note*: If an author already exists in the DB (matched by name), the system reuses the existing record to prevent duplicates.

---

## 4. Database Models (The "Brain")

How the data is structured effectively:

### `Author` Model
*   **`id`**: Unique database ID.
*   **`name`**: Full name.
*   **`h_index`**: The academic impact score (integer).
*   **`semantic_scholar_id`**: The external ID used for reliable updates later.
*   **`affiliation`**: University or organization.
*   **`last_updated`**: Timestamp of when we last checked the h-index.

### `Paper` Model
*   **`id`**: Unique ID.
*   **`title`**: Paper title.
*   **`conference_id`**: Which conference this belongs to.
*   **`authors`**: A **Many-to-Many** relationship. One paper can have multiple authors, and one author can have multiple papers.

---

## 5. Technical Details & Scalability

### Semantic Scholar Integration
*   **API**: Uses the Graph API (`api.semanticscholar.org/graph/v1`).
*   **Rate Limits**: The service handles 429 (Too Many Requests) errors by waiting and retrying automatically.
*   **Accuracy**: It defaults to the top-ranked search result for a name.

### Author Search & Discovery
*   The system exposes a public endpoint `GET /authors` where anyone can view the roster of authors in the system, sorted by h-index.
*   This creates a "Hall of Fame" effect, highlighting the most influential researchers attending your conferences.

---

## 6. Directory Structure

*   `app.py`: Main entry point and configuration.
*   `models/`: Database definitions (`author.py`, `paper.py`, `submission.py`, `conference.py`).
*   `resources/`: API routes (`submission.py` handles the logic, `admin.py` handles approval).
*   `services/`: External integrations (`scholar_service.py`).
*   `schemas.py`: Data validation rules (Marshmallow).

---

This architecture ensures that **data quality is high from the start**. By validating metrics at the gate (submission time), the system reduces the workload on admins and ensures that the final database is populated with rich, verified academic data.
