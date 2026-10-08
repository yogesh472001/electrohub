from datetime import datetime
from flask import Blueprint, request, jsonify, session, url_for
from models import db
from models.product import Product

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/search-autocomplete')
def search_autocomplete():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])

    results = Product.query.filter(
        Product.is_active == True,
        (Product.title.ilike(f'%{q}%')) | (Product.brand.ilike(f'%{q}%')) | (Product.description.ilike(f'%{q}%'))
    ).limit(6).all()

    output = []
    for p in results:
        output.append({
            'id': p.id,
            'title': p.title,
            'brand': p.brand,
            'price': f"₹{p.price:,.2f}",
            'thumbnail': p.thumbnail,
            'url': url_for('shop.product_detail', slug=p.slug)
        })

    return jsonify(output)

@api_bp.route('/inventory/sync', methods=['GET', 'POST'])
def inventory_sync():
    """Omnichannel Centralized Inventory Sync API between Physical Retail Shop & Online Store."""
    products = Product.query.all()
    synced_count = 0
    now = datetime.utcnow()

    for p in products:
        if request.method == 'POST':
            # Simulate POS system updating retail stock
            new_retail_stock = request.json.get(f'prod_{p.id}_stock') if request.is_json else None
            if new_retail_stock is not None:
                p.retail_shop_stock = int(new_retail_stock)

        p.last_synced_at = now
        synced_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Centralized Omnichannel Inventory Synchronized for {synced_count} products!',
        'synced_at': now.strftime('%Y-%m-%d %H:%M:%S IST')
    })
