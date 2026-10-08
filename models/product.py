from datetime import datetime
import json
from models import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False)
    brand = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)
    discount_percent = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=10) # Online E-Commerce Stock
    retail_shop_stock = db.Column(db.Integer, default=15) # Physical Retail Shop Stock (Omnichannel Sync)
    last_synced_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Float, default=4.5)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    thumbnail = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    specifications_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade="all, delete-orphan")
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy=True, cascade="all, delete-orphan")
    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade="all, delete-orphan")

    @property
    def total_combined_stock(self):
        return self.stock + (self.retail_shop_stock or 0)

    @property
    def specifications(self):
        if self.specifications_json:
            try:
                return json.loads(self.specifications_json)
            except Exception:
                return {}
        return {}

    @specifications.setter
    def specifications(self, val):
        if isinstance(val, dict):
            self.specifications_json = json.dumps(val)
        elif isinstance(val, str):
            self.specifications_json = val

    def __repr__(self):
        return f"<Product {self.title}>"

class ProductVariant(db.Model):
    __tablename__ = 'product_variants'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    color_name = db.Column(db.String(50), nullable=False)
    color_code = db.Column(db.String(20), default='#333333')
    image_url = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=True) # Variant specific price override
    stock = db.Column(db.Integer, default=10)   # Variant specific stock
    description = db.Column(db.Text, nullable=True) # Color variant description note

    cart_items = db.relationship('CartItem', backref='variant', lazy=True)

    @property
    def effective_price(self):
        return self.price if (self.price is not None and self.price > 0) else self.product.price

    def __repr__(self):
        return f"<ProductVariant {self.color_name} for Product #{self.product_id}>"

class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), default='percent') # 'percent' or 'fixed'
    discount_value = db.Column(db.Float, nullable=False)
    min_order_amount = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_discount(self, cart_total):
        if cart_total < self.min_order_amount:
            return 0.0
        if self.discount_type == 'percent':
            return round((cart_total * self.discount_value) / 100.0, 2)
        else:
            return min(self.discount_value, cart_total)

    def __repr__(self):
        return f"<Coupon {self.code} ({self.discount_value} {self.discount_type})>"

class ReturnRequest(db.Model):
    __tablename__ = 'return_requests'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    refund_upi_id = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(30), default='Requested') # Requested, Approved, Refunded, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref=db.backref('return_request', uselist=False))
    user = db.relationship('User', backref='return_requests')

    def __repr__(self):
        return f"<ReturnRequest Order #{self.order_id} - {self.status}>"
