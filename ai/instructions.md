# AI Agent Working Instructions & Project Constraints

This document defines the strict rules, architectural constraints, and development guidelines for AI agents working on the **ElectroHub E-Commerce** project.

---

## 🚨 Critical Project Rules

1. **Preserve Database Compatibility**:
   - Maintain compatibility for both **MySQL** (`mysql+pymysql://`) and **SQLite** fallback (`sqlite:///electrohub.db`).
   - Any schema modifications to SQLAlchemy models in `models/` **MUST** also be updated in `schema.sql`.

2. **Role-Based Authorization Enforcement**:
   - Every administrative route under `/admin` **MUST** be protected with `@admin_required`.
   - Every user cart, profile, checkout, and order route **MUST** be protected with `@login_required`.

3. **Currency & Locale Standard**:
   - The primary currency across the application is **Indian Rupees (₹)**.
   - All price formatting must use `₹{{ "%.2f"|format(price) }}` format.
   - Tax rate is standardized at **18% GST**. Free Express Shipping threshold is **₹999.00**.

4. **Online Payment Gateway Flow**:
   - Order placement redirects customers to dedicated gateway endpoints under `/cart/payment-gateway/<gateway>/<order_id>`.
   - Supported gateway keys: `phonepe`, `gpay`, `paytm`, `card`, `netbanking`.
   - Payment confirmation callback occurs at `/cart/payment-callback/<order_id>`.

5. **2-Tier Architecture Refactoring Caution**:
   - The user has expressed intent to decouple the project into a **2-tier architecture** (separate `frontend/` folder and `backend/` folder with database connection).
   - **DO NOT** execute structural directory splitting without explicit user instruction and architectural confirmation.

---

## 📁 Key Components & High-Caution Modules

| Module / File | Description | Caution Level | Reason |
|---|---|---|---|
| `app.py` | Flask App Factory & Global Context Processors | **HIGH** | Injects global `cart_count` and `wishlist_count` into Jinja context. |
| `config.py` | Environment & DB Connection Switching | **HIGH** | Controls MySQL / SQLite fallback logic based on `USE_MYSQL`. |
| `models/product.py` | `Product`, `Category`, `ProductVariant` | **HIGH** | Handles dynamic JSON specs and variant pricing overrides. |
| `routes/admin.py` | Admin Management & Stock CRUD | **HIGH** | Role verification & stock modification logic. |
| `routes/cart.py` | Cart & Multi-Gateway Order Redirection | **CRITICAL** | Calculates totals, deducts stock, processes payment callbacks. |
| `database.py` | Database Seeder | **MEDIUM** | Auto-seeds default admin/customer accounts and initial tech catalog. |

---

## 🧪 Testing & Validation Expectations

Before declaring any feature complete or committing code:

1. **App Context Verification**:
   Run a test script using Python `test_client()` to verify HTTP 200 responses on key routes:
   ```bash
   source venv/bin/activate
   python3 -c "from app import app; client = app.test_client(); print(client.get('/').status_code)"
   ```
2. **Git Commit Discipline**:
   Commit logical atomic changes with descriptive commit messages following project history style.

---

## 🔒 Security & Data Protection

- **Password Hashing**: Use `Bcrypt` (`set_password()` and `check_password()`). Never store raw text passwords.
- **SQL Injection Safety**: Always use SQLAlchemy ORM queries or parameterized execution. Never concatenate strings into raw SQL queries.
- **Secret Keys**: Never hardcode production secret keys; rely on `os.environ.get('SECRET_KEY')`.
