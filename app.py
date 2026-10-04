import os
from flask import Flask, render_template
from config import Config
from models import db, login_manager, bcrypt
from models.cart import CartItem, WishlistItem
from flask_login import current_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.shop import shop_bp
    from routes.cart import cart_bp
    from routes.user import user_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # Global Template Context Processor (Cart & Wishlist counts)
    @app.context_processor
    def inject_global_counts():
        cart_count = 0
        wishlist_count = 0
        if current_user.is_authenticated:
            cart_count = sum(item.quantity for item in current_user.cart_items)
            wishlist_count = len(current_user.wishlist_items)
        return dict(cart_count=cart_count, wishlist_count=wishlist_count)

    # Global 404 & 500 error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    # Auto-initialize database & seed data
    with app.app_context():
        db.create_all()
        from database import seed_database
        try:
            seed_database()
        except Exception as err:
            print(f"Database seed note: {err}")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
