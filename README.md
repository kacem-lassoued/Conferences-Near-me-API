# Conference Discovery & Research Indexing Platform

Welcome to the **Conference Discovery Platform API**! This project is a backend application that helps researchers find academic conferences, submit new ones, and view them on an interactive map.

This document serves as a guide to understanding the code, file structure, and how the different parts of the application work together.

---

## 📂 Project Structure Explained

Here is a breakdown of every file and folder in the project and what it does.

### Root Directory
These files are in the main folder:

- **`run.py`**: **The Entry Point**.
  - This is the file you run to start the application. 
  - It creates the app and tells it to listen on port 5000.
  - Think of it as the "Ignition Switch" for the car.

- **`config.py`**: **The Settings**.
  - Stores settings like database URLs, security keys, and environment options.
  - It uses "Classes" (DevelopmentConfig, ProductionConfig) to change settings easily depending on where the code is running.

- **`requirements.txt`**: **The Shopping List**.
  - Lists all the external libraries (packages) this project needs to work (like `flask`, `sqlalchemy`).
  - You install these with `pip install -r requirements.txt`.

- **`Dockerfile` & `docker-compose.yml`**: **The Instructions for Docker**.
  - These files tell Docker how to build a virtual container for this app so it runs the same on every computer.

- **`seed.py`**: **The Data Planter**.
  - A script that fills your empty database with sample data (users, conferences) so you have something to test with.

---

### `app/` Directory
This folder contains the actual logic of the application.

- **`__init__.py`**: **The Factory**.
  - This file makes the `app` folder a Python package.
  - It contains the `create_app()` function which sets up the Flask application, connects the database, runs the security plugins, and registers all the "Blueprints" (routes).

- **`extensions.py`**: **The Plugins**.
  - Initializes plugins like the Database (SQLAlchemy), Login Manager (JWT), and API Documentation (Swagger).
  - We keep them here to avoid "circular import" errors (app needs db, db needs app).

#### `app/routes/` Folder
"Routes" are the URLs that users can visit. Each file handles a specific category of features.

- **`auth.py`**: **The Bouncer**.
  - Handles User Registration (`/api/auth/register`) and Login (`/api/auth/login`).
  - Checks passwords and issues security "tokens" (JWTs).

- **`conferences.py`**: **The Librarian**.
  - Handles searching and viewing conferences (`/api/conferences`).
  - Can filter by keyword, country, year, or map location.

- **`submissions.py`**: **The Suggestion Box**.
  - Allows users to suggest new conferences or edits.
  - These go into a "Pending" state until an admin checks them.

- **`admin.py`**: **The Manager**.
  - Routes for Admins only.
  - Allows approving or rejecting the submissions from users.

- **`reference.py`**: **The Reference Book**.
  - Simple lists of data like "Rankings" or "Themes" that the frontend might need for dropdown menus.

#### `app/models/` Folder
"Models" are definitions of our Data. They tell the database what tables to create and what columns they have.

- **`user.py`**: Defines a `User` (email, password, role).
- **`conference.py`**: Defines a `Conference` (name, dates, location) and its relationships (Paper, Workshop).
- **`submission.py`**: Defines a `PendingSubmission` (changes waiting for approval).

---

## 🔄 How It All Works Together (The Plot)

Imagine this application like a restaurant. Here is how the "Staff" (Files) interact:

```mermaid
graph TD
    User((User)) -->|Requests URL| Run[run.py<br>(The Ignition)]
    Run -->|Starts| App[app/__init__.py<br>(The Factory)]
    
    App -->|Loads Settings| Config[config.py<br>(The Rules)]
    App -->|Connects| DB[(Database)]
    App -->|Registers| Routes[app/routes/<br>(The Waiters)]
    
    subgraph "Request Handling Flow"
        Routes -->|1. User asks for Data| Logic{Logic Check}
        Logic -->|2. Query Data| Models[app/models/<br>(The Recipes)]
        Models -->|3. Get from DB| DB
        Models -.->|4. Data Returned| Logic
        Logic -.->|5. JSON Response| User
    end
```

### Step-by-Step Flow:

1.  **Start (run.py)**: You turn the key. The app starts listening for requests.
2.  **Setup (app/__init__)**: The app hires the staff (routes) and opens the kitchen (database connection).
3.  **Request**: A user visits `/api/conferences`.
4.  **Route (app/routes/conferences.py)**: The "Waiter" takes the order.
5.  **Model (app/models/conference.py)**: The "Chef" looks up the recipe (SQL query) to find conferences in the Database.
6.  **Response**: The data is served back to the user as JSON (ingredients listed nicely).

---

## 🚀 How to Run It

1. **Install Docker** (if you haven't).
2. **Run logic**:
   Open a terminal in this folder and run:
   ```bash
   docker-compose up --build
   ```
   This will start the database and the web server.

3. **Check it works**:
   Open your browser to: [http://localhost:5000/](http://localhost:5000/)
   You should see a "Welcome" message.

4. **See Documentation**:
   Go to: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)
   You can see all available API endpoints and test them right in the browser!

---

## 🛠 Troubleshooting

- **404 Not Found at `/`**:
  - We added a "Welcome" page at the root `/`. If you see this error, ensure you check the URL.
  
- **Database Connection Errors**:
  - Ensure Docker is running. The app tries to connect to the postgres container named `db`.

happy coding!
