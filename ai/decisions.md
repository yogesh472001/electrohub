# Chronological Record of Technical Decisions

This document records the architectural and technical decisions present in the **YAMORA Retails** codebase.

---

### Decision 1: Flask SSR & Blueprint-Based Monolithic Architecture
- **Decision**: Build the application as a Flask Server-Side Rendered (SSR) monolith using Flask Blueprints and Jinja2 templates.
- **Reason (Inferred)**: Enables rapid development of user auth, product catalogue, shopping cart, admin management, and session handling without needing a separate frontend build pipeline.
- **Current Implementation**: Blueprints registered in `app.py`: `auth_bp`, `shop_bp`, `cart_bp`, `user_bp`, `admin_bp`.
- **Files Affected**: `app.py`, `routes/*.py`, `templates/**/*.html`.
- **Known Trade-Offs**: Tightly couples frontend HTML rendering with backend Flask route handlers. Separating into API + SPA requires decoupling.
- **Evidence**: Initial commit `2e7ba8e`, `app.py:19-27`.
- **Verification**: VERIFIED in codebase.

---

### Decision 2: Dual Database Strategy (MySQL Primary with SQLite Fallback)
- **Decision**: Configure PyMySQL connection string for MySQL/MariaDB while falling back to a local SQLite database (`yamoraretails.db`) when environment flag `USE_MYSQL` is false.
- **Reason (Verified)**: Allows zero-friction local execution without requiring a running MySQL server, while retaining 100% production MySQL database compatibility.
- **Current Implementation**: `config.py` inspects `os.environ.get('USE_MYSQL')`.
- **Files Affected**: `config.py`, `schema.sql`, `database.py`.
- **Known Trade-Offs**: Requires keeping raw `schema.sql` synchronized with SQLAlchemy ORM definitions manually.
- **Evidence**: Commit `2e7ba8e`, `config.py:14-22`, `schema.sql`.
- **Verification**: VERIFIED in codebase.

---

### Decision 3: Product Color Variants & Dynamic Pricing Schema
- **Decision**: Create a dedicated `ProductVariant` model and `product_variants` database table linked to `Product`.
- **Reason (Verified)**: Real-world flagship technology products (e.g. iPhone, MacBook Pro) feature different color finishes, custom variant images, individual stock levels, and price variations.
- **Current Implementation**: `ProductVariant` model defined in `models/product.py` with `effective_price` property; interactive color swatches in `templates/shop/product_detail.html`.
- **Files Affected**: `models/product.py`, `routes/admin.py`, `templates/admin/product_form.html`, `templates/shop/product_detail.html`, `database.py`.
- **Known Trade-Offs**: Admin form requires multi-field list handling (`request.form.getlist`).
- **Evidence**: Commit `be5e121`, `models/product.py:63-82`.
- **Verification**: VERIFIED in codebase.

---

### Decision 4: Dedicated Multi-Gateway Online Payment Redirection Workflow
- **Decision**: Remove Cash on Delivery (COD) and implement dedicated redirection endpoints `/cart/payment-gateway/<gateway>/<order_id>` for PhonePe, GPay, Paytm, Cards, and Net Banking.
- **Reason (Verified)**: Simulates realistic online payment gateway authorization flows for Indian e-commerce checkout.
- **Current Implementation**: `routes/cart.py` evaluates selected `payment_method`, routes to dedicated gateway view, and processes stock deduction upon callback (`/cart/payment-callback/<order_id>`).
- **Files Affected**: `routes/cart.py`, `templates/cart/checkout.html`, `templates/cart/payment_gateway.html`.
- **Known Trade-Offs**: Payment gateways are currently simulated in-app rather than integrating live third-party PSP SDKs (e.g. Razorpay / PhonePe Merchant API).
- **Evidence**: Commits `7464ae5`, `1f854a4`, `2911ef8`, `fd2b750`, `routes/cart.py:202-231`.
- **Verification**: VERIFIED in codebase.

---

### Decision 5: Indian Rupee (₹) Currency Standard & 18% GST Rate
- **Decision**: Standardize all product pricing, cart subtotal calculations, taxes (18% GST), and shipping rules (₹999 free shipping threshold) to Indian Rupees (₹).
- **Reason (Verified)**: User explicitly requested Indian currency formatting and regional payment methods (GPay, PhonePe, Paytm).
- **Current Implementation**: All Jinja2 templates format values using `₹{{ "%.2f"|format(...) }}`; `database.py` stores realistic INR prices.
- **Files Affected**: `database.py`, `routes/cart.py`, all `templates/**/*.html`.
- **Evidence**: Commit `1f854a4`, `database.py:65-175`.
- **Verification**: VERIFIED in codebase.
