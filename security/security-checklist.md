# Project-Specific Security Checklist & Findings

This document evaluates the **YAMORA Retails** codebase against standard security criteria using the strict finding format:
`Severity → Evidence → Risk → Affected location → Why it matters → Recommended fix`

---

## 1. Security Checklist Evaluation

### 🟢 Authentication
- [x] Passwords salted and hashed with `Bcrypt` (`set_password()` in `models/user.py`).
- [ ] **Finding**: `Medium` → `routes/auth.py:25-50` → Account brute-force attack vulnerability → `/auth/login` → No rate limiting exists on login attempts, permitting unlimited automated dictionary attacks → Add `Flask-Limiter` to restrict login attempts per IP/user.

### 🟢 Authorization & RBAC
- [x] Admin endpoints protected via `@admin_required` decorator (`routes/admin.py`).
- [x] User orders protected by `user_id` ownership checks (`routes/user.py:order_detail`).
- [x] Cart item operations scoped to `current_user.id` (`routes/cart.py`).

### 🔴 Session & Token Security
- [ ] **Finding**: `High` → `config.py:4` → Session cookie forgery risk → `config.py` → If deployed without setting environment variable `SECRET_KEY`, all instances share the hardcoded fallback key, enabling cookie forgery → Block application startup if default secret key is used in production.

### 🔴 XSS & CSRF Protection
- [x] Jinja2 template auto-escaping enabled by default (`{{ variable }}`).
- [ ] **Finding**: `Medium` → `templates/cart/checkout.html`, `templates/auth/login.html` → Cross-Site Request Forgery (CSRF) risk → All POST forms → Forms process `request.form` without validating a anti-CSRF token → Integrate `Flask-WTF` / `CSRFProtect(app)`.

### 🟢 Input Validation & Injection Prevention
- [x] SQL Injection mitigated via SQLAlchemy ORM parameterized queries (`Product.query.filter(...)`).
- [ ] **Finding**: `Low` → `routes/admin.py:124-129` → Unvalidated JSON input fallback → `routes/admin.py` → Invalid JSON in product specifications silently converts to `{}` without returning user feedback → Validate JSON syntax and return error feedback to admin.

### 🟢 Rate Limiting & Abuse Prevention
- [ ] **Finding**: `Medium` → `app.py`, `routes/auth.py` → API & form submission abuse → Public POST endpoints → Absence of rate limit allows automated spam registrations and brute force → Install and configure `Flask-Limiter`.

### 🟢 File Upload Security
- [x] `MAX_CONTENT_LENGTH` set to 16MB in `config.py`.
- [ ] **Finding**: `Low` → `config.py:25` → Local filesystem upload storage → `static/uploads/` → Ephemeral containers lose uploaded files upon restart → Integrate S3 / Cloudinary cloud storage adapter.

### 🟢 Secrets & Key Management
- [x] Database credentials loaded via environment variables (`MYSQL_PASSWORD`).
- [x] No plaintext passwords or private keys committed in Git history.

### 🟢 Logging & Error Handling
- [x] Generic, non-revealing error messages displayed to users via Flask `flash()`.
- [ ] **Finding**: `High` → `app.py:48` → Production debug exposure risk → `app.py` (`debug=True`) → Interactive Werkzeug debugger allows arbitrary code execution if exposed publicly → Set `debug=False` or load from environment variable.

---

## 2. Summary Categorization

### Confirmed Vulnerabilities
- None identified.

### Security Weaknesses & Missing Controls
1. **Missing Anti-CSRF Tokens on Forms**: `Medium` → `templates/**/*.html` → CSRF vulnerability → All HTML POST forms → Allows unauthorized state mutations → Implement `Flask-WTF`.
2. **Missing Rate Limiting on Login**: `Medium` → `routes/auth.py:login` → Brute-force risk → `/auth/login` → Allows password guessing → Implement `Flask-Limiter`.
3. **Hardcoded Fallback Secret Key**: `High` → `config.py:4` → Cookie forgery risk → `config.py` → Allows session spoofing if env var is missing → Enforce env var setting.
4. **Flask Debug Mode Active by Default**: `High` → `app.py:48` → Remote code execution risk → `app.py` → Debugger exposed on 0.0.0.0 → Set `debug=False` for production deployments.
