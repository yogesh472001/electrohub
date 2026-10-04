import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.product import Product, ProductVariant
from models.cart import CartItem
from models.order import Order, OrderItem

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal for item in cart_items)
    shipping = 0.0 if subtotal > 499 or subtotal == 0 else 25.0
    tax = round(subtotal * 0.08, 2)
    grand_total = subtotal + shipping + tax

    return render_template(
        'cart/cart.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
        grand_total=grand_total
    )

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
    shipping = 0.0 if subtotal > 499 else 25.0
    tax = round(subtotal * 0.08, 2)
    grand_total = subtotal + shipping + tax

    return render_template(
        'cart/checkout.html',
        cart_items=cart_items,
        subtotal=subtotal,
        shipping=shipping,
        tax=tax,
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
    payment_method = request.form.get('payment_method', 'Credit Card')

    if not full_name or not shipping_address or not city or not zip_code or not phone:
        flash('Please fill in all required shipping details.', 'danger')
        return redirect(url_for('cart.checkout'))

    subtotal = sum(item.subtotal for item in cart_items)
    shipping = 0.0 if subtotal > 499 else 25.0
    tax = round(subtotal * 0.08, 2)
    grand_total = subtotal + shipping + tax

    # Stock check
    for item in cart_items:
        max_stk = item.variant.stock if item.variant else item.product.stock
        if max_stk < item.quantity:
            flash(f'Insufficient stock for {item.product.title}.', 'danger')
            return redirect(url_for('cart.view_cart'))

    # Generate order number
    order_num = "EH-" + str(uuid.uuid4().hex[:8]).upper()

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
        
        # Deduct stock
        if item.variant:
            item.variant.stock -= item.quantity
        else:
            item.product.stock -= item.quantity
        
        # Remove from cart
        db.session.delete(item)

    db.session.commit()
    flash(f'Success! Your order #{order.order_number} has been placed.', 'success')
    return redirect(url_for('user.order_detail', order_id=order.id))
