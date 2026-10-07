# Secrets Management & Exposure Assessment

This document details the handling, risks, exposure vectors, and findings regarding secrets, credentials, and keys within the **ElectroHub** codebase.

---

## 1. Secrets Inventory & Expected Locations

| Secret Type | Expected Storage Location | Current Handling Mechanism | Risk Assessment |
|---|---|---|---|
| **Flask Secret Key** | Environment Variable (`SECRET_KEY`) | Loaded via `os.environ.get('SECRET_KEY')` with static fallback | **MEDIUM** (Static fallback in code) |
| **MySQL User Password** | Environment Variable (`MYSQL_PASSWORD`) | Loaded via `os.environ.get('MYSQL_PASSWORD')` with default `'password'` | **LOW** (Standard dev default) |
| **Database URI** | Environment Variable (`DATABASE_URL`) | Evaluated in `config.py:14-22` | **LOW** (Safe env retrieval) |
| **User Account Passwords** | Database Storage (`users.password_hash`) | Bcrypt salted & hashed via `Flask-Bcrypt` | **SAFE** (Hashed, no plaintext stored) |

---

## 2. Configuration Analysis (`config.py`)

- **File Location**: `config.py`
- **Code Inspection**:
  ```python
  class Config:
      SECRET_KEY = os.environ.get('SECRET_KEY', 'electrohub-super-secret-key-tech-2026')
      MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
      MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
      ...
  ```
- **Finding**:
  - The application provides a default fallback string for `SECRET_KEY` if the environment variable is not defined.
  - While convenient for local development, if deployed to production without configuring `SECRET_KEY` in system environment variables, all instances share the same session signing key.

---

## 3. Client-Side Exposure Risk

- **Templates Inspection (`templates/`)**:
  - All templates were audited to ensure no database credentials, internal server keys, or private API keys are injected into HTML output or inline scripts.
  - **Result**: **NO** server secrets or API keys are exposed in client-side HTML/JS templates.

- **JavaScript Inspection (`static/js/main.js`)**:
  - Main client script handles AJAX Fetch calls (`/cart/add/<id>`, `/wishlist/toggle/<id>`) using relative paths and standard `XMLHttpRequest` headers.
  - **Result**: **NO** hardcoded secrets or tokens present in static JavaScript files.

---

## 4. Git Repository & History Exposure Assessment

- **`.gitignore` Audit**:
  - File `.gitignore` properly excludes:
    - Environment files (`.env`, `.env.local`)
    - Virtual environment directories (`venv/`, `env/`)
    - Local SQLite database files (`*.db`, `*.sqlite3`)
    - Python bytecode (`__pycache__/`, `*.pyc`)
- **Git Commit Log Inspection**:
  - Audited full commit history (`git log -p`).
  - **Result**: **NO** real production credentials, private SSL keys, cloud API tokens, or production database passwords exist in the Git commit history.

---

## 5. Logging & Error Handling Exposure

- **Debug Mode**:
  - In `app.py:48`: `app.run(debug=True, host='0.0.0.0', port=5000)`.
  - **Risk**: Flask's built-in Werkzeug debug mode displays interactive tracebacks upon unhandled exceptions. If exposed to public networks in production, interactive debugging allows arbitrary code execution.
  - **Mitigation Requirement**: Debug mode must be disabled (`debug=False`) when deploying to production environments.

- **Flash Error Messages**:
  - Form validation error messages in `routes/auth.py` and `routes/cart.py` use generic user-friendly text (e.g. `"Invalid email or password"`, `"Please fill in all required shipping details"`).
  - **Result**: User error messages do not leak internal database tracebacks or system paths to end users.

---

## 6. Secret Rotation Requirements

1. **Flask Secret Key Rotation**:
   - If `SECRET_KEY` is changed or rotated in environment variables, existing active user session cookies will be invalidated, requiring users to log in again.
2. **Database Password Rotation**:
   - MySQL database password changes require updating the `MYSQL_PASSWORD` environment variable in deployment settings without requiring application code changes.
