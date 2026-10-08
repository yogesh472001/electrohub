from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required
from models import db
from models.product import Category, Product
from models.cart import WishlistItem

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/')
def index():
    categories = Category.query.all()
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    new_arrivals = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    flash_deals = Product.query.filter(Product.discount_percent > 10, Product.is_active == True).limit(4).all()
    
    return render_template(
        'shop/index.html',
        categories=categories,
        featured_products=featured_products,
        new_arrivals=new_arrivals,
        flash_deals=flash_deals
    )

@shop_bp.route('/products')
def products():
    query = Product.query.filter_by(is_active=True)

    # Search query
    q = request.args.get('q', '').strip()
    if q:
        query = query.filter((Product.title.ilike(f'%{q}%')) | (Product.brand.ilike(f'%{q}%')) | (Product.description.ilike(f'%{q}%')))

    # Category filter
    selected_category_slug = request.args.get('category', '').strip()
    selected_category = None
    if selected_category_slug:
        selected_category = Category.query.filter_by(slug=selected_category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    # Brand filter
    selected_brand = request.args.get('brand', '').strip()
    if selected_brand:
        query = query.filter_by(brand=selected_brand)

    # Min/Max Price filter
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Sorting
    sort_by = request.args.get('sort', 'featured')
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.is_featured.desc(), Product.id.desc())

    all_products = query.all()
    categories = Category.query.all()
    
    all_brands = db.session.query(Product.brand).filter_by(is_active=True).distinct().all()
    brands = sorted([b[0] for b in all_brands if b[0]])

    return render_template(
        'shop/products.html',
        products=all_products,
        categories=categories,
        brands=brands,
        selected_category=selected_category_slug,
        selected_brand=selected_brand,
        q=q,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )

@shop_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()

    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product.id).first() is not None

    return render_template('shop/product_detail.html', product=product, related_products=related_products, in_wishlist=in_wishlist)

@shop_bp.route('/compare')
def compare():
    compare_ids = session.get('compare_ids', [])
    products = Product.query.filter(Product.id.in_(compare_ids)).all() if compare_ids else []
    return render_template('shop/compare.html', compare_products=products)

@shop_bp.route('/compare/add/<int:product_id>')
def add_to_compare(product_id):
    compare_ids = session.get('compare_ids', [])
    if product_id not in compare_ids:
        if len(compare_ids) >= 4:
            flash('You can compare up to 4 products at once.', 'warning')
        else:
            compare_ids.append(product_id)
            session['compare_ids'] = compare_ids
            flash('Product added to comparison matrix!', 'success')
    return redirect(url_for('shop.compare'))

@shop_bp.route('/compare/remove/<int:product_id>')
def remove_from_compare(product_id):
    compare_ids = session.get('compare_ids', [])
    if product_id in compare_ids:
        compare_ids.remove(product_id)
        session['compare_ids'] = compare_ids
        flash('Product removed from comparison.', 'info')
    return redirect(url_for('shop.compare'))

@shop_bp.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('shop/wishlist.html', wishlist_items=wishlist_items)

@shop_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        added = False
        message = f"Removed {product.title} from your wishlist."
    else:
        new_item = WishlistItem(user_id=current_user.id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        added = True
        message = f"Added {product.title} to your wishlist!"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'added': added, 'message': message})

    flash(message, 'success' if added else 'info')
    return redirect(request.referrer or url_for('shop.products'))
