from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.order import Order
from models.product import ReturnRequest

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
    
    statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
    current_step = 1
    if order.status in statuses:
        current_step = statuses.index(order.status) + 1
    elif order.status == 'Cancelled':
        current_step = -1

    return render_template('user/order_detail.html', order=order, current_step=current_step, statuses=statuses)

@user_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.status in ['Pending', 'Processing']:
        order.status = 'Cancelled'
        db.session.commit()
        flash(f'Order #{order.order_number} has been cancelled successfully.', 'info')
    else:
        flash('Order cannot be cancelled at this stage.', 'warning')
    return redirect(url_for('user.order_detail', order_id=order.id))

@user_bp.route('/order/<int:order_id>/request-return', methods=['POST'])
@login_required
def request_return(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    if order.status == 'Delivered':
        reason = request.form.get('reason', '').strip()
        refund_upi_id = request.form.get('refund_upi_id', '').strip()
        
        if not reason:
            flash('Please specify a reason for return.', 'warning')
        else:
            existing = ReturnRequest.query.filter_by(order_id=order.id).first()
            if existing:
                flash('A return request has already been submitted for this order.', 'info')
            else:
                ret = ReturnRequest(order_id=order.id, user_id=current_user.id, reason=reason, refund_upi_id=refund_upi_id)
                db.session.add(ret)
                db.session.commit()
                flash('Return & refund request submitted successfully! Our team will process it within 24 hours.', 'success')
    else:
        flash('Return request can only be submitted for delivered orders.', 'warning')
    return redirect(url_for('user.order_detail', order_id=order.id))
