# ⚡ YAMORA Retails - Modern Electronics & Tech E-Commerce Store

YAMORA Retails is a feature-packed, professional e-commerce web application built for an electronics and technology retail shop. 

Built with **Python Flask**, **MySQL** (with SQLite fallback), **SQLAlchemy**, **HTML5**, **CSS3**, **JavaScript (ES6)**, and **Bootstrap 5**.

---

## 🔥 Key Features

### 🛒 Customer Storefront
- **Modern Tech UI**: Dark navy header, neon blue accents, responsive cards, micro-interactions, and toast alerts.
- **Dynamic Search & Filtering**: Filter products by Category, Brand, Price Range, and Keyword Search with multi-criteria sorting (Price, Rating, Newest).
- **Product Specifications**: Rich product details with technical specification tables, rating indicators, real-time stock badges, and category-based recommendations.
- **Wishlist & Cart**: Interactive wishlist toggle and shopping cart with free-shipping threshold progress bar.
- **Checkout & Order Processing**: Multi-step checkout with address validation, payment selection (Card, PayPal, COD), and order placement.
- **Live Order Tracking**: Visual 4-step order status pipeline (`Pending` ➔ `Processing` ➔ `Shipped` ➔ `Delivered`).

### ⚙️ Administrator Dashboard
- **Store KPIs**: Real-time sales revenue, total order count, active products count, and customer metrics.
- **Inventory & Low Stock Alerts**: Automatic alert banner for items with stock $\le 5$.
- **Product CRUD**: Full add/edit/delete product functionality with custom JSON specification parser and homepage featured toggles.
- **Category & Order Management**: Real-time status updater dropdown for orders and full category CRUD.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
- **Database**: MySQL / MariaDB (via PyMySQL) with SQLite automatic fallback
- **Frontend**: HTML5, CSS3, JavaScript (Fetch API / Async), Bootstrap 5, Bootstrap Icons

---

## 🚀 Quick Start Guide

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/electrohub.git
cd electrohub
```

### 2. Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup

#### Option A: SQLite (Immediate Execution)
Simply run the app! SQLite database `yamoraretails.db` will be automatically created and populated with demo products and accounts.

#### Option B: MySQL Setup
1. Create the MySQL database:
```sql
CREATE DATABASE yamoraretails_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
2. Import `schema.sql`:
```bash
mysql -u root -p yamoraretails_db < schema.sql
```
3. Set environment variables:
```bash
export USE_MYSQL=true
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_DB=yamoraretails_db
```

### 4. Run the Application
```bash
python3 app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🔐 Demo Account Credentials

| Role | Email | Password |
|---|---|---|
| **Customer** | `customer@yamoraretails.com` | `customer123` |
| **Admin** | `admin@yamoraretails.com` | `admin123` |

---

## 📄 License
This project is open-source under the MIT License.
