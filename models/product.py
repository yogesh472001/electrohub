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
    stock = db.Column(db.Integer, default=10)
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
