from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.order import Order

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.address = request.form.get('address', '').strip()

        new_password = request.form.get('new_password', '')
        if new_password:
            confirm_password = request.form.get('confirm_password', '')
            if new_password == confirm_password:
                current_user.set_password(new_password)
                flash('Profile & password updated successfully!', 'success')
            else:
                flash('Passwords do not match.', 'danger')
                return render_template('user/profile.html')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html')

@user_bp.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', orders=user_orders)

@user_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Calculate step status for tracking timeline visualization
    statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
    current_step = 1
    if order.status in statuses:
        current_step = statuses.index(order.status) + 1
    elif order.status == 'Cancelled':
        current_step = -1

    return render_template('user/order_detail.html', order=order, current_step=current_step, statuses=statuses)
