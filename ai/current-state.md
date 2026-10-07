# Current State Snapshot

This document provides a factual snapshot of the **YAMORA Retails** codebase state as of October 2026.

---

## 🎯 Project Purpose & Overview
**YAMORA Retails** is a modern e-commerce web platform tailored for an electronics and technology retail shop. It features an online storefront, interactive color variant photo/price swatches, shopping cart, checkout system with dedicated Indian online payment gateways (PhonePe, GPay, Paytm, Cards, Net Banking), customer order tracking, and a full-featured admin management dashboard.

---

## 🛠️ Technology Stack
- **Backend Framework**: Python 3.10+, Flask 3.1.3
- **ORM & Database**: Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.3
- **Database Engines**:
  - **MySQL / MariaDB** (via `PyMySQL` 1.2.3)
  - **SQLite** (local zero-config fallback `yamoraretails.db`)
- **Authentication & Security**: Flask-Login 0.6.3, Flask-Bcrypt 1.0.1
- **Frontend Stack**: HTML5, CSS3, JavaScript (ES6 Fetch API), Bootstrap 5.3.2, Bootstrap Icons 1.11.1
- **Version Control**: Git

---

## 📁 Directory Structure
```
electrohub/
├── ai/                     # Universal AI Project Brain Setup Documentation
│   ├── current-state.md
│   ├── decisions.md
│   ├── instructions.md
│   └── known-issues.md
├── app.py                  # Main Flask app factory, Blueprint registration & context processors
├── config.py               # Environment configuration (MySQL URI & SQLite fallback)
├── database.py             # Database seeder (creates default admin, customer & INR tech products)
├── schema.sql              # MySQL schema creation script
├── requirements.txt        # Python dependency manifest
├── README.md               # Project overview & execution documentation
├── .gitignore              # Git ignore rules for virtualenv, bytecode, sqlite db
├── models/
│   ├── __init__.py         # DB Extensions initialization (SQLAlchemy, LoginManager, Bcrypt)
│   ├── user.py             # User model with role-based access ('user' & 'admin')
│   ├── product.py          # Category, Product & ProductVariant models
│   ├── cart.py             # CartItem & WishlistItem models
│   └── order.py            # Order & OrderItem models
├── routes/
│   ├── __init__.py
│   ├── auth.py             # User Login, Registration & Logout routes
│   ├── shop.py             # Catalog, Filters, Search, Product Details, Wishlist
│   ├── cart.py             # Shopping Cart, Checkout, Order Placement & Gateway Redirection
│   ├── user.py             # User Profile, Order History & Visual Order Tracking Pipeline
│   └── admin.py            # Admin Dashboard, Product CRUD, Categories, Stock & Order Statuses
├── static/
│   ├── css/style.css       # Custom tech store styling, dark header, card elevation, tracking stepper
│   ├── js/main.js          # Interactive AJAX add-to-cart, toast alerts, qty buttons, wishlist
│   └── uploads/            # Media uploads storage
└── templates/
    ├── base.html           # Master layout template (navbar, topbar, search, footer)
    ├── 404.html & 500.html # Custom error pages
    ├── auth/               # Login & Register views
    ├── shop/               # Storefront, Catalog, Product Detail & Wishlist views
    ├── cart/               # Cart, Checkout & Dedicated Gateway views (`payment_gateway.html`)
    ├── user/               # Profile, Orders & Order Detail Tracking views
    └── admin/              # Admin layout, Dashboard, Products, Categories, Orders & Users views
```

---

## 🛢️ Database Structure
1. **`users`**: `id`, `full_name`, `email`, `password_hash`, `role` (`'user'`/`'admin'`), `phone`, `address`, `created_at`.
2. **`categories`**: `id`, `name`, `slug`, `description`, `image_url`, `created_at`.
3. **`products`**: `id`, `title`, `slug`, `brand`, `category_id`, `price` (INR ₹), `original_price`, `discount_percent`, `stock`, `rating`, `is_featured`, `is_active`, `thumbnail`, `description`, `specifications_json`, `created_at`.
4. **`product_variants`**: `id`, `product_id`, `color_name`, `color_code`, `image_url`, `price` (optional override in ₹), `stock`, `description`.
5. **`cart_items`**: `id`, `user_id`, `product_id`, `variant_id`, `selected_color`, `quantity`, `created_at`.
6. **`wishlist_items`**: `id`, `user_id`, `product_id`, `created_at`.
7. **`orders`**: `id`, `order_number`, `user_id`, `full_name`, `email`, `phone`, `shipping_address`, `city`, `zip_code`, `payment_method`, `total_amount` (INR ₹), `status` (`'Pending'`, `'Processing'`, `'Shipped'`, `'Delivered'`, `'Cancelled'`), `created_at`.
8. **`order_items`**: `id`, `order_id`, `product_id`, `product_name`, `selected_color`, `price`, `quantity`, `thumbnail`.

---

## 🔌 API & Route Structure

| Endpoint | Method | Access | Purpose |
|---|---|---|---|
| `/` | `GET` | Public | Storefront index (Hero, Flash sales, Featured products) |
| `/products` | `GET` | Public | Product catalog with Search, Category, Brand, Price Range (₹) & Sort |
| `/product/<slug>` | `GET` | Public | Detailed view with interactive Color Swatches & specifications |
| `/wishlist` | `GET` | User | View saved wishlist items |
| `/wishlist/toggle/<id>`| `POST` | User | AJAX toggle wishlist item |
| `/cart/` | `GET` | User | View shopping cart with 18% GST & Shipping calculations |
| `/cart/add/<id>` | `POST` | User | Add product/variant to cart |
| `/cart/checkout` | `GET` | User | Checkout page with dynamic payment selection UI |
| `/cart/place-order` | `POST` | User | Places order and redirects to dedicated Gateway |
| `/cart/payment-gateway/<gateway>/<order_id>` | `GET` | User | Dedicated Gateway UI (`phonepe`, `gpay`, `paytm`, `card`, `netbanking`) |
| `/cart/payment-callback/<order_id>` | `POST` | User | Authorizes payment, updates order status to `Processing`, deducts stock |
| `/user/orders` | `GET` | User | User order history list |
| `/user/order/<id>` | `GET` | User | Order details & 4-step status tracking pipeline |
| `/admin/dashboard` | `GET` | Admin | Store KPIs in ₹, low stock warnings ($\le 5$), recent orders |
| `/admin/products` | `GET` | Admin | Inventory table with active/featured toggles |
| `/admin/products/add` | `GET/POST` | Admin | Create product & color variants |
| `/admin/products/edit/<id>` | `GET/POST` | Admin | Edit product & color variants |
| `/admin/orders` | `GET` | Admin | View orders & update order status dropdown |

---

## 🏃 Run & Execution Instructions

```bash
# 1. Navigate to directory
cd /Users/yogeshthawari/.gemini/antigravity/scratch/electrohub

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run Flask App
python3 app.py
```
App runs locally on `http://127.0.0.1:5000`.
