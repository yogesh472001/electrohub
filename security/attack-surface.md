# Attack Surface Mapping

This document maps all reachable attack surfaces, endpoints, authentication boundaries, and data entry vectors within the **ElectroHub** application.

---

## 1. Public Reachable Endpoints (Unauthenticated)

| Route Endpoint | HTTP Methods | Data Inputs / Parameters | Security Controls | Risk Level |
|---|---|---|---|---|
| `/` | `GET` | None | None (Public Homepage) | Low |
| `/products` | `GET` | `q`, `category`, `brand`, `min_price`, `max_price`, `sort` | Input sanitization via SQLAlchemy ORM | Low |
| `/product/<slug>` | `GET` | URL `slug` parameter | `first_or_404()` DB Lookup | Low |
| `/auth/login` | `GET`, `POST` | `email`, `password`, `remember` | Bcrypt password check | **MEDIUM** (No Rate Limit) |
| `/auth/register` | `GET`, `POST` | `full_name`, `email`, `phone`, `password`, `confirm_password` | Email uniqueness & password matching | **MEDIUM** (No Rate Limit) |

---

## 2. Authenticated Customer Endpoints

| Route Endpoint | HTTP Methods | Data Inputs | Security Controls | Risk Level |
|---|---|---|---|---|
| `/auth/logout` | `GET` | None | `@login_required`, `logout_user()` | Low |
| `/wishlist` | `GET` | None | `@login_required`, session filtering | Low |
| `/wishlist/toggle/<id>` | `POST` | URL `product_id` | `@login_required`, user_id check | Low |
| `/cart/` | `GET` | None | `@login_required`, user session | Low |
| `/cart/add/<id>` | `POST` | `quantity`, `variant_id` | `@login_required`, stock verification | Low |
| `/cart/update/<id>` | `POST` | `quantity` | `@login_required`, user cart ownership | Low |
| `/cart/remove/<id>` | `POST` | None | `@login_required`, user cart ownership | Low |
| `/cart/checkout` | `GET` | None | `@login_required`, cart empty check | Low |
| `/cart/place-order` | `POST` | `full_name`, `email`, `phone`, `shipping_address`, `city`, `zip_code`, `payment_method`, `upi_id` | `@login_required`, shipping field validation | Low |
| `/cart/payment-gateway/<gateway>/<id>` | `GET` | URL `gateway`, `order_id` | `@login_required`, order owner check | Low |
| `/cart/payment-callback/<id>` | `POST` | None | `@login_required`, order owner check | **MEDIUM** (Simulated Callback) |
| `/user/profile` | `GET`, `POST` | `full_name`, `phone`, `address`, `new_password`, `confirm_password` | `@login_required` | Low |
| `/user/orders` | `GET` | None | `@login_required`, `user_id` filtering | Low |
| `/user/order/<id>` | `GET` | URL `order_id` | `@login_required`, IDOR ownership check | Low |

---

## 3. Administrative Privileged Endpoints (`role == 'admin'`)

| Route Endpoint | HTTP Methods | Data Inputs | Security Controls | Risk Level |
|---|---|---|---|---|
| `/admin/dashboard` | `GET` | None | `@admin_required` decorator | Low |
| `/admin/products` | `GET` | None | `@admin_required` decorator | Low |
| `/admin/products/add` | `GET`, `POST` | `title`, `brand`, `category_id`, `price`, `original_price`, `discount_percent`, `stock`, `thumbnail`, `description`, `specifications_json`, `variant_*` | `@admin_required` decorator | Low |
| `/admin/products/edit/<id>` | `GET`, `POST` | Same as above | `@admin_required` decorator | Low |
| `/admin/products/delete/<id>` | `POST` | URL `product_id` | `@admin_required` decorator | Low |
| `/admin/categories` | `GET`, `POST` | `name`, `image_url`, `description` | `@admin_required` decorator | Low |
| `/admin/categories/delete/<id>` | `POST` | URL `cat_id` | `@admin_required` decorator | Low |
| `/admin/orders` | `GET` | None | `@admin_required` decorator | Low |
| `/admin/orders/update-status/<id>` | `POST` | `status` | `@admin_required` decorator | Low |
| `/admin/users` | `GET` | None | `@admin_required` decorator | Low |

---

## 4. Input Vectors & Validation Summary

1. **Text & Search Input**: Form inputs (`q`, `full_name`, `email`, `address`, `city`) sanitized through Jinja2 auto-escaping in templates and SQLAlchemy ORM parameter binding.
2. **Numeric & Price Input**: Inputs parsed via `float()` / `int()`.
3. **JSON Specifications**: Handled via `json.loads()` wrapped in `try/except`.
4. **Payment Parameters**: `payment_method` validated against gateway keys (`phonepe`, `gpay`, `paytm`, `card`, `netbanking`).
