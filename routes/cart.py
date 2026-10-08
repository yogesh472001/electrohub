import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models import db
from models.product import Product, ProductVariant, Coupon
from models.cart import CartItem
from models.order import Order, OrderItem

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal for item in cart_items)
    shipping = 0.0 if subtotal > 999 or subtotal == 0 else 99.0
    tax = round(subtotal * 0.18, 2) # GST 18%

    # Applied Coupon Logic
    applied_coupon_code = session.get('applied_coupon_code')
    applied_coupon = None
    discount = 0.0
    if applied_coupon_code:
        applied_coupon = Coupon.query.filter_by(code=applied_coupon_code, is_active=True).first()
        if applied_coupon:
            discount = applied_coupon.calculate_discount(subtotal)

    grand_total = max(0.0, subtotal + shipping + tax - discount)

    return render_template(
        'cart/cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        discount=discount,
        applied_coupon=applied_coupon,
        grand_total=grand_total
    )

@cart_bp.route('/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    code = request.form.get('coupon_code', '').strip().upper()
    if not code:
        flash('Please enter a coupon code.', 'warning')
        return redirect(url_for('cart.view_cart'))

    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal for item in cart_items)

    if not coupon:
        flash(f'Invalid coupon code "{code}".', 'danger')
    elif subtotal < coupon.min_order_amount:
        flash(f'Coupon "{code}" requires a minimum order of ₹{coupon.min_order_amount:,.2f}.', 'warning')
    else:
        session['applied_coupon_code'] = coupon.code
        flash(f'🎉 Coupon "{code}" applied successfully!', 'success')

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove-coupon', methods=['POST'])
@login_required
def remove_coupon():
    session.pop('applied_coupon_code', None)
    flash('Coupon removed.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    variant_id = request.form.get('variant_id', type=int)

    selected_variant = None
    selected_color = None
    effective_stock = product.stock

    if variant_id:
        selected_variant = ProductVariant.query.filter_by(id=variant_id, product_id=product_id).first()
        if selected_variant:
            selected_color = selected_variant.color_name
            effective_stock = selected_variant.stock

    if effective_stock < quantity:
        flash(f'Sorry, only {effective_stock} units available for this item.', 'danger')
        return redirect(request.referrer or url_for('shop.products'))

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        variant_id=variant_id
    ).first()

    if cart_item:
        if (cart_item.quantity + quantity) > effective_stock:
            flash(f'Cannot add more than available stock ({effective_stock}).', 'warning')
            return redirect(request.referrer or url_for('cart.view_cart'))
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            variant_id=variant_id,
            selected_color=selected_color,
            quantity=quantity
        )
        db.session.add(cart_item)

    db.session.commit()

    color_msg = f" ({selected_color})" if selected_color else ""
    msg = f'{product.title}{color_msg} added to your cart!'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in current_user.cart_items)
        return jsonify({'success': True, 'message': msg, 'cart_count': cart_count})

    flash(msg, 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = int(request.form.get('quantity', 1))
    max_stock = cart_item.variant.stock if cart_item.variant else cart_item.product.stock

    if quantity <= 0:
        db.session.delete(cart_item)
    elif quantity > max_stock:
        flash(f'Only {max_stock} units available.', 'warning')
        cart_item.quantity = max_stock
    else:
        cart_item.quantity = quantity

    db.session.commit()
    flash('Cart updated.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is currently empty.', 'warning')
        return redirect(url_for('shop.products'))

    subtotal = sum(item.subtotal for item in cart_items)
    shipping = 0.0 if subtotal > 999 else 99.0
    tax = round(subtotal * 0.18, 2)

    applied_coupon_code = session.get('applied_coupon_code')
    applied_coupon = None
    discount = 0.0
    if applied_coupon_code:
        applied_coupon = Coupon.query.filter_by(code=applied_coupon_code, is_active=True).first()
        if applied_coupon:
            discount = applied_coupon.calculate_discount(subtotal)

    grand_total = max(0.0, subtotal + shipping + tax - discount)

    return render_template(
        'cart/checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        discount=discount,
        applied_coupon=applied_coupon,
        grand_total=grand_total
    )

@cart_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('shop.products'))

    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    shipping_address = request.form.get('shipping_address', '').strip()
    city = request.form.get('city', '').strip()
    zip_code = request.form.get('zip_code', '').strip()
    payment_method = request.form.get('payment_method', 'PhonePe (UPI)')
    upi_id = request.form.get('upi_id', '').strip()

    if not full_name or not shipping_address or not city or not zip_code or not phone:
        flash('Please fill in all required shipping details.', 'danger')
        return redirect(url_for('cart.checkout'))

    subtotal = sum(item.subtotal for item in cart_items)
    shipping = 0.0 if subtotal > 999 else 99.0
    tax = round(subtotal * 0.18, 2)

    applied_coupon_code = session.get('applied_coupon_code')
    discount = 0.0
    if applied_coupon_code:
        coupon = Coupon.query.filter_by(code=applied_coupon_code, is_active=True).first()
        if coupon:
            discount = coupon.calculate_discount(subtotal)

    grand_total = max(0.0, subtotal + shipping + tax - discount)

    # Stock check
    for item in cart_items:
        max_stk = item.variant.stock if item.variant else item.product.stock
        if max_stk < item.quantity:
            flash(f'Insufficient stock for {item.product.title}.', 'danger')
            return redirect(url_for('cart.view_cart'))

    # Generate order number
    order_num = "YM-" + str(uuid.uuid4().hex[:8]).upper()

    order = Order(
        order_number=order_num,
        user_id=current_user.id,
        full_name=full_name,
        email=email or current_user.email,
        phone=phone,
        shipping_address=shipping_address,
        city=city,
        zip_code=zip_code,
        payment_method=payment_method,
        total_amount=grand_total,
        status='Pending'
    )
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        thumb = item.variant.image_url if (item.variant and item.variant.image_url) else item.product.thumbnail
        price = item.unit_price

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            selected_color=item.selected_color,
            product_name=item.product.title,
            price=price,
            quantity=item.quantity,
            thumbnail=thumb
        )
        db.session.add(order_item)

    db.session.commit()
    session.pop('applied_coupon_code', None)

    gateway = 'phonepe'
    if 'Google Pay' in payment_method or 'GPay' in payment_method:
        gateway = 'gpay'
    elif 'Paytm' in payment_method:
        gateway = 'paytm'
    elif 'Card' in payment_method:
        gateway = 'card'
    elif 'Net Banking' in payment_method:
        gateway = 'netbanking'

    return redirect(url_for('cart.payment_gateway', gateway=gateway, order_id=order.id, upi_id=upi_id))

@cart_bp.route('/payment-gateway/<gateway>/<int:order_id>')
@login_required
def payment_gateway(gateway, order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    upi_id = request.args.get('upi_id', '')

    if gateway not in ['phonepe', 'gpay', 'paytm', 'card', 'netbanking']:
        gateway = 'phonepe'

    return render_template('cart/payment_gateway.html', order=order, gateway=gateway, upi_id=upi_id)

@cart_bp.route('/payment-callback/<int:order_id>', methods=['POST'])
@login_required
def payment_callback(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order.status = 'Processing'

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    for item in cart_items:
        if item.variant:
            item.variant.stock -= item.quantity
        else:
            item.product.stock -= item.quantity
        db.session.delete(item)

    db.session.commit()
    flash(f'🎉 Payment of ₹{order.total_amount:,.2f} received via {order.payment_method}! Order #{order.order_number} is confirmed.', 'success')
    return redirect(url_for('user.order_detail', order_id=order.id))

@cart_bp.route('/invoice/<int:order_id>')
@login_required
def invoice(order_id):
    order = Order.query.filter_by(id=order_id).first_or_404()
    if not current_user.is_admin() and order.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('shop.index'))
    return render_template('cart/invoice.html', order=order)
