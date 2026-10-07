# Threat Model

This document outlines the threat model for the **YAMORA Retails E-Commerce** platform based on an empirical security analysis of the application architecture, authentication, authorization, and data flows.

---

## 1. Assets

| Asset | Sensitivity | Impact of Compromise |
|---|---|---|
| **User Credentials & Hash Records** | High | Password database exposure, account takeover. |
| **Customer PII & Shipping Addresses** | High | Privacy violation, customer identity exposure. |
| **Order History & Financial Totals** | Medium | Confidentiality breach of commercial sales data. |
| **Admin Privilege & Dashboard Access** | Critical | Full system control, inventory manipulation, user deletion. |
| **Product Inventory & Pricing Data** | Medium | Unauthorized price modification or stock exhaustion. |
| **Database Connection & Session Secret** | Critical | Session forgery, direct DB manipulation. |

---

## 2. Trust Boundaries

```
[ Unauthenticated Public User ]
       │  (HTTP / Web Browser)
       ▼
┌─────────────────────────────────────────────────────────┐
│ Trust Boundary 1: Web Application Entry Point           │
│ - Unauthenticated Public Routes (Catalog, Search, Auth) │
└──────────────────────────┬──────────────────────────────┘
                           │  (Flask-Login Session Cookie)
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Trust Boundary 2: Authenticated User Context            │
│ - Customer Routes (Cart, Wishlist, Profile, Orders)     │
└──────────────────────────┬──────────────────────────────┘
                           │  (Role Check: role == 'admin')
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Trust Boundary 3: Administrator Privilege Zone         │
│ - Admin Dashboard, Product CRUD, Order Statuses         │
└──────────────────────────┬──────────────────────────────┘
                           │  (PyMySQL / SQLite ORM)
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Database Storage Layer (MySQL / SQLite)                 │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Actors

1. **Anonymous Visitor**: Can browse products, filter catalog, view details, search items, and register/login.
2. **Authenticated Customer**: Can manage personal cart, wishlist, profile, shipping address, place orders, and track order pipeline.
3. **Store Administrator**: Possesses full administrative rights over products, stock, categories, orders, and customer accounts.
4. **Malicious Threat Actor**: Attempts unauthorized access, credential brute-forcing, CSRF, session forgery, or price manipulation.

---

## 4. Entry Points

- **Authentication Endpoints**: `/auth/login`, `/auth/register`, `/auth/logout`
- **Shop & Search Endpoints**: `/`, `/products`, `/product/<slug>`, `/wishlist`, `/wishlist/toggle/<product_id>`
- **Cart & Checkout Endpoints**: `/cart/`, `/cart/add/<product_id>`, `/cart/update/<item_id>`, `/cart/remove/<item_id>`, `/cart/checkout`, `/cart/place-order`, `/cart/payment-gateway/<gateway>/<order_id>`, `/cart/payment-callback/<order_id>`
- **User Profile & Order Endpoints**: `/user/profile`, `/user/orders`, `/user/order/<order_id>`
- **Admin Endpoints**: `/admin/dashboard`, `/admin/products`, `/admin/products/add`, `/admin/products/edit/<id>`, `/admin/products/delete/<id>`, `/admin/categories`, `/admin/categories/delete/<id>`, `/admin/orders`, `/admin/orders/update-status/<id>`, `/admin/users`

---

## 5. Threats & Attack Scenarios

### Scenario A: Credential Brute-Force on Login Endpoint
- **Threat**: Attacker sends repeated automated POST requests to `/auth/login`.
- **Likelihood**: High
- **Impact**: High (Account Takeover)
- **Risk Severity**: **HIGH**
- **Existing Mitigations**: Bcrypt password verification (`check_password()`).
- **Missing Mitigations**: No rate limiting (e.g., `Flask-Limiter`) or CAPTCHA on `/auth/login`.

### Scenario B: Cross-Site Request Forgery (CSRF) on Cart & Order Actions
- **Threat**: Attacker tricks authenticated user into submitting state-changing POST forms (e.g. adding items, updating profile, placing orders).
- **Likelihood**: Medium
- **Impact**: Medium (Unauthorized state mutation)
- **Risk Severity**: **MEDIUM**
- **Existing Mitigations**: Session-based auth via Flask-Login.
- **Missing Mitigations**: Forms process `request.form` directly without Flask-WTF CSRF tokens.

### Scenario C: Session Cookie Forgery via Static Secret Key Fallback
- **Threat**: If `SECRET_KEY` environment variable is not supplied, application falls back to a static default key string in `config.py`. Attacker uses known fallback key to forge signed session cookies.
- **Likelihood**: Medium (depends on deployment config)
- **Impact**: Critical (Full Session & Identity Spoofing)
- **Risk Severity**: **HIGH**
- **Existing Mitigations**: Environment variable override supported (`os.environ.get('SECRET_KEY')`).
- **Missing Mitigations**: System does not block execution when running on fallback default key.

### Scenario D: Direct Object Reference (IDOR) Attempt on User Orders
- **Threat**: Authenticated customer attempts to view or modify another user's order by altering `order_id` in URL `/user/order/<order_id>`.
- **Likelihood**: Low
- **Impact**: High (Privacy Breach)
- **Risk Severity**: **LOW (Mitigated)**
- **Existing Mitigations**: Route explicitly queries `Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()`, restricting access to the owner only.
- **Missing Mitigations**: None (Properly Mitigated).

---

## 6. Summary of Mitigations

| Threat Category | Existing Mitigations | Missing / Recommended Mitigations |
|---|---|---|
| **SQL Injection** | SQLAlchemy ORM parameterized queries used across all models & routes | None required |
| **Authentication Security** | Flask-Bcrypt password hashing, Flask-Login user loader | Rate limiting on auth routes (`Flask-Limiter`) |
| **Authorization / RBAC** | `@admin_required` decorator checks `current_user.is_admin()`, owner checks on user orders | Enforce RBAC checks on API callback endpoints |
| **CSRF Protection** | Browser SameSite cookie default | Enable explicit Flask-WTF CSRF tokens on all POST forms |
| **Session Security** | HTTP session signing via `SECRET_KEY` | Enforce non-default `SECRET_KEY` in non-debug mode |
