from functools import wraps
import json
import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.product import Category, Product, ProductVariant
from models.order import Order

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access denied. Administrator privilege required.', 'danger')
            return redirect(url_for('shop.index'))
        return f(*args, **kwargs)
    return decorated_function

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

def save_uploaded_file(file_obj):
    """Saves an uploaded image file securely to static/uploads/products/ and returns its web URL path."""
    if not file_obj or not getattr(file_obj, 'filename', None):
        return None
    
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
    os.makedirs(upload_dir, exist_ok=True)
    
    raw_filename = secure_filename(file_obj.filename)
    if not raw_filename:
        raw_filename = "product_image.jpg"
        
    unique_filename = f"{uuid.uuid4().hex[:8]}_{raw_filename}"
    filepath = os.path.join(upload_dir, unique_filename)
    file_obj.save(filepath)
    return f"/static/uploads/products/{unique_filename}"

def process_variants(product, form, files):
    """Saves or updates color variants and uploaded photo gallery files for a product."""
    ProductVariant.query.filter_by(product_id=product.id).delete()

    color_names = form.getlist('variant_color_name')
    color_codes = form.getlist('variant_color_code')
    image_urls = form.getlist('variant_image_url')
    prices = form.getlist('variant_price')
    stocks = form.getlist('variant_stock')
    descriptions = form.getlist('variant_description')

    variant_files = files.getlist('variant_image_file')

    for i in range(len(color_names)):
        c_name = color_names[i].strip()
        if not c_name:
            continue

        c_code = color_codes[i].strip() if i < len(color_codes) and color_codes[i].strip() else '#333333'

        # Check if an uploaded file is provided for this variant
        uploaded_variant_url = None
        if i < len(variant_files):
            uploaded_variant_url = save_uploaded_file(variant_files[i])

        if uploaded_variant_url:
            img_url = uploaded_variant_url
        elif i < len(image_urls) and image_urls[i].strip():
            img_url = image_urls[i].strip()
        else:
            img_url = product.thumbnail

        v_price = None
        if i < len(prices) and prices[i].strip():
            try:
                v_price = float(prices[i].strip())
            except ValueError:
                v_price = None

        v_stock = product.stock
        if i < len(stocks) and stocks[i].strip():
            try:
                v_stock = int(stocks[i].strip())
            except ValueError:
                v_stock = product.stock

        v_desc = descriptions[i].strip() if i < len(descriptions) else None

        variant = ProductVariant(
            product_id=product.id,
            color_name=c_name,
            color_code=c_code,
            image_url=img_url,
            price=v_price,
            stock=v_stock,
            description=v_desc
        )
        db.session.add(variant)

    # Process Multiple Extra Uploaded Gallery Photos
    gallery_files = files.getlist('gallery_files')
    for idx, g_file in enumerate(gallery_files, 1):
        g_url = save_uploaded_file(g_file)
        if g_url:
            g_variant = ProductVariant(
                product_id=product.id,
                color_name=f"Gallery Photo #{idx}",
                color_code="#38bdf8",
                image_url=g_url,
                price=product.price,
                stock=product.stock,
                description=f"Additional product angle view #{idx}"
            )
            db.session.add(g_variant)

    db.session.commit()

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_sales = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status != 'Cancelled').scalar() or 0.0
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_users = User.query.filter_by(role='user').count()
    low_stock_products = Product.query.filter(Product.stock <= 5, Product.is_active == True).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_sales=total_sales,
        total_orders=total_orders,
        total_products=total_products,
        total_users=total_users,
        low_stock_products=low_stock_products,
        recent_orders=recent_orders
    )

# --- PRODUCT MANAGEMENT ---
@admin_bp.route('/products')
@admin_required
def products():
    all_products = Product.query.order_by(Product.id.desc()).all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=all_products, categories=categories)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        brand = request.form.get('brand', '').strip()
        category_id = int(request.form.get('category_id', 0))
        price = float(request.form.get('price', 0.0))
        original_price = float(request.form.get('original_price', price))
        discount_percent = int(request.form.get('discount_percent', 0))
        stock = int(request.form.get('stock', 0))
        description = request.form.get('description', '').strip()
        is_featured = True if request.form.get('is_featured') else False

        # Main Photo File Upload or URL
        uploaded_thumb = save_uploaded_file(request.files.get('thumbnail_file'))
        thumbnail = uploaded_thumb or request.form.get('thumbnail', '').strip() or 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800'

        slug = slugify(title)
        existing_slug = Product.query.filter_by(slug=slug).first()
        if existing_slug:
            slug = f"{slug}-{Product.query.count() + 1}"

        specs_raw = request.form.get('specifications_json', '{}')
        try:
            json.loads(specs_raw)
        except Exception:
            specs_raw = '{}'

        new_prod = Product(
            title=title,
            slug=slug,
            brand=brand,
            category_id=category_id,
            price=price,
            original_price=original_price,
            discount_percent=discount_percent,
            stock=stock,
            thumbnail=thumbnail,
            description=description,
            is_featured=is_featured,
            specifications_json=specs_raw
        )
        db.session.add(new_prod)
        db.session.commit()

        # Save Color Variants & Uploaded Photos
        process_variants(new_prod, request.form, request.files)

        flash(f'Product "{title}" created successfully with photos!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=None)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()

    if request.method == 'POST':
        product.title = request.form.get('title', '').strip()
        product.brand = request.form.get('brand', '').strip()
        product.category_id = int(request.form.get('category_id'))
        product.price = float(request.form.get('price'))
        product.original_price = float(request.form.get('original_price', product.price))
        product.discount_percent = int(request.form.get('discount_percent', 0))
        product.stock = int(request.form.get('stock'))
        
        uploaded_thumb = save_uploaded_file(request.files.get('thumbnail_file'))
        if uploaded_thumb:
            product.thumbnail = uploaded_thumb
        elif request.form.get('thumbnail', '').strip():
            product.thumbnail = request.form.get('thumbnail', '').strip()

        product.description = request.form.get('description', '').strip()
        product.is_featured = True if request.form.get('is_featured') else False
        product.is_active = True if request.form.get('is_active') else False

        specs_raw = request.form.get('specifications_json', '{}')
        try:
            json.loads(specs_raw)
            product.specifications_json = specs_raw
        except Exception:
            pass

        db.session.commit()

        # Update Color Variants & Uploaded Photos
        process_variants(product, request.form, request.files)

        flash(f'Product "{product.title}" updated successfully with photos!', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=product)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product.title}" deleted.', 'info')
    return redirect(url_for('admin.products'))

# --- CATEGORY MANAGEMENT ---
@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        slug = slugify(name)

        if not name:
            flash('Category name is required.', 'danger')
        else:
            existing = Category.query.filter_by(slug=slug).first()
            if existing:
                flash('Category with this name already exists.', 'warning')
            else:
                cat = Category(name=name, slug=slug, description=description, image_url=image_url)
                db.session.add(cat)
                db.session.commit()
                flash(f'Category "{name}" created!', 'success')
        return redirect(url_for('admin.categories'))

    all_categories = Category.query.all()
    return render_template('admin/categories.html', categories=all_categories)

@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{cat.name}" deleted.', 'info')
    return redirect(url_for('admin.categories'))

# --- ORDER MANAGEMENT ---
@admin_bp.route('/orders')
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=all_orders)

@admin_bp.route('/orders/update-status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.order_number} status changed to {new_status}.', 'success')
    return redirect(url_for('admin.orders'))

# --- USER MANAGEMENT ---
@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)
