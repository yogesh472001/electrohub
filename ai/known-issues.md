# Known Issues, Risks & Technical Debt

This document records factual observations regarding current limitations, technical debt, and risks identified in the **YAMORA Retails** codebase.

---

### 1. Monolithic 1-Tier Architecture (Decoupling Needed for 2-Tier Goal)
- **Issue**: The current application is built as a single 1-tier monolithic Flask application where HTML rendering (`templates/`) and Python routes (`routes/`) reside in the same project directory.
- **Severity**: MEDIUM
- **Evidence**: `app.py`, `templates/`, `routes/`.
- **Affected Area**: Architecture, Deployment, Directory Layout.
- **Current Behavior**: Routes directly return rendered Jinja2 templates (`render_template(...)`).
- **Expected Behavior**: If refactored into a 2-tier architecture as requested by the user, the backend should expose JSON REST APIs (`jsonify(...)`) in a `backend/` folder, while the frontend UI resides in a separate `frontend/` folder.
- **Possible Impact**: Limits frontend framework flexibility (e.g. React/Vue/Svelte integration) until API decoupling is performed.
- **Status**: OPEN / PENDING USER DECOUPLING STEP.
- **Recommended Next Fix**: Design a RESTful API specification (`/api/v1/...`) and separate frontend assets into a standalone directory.

---

### 2. Default Fallback Secret Key in Configuration
- **Issue**: `config.py` contains a hardcoded default string for `SECRET_KEY`.
- **Severity**: MEDIUM (Security Risk)
- **Evidence**: `config.py:4`: `SECRET_KEY = os.environ.get('SECRET_KEY', 'yamora-retails-super-secret-key-2026')`.
- **Affected Area**: `config.py`, Session Management.
- **Current Behavior**: If `SECRET_KEY` is not provided in environment variables, the application defaults to a static fallback key.
- **Expected Behavior**: Enforce `SECRET_KEY` generation from environment variables in production environments.
- **Possible Impact**: Vulnerability to session tampering if deployed without setting `SECRET_KEY` in production.
- **Status**: OPEN.
- **Recommended Next Fix**: Raise an error or log a critical security warning when the fallback secret key is active in non-development modes.

---

### 3. Specifications Input Requires Raw JSON Text Formatting
- **Issue**: Technical specifications in `templates/admin/product_form.html` are entered via a single raw JSON `<textarea>`.
- **Severity**: LOW (Usability & Validation Technical Debt)
- **Evidence**: `templates/admin/product_form.html:47-49`, `routes/admin.py:124-129`.
- **Affected Area**: Admin Product Management (`routes/admin.py`).
- **Current Behavior**: If an admin enters invalid JSON syntax, it silently falls back to `{}` without giving an interactive validation message.
- **Expected Behavior**: Interactive key-value row builder for technical specifications.
- **Possible Impact**: Admin entry errors when adding product specifications.
- **Status**: OPEN.
- **Recommended Next Fix**: Replace raw JSON textarea with dynamic key-value input rows in `product_form.html`.

---

### 4. Local Filesystem Media Upload Storage
- **Issue**: Media uploads default to `static/uploads` on the local file system.
- **Severity**: LOW (Deployment Risk)
- **Evidence**: `config.py:25` (`UPLOAD_FOLDER`).
- **Affected Area**: `config.py`, Media Storage.
- **Current Behavior**: Product images rely on external HTTPS URLs or local static folder storage.
- **Expected Behavior**: Support for cloud object storage (AWS S3, Cloudinary, or Google Cloud Storage).
- **Possible Impact**: Local file uploads will be lost on ephemeral cloud platforms (Render, Heroku, AWS Fargate) upon container restart.
- **Status**: OPEN.
- **Recommended Next Fix**: Add a cloud storage service adapter for user-uploaded product thumbnails.

---

### 5. Simulated Payment Callback Gateway
- **Issue**: Payment gateway callbacks (`/cart/payment-callback/<order_id>`) do not perform cryptographic signature verification (HMAC).
- **Severity**: LOW (Integration Risk)
- **Evidence**: `routes/cart.py:218-232`.
- **Affected Area**: Payment Gateway Simulation.
- **Current Behavior**: Callback triggers order status update upon POST submission from the gateway page.
- **Expected Behavior**: Production payment gateways (PhonePe Merchant API / Razorpay) require webhook signature verification.
- **Possible Impact**: Acceptable for demo/simulation purposes; requires webhook verification if integrating live production PSP APIs.
- **Status**: OPEN (BY DESIGN FOR SIMULATION).
- **Recommended Next Fix**: Implement signature verification if connecting live PhonePe / Razorpay merchant API keys.
