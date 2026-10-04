import json
from models import db
from models.user import User
from models.product import Category, Product, ProductVariant

def seed_database():
    """Seeds initial categories, products with color variants, and default users."""
    if User.query.first():
        return # Already seeded

    print("Seeding initial ElectroHub database with color variants...")

    # Create Default Users
    admin = User(
        full_name="ElectroHub Admin",
        email="admin@electrohub.com",
        role="admin",
        phone="+1 800-555-TECH",
        address="100 Technology Plaza, Tech City, CA"
    )
    admin.set_password("admin123")

    customer = User(
        full_name="Alex Techie",
        email="customer@electrohub.com",
        role="user",
        phone="+1 555-019-2834",
        address="742 Evergreen Terrace, Springfield, OR"
    )
    customer.set_password("customer123")

    db.session.add_all([admin, customer])

    # Categories
    categories_data = [
        {"name": "Laptops", "slug": "laptops", "description": "High performance gaming & ultrabook laptops", "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80"},
        {"name": "Mobiles", "slug": "mobiles", "description": "Flagship smartphones with cutting-edge camera & speed", "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&auto=format&fit=crop&q=80"},
        {"name": "Headphones", "slug": "headphones", "description": "Premium wireless noise-cancelling headphones & earbuds", "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80"},
        {"name": "Keyboards", "slug": "keyboards", "description": "Mechanical, wireless, and ergonomic keyboards", "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80"},
        {"name": "Mouse", "slug": "mouse", "description": "Precision gaming & productivity wireless mice", "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80"},
        {"name": "Monitors", "slug": "monitors", "description": "4K UHD, OLED & ultra-wide high refresh rate monitors", "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80"},
        {"name": "Speakers", "slug": "speakers", "description": "Bluetooth portable speakers & studio soundbars", "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80"},
        {"name": "Accessories", "slug": "accessories", "description": "Fast chargers, cables, hubs & desk accessories", "image_url": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600&auto=format&fit=crop&q=80"}
    ]

    cat_map = {}
    for cat_dict in categories_data:
        cat = Category(**cat_dict)
        db.session.add(cat)
        db.session.flush()
        cat_map[cat.slug] = cat.id

    # Sample Products with Color Variants
    p1 = Product(
        title='Apple MacBook Pro 16" M3 Max',
        slug="apple-macbook-pro-16-m3-max",
        brand="Apple",
        category_id=cat_map["laptops"],
        price=3499.00,
        original_price=3799.00,
        discount_percent=8,
        stock=15,
        rating=4.9,
        is_featured=True,
        thumbnail="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
        description="Unleash extreme power with the M3 Max chip. 36GB Unified Memory, 1TB SSD, Liquid Retina XDR display, up to 22 hours of battery life.",
        specifications_json=json.dumps({"Processor": "Apple M3 Max 16-Core", "RAM": "36GB Unified", "Storage": "1TB NVMe SSD", "Display": '16.2" Liquid Retina XDR'})
    )
    db.session.add(p1)
    db.session.flush()

    v1_1 = ProductVariant(
        product_id=p1.id,
        color_name="Space Black",
        color_code="#1e1e1e",
        image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
        price=3499.00,
        stock=10,
        description="Deep dark Space Black anodized finish with anti-fingerprint seal."
    )
    v1_2 = ProductVariant(
        product_id=p1.id,
        color_name="Silver Aluminum",
        color_code="#e3e4e5",
        image_url="https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&auto=format&fit=crop&q=80",
        price=3499.00,
        stock=5,
        description="Classic sleek Silver metallic enclosure."
    )
    db.session.add_all([v1_1, v1_2])

    p2 = Product(
        title="iPhone 15 Pro Max (512GB)",
        slug="iphone-15-pro-max-512gb",
        brand="Apple",
        category_id=cat_map["mobiles"],
        price=1399.00,
        original_price=1499.00,
        discount_percent=7,
        stock=20,
        rating=4.9,
        is_featured=True,
        thumbnail="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80",
        description="Aerospace-grade titanium design with A17 Pro chip, Action Button, and 5x Optical Telephoto zoom.",
        specifications_json=json.dumps({"Chipset": "A17 Pro", "Camera": "48MP Main + 12MP 5x Telephoto", "Display": '6.7" Super Retina XDR'})
    )
    db.session.add(p2)
    db.session.flush()

    v2_1 = ProductVariant(
        product_id=p2.id,
        color_name="Natural Titanium",
        color_code="#9a958e",
        image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80",
        price=1399.00,
        stock=8,
        description="Raw metallic Natural Titanium with micro-blasted texture."
    )
    v2_2 = ProductVariant(
        product_id=p2.id,
        color_name="White Titanium",
        color_code="#f3f3f3",
        image_url="https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80",
        price=1429.00, # Price difference for color!
        stock=6,
        description="Bright White Titanium with ceramic shield front glass."
    )
    v2_3 = ProductVariant(
        product_id=p2.id,
        color_name="Blue Titanium",
        color_code="#323e4d",
        image_url="https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=800&auto=format&fit=crop&q=80",
        price=1399.00,
        stock=6,
        description="Rich deep navy Blue Titanium finish."
    )
    db.session.add_all([v2_1, v2_2, v2_3])

    p3 = Product(
        title="Sony WH-1000XM5 Wireless Headphones",
        slug="sony-wh-1000xm5",
        brand="Sony",
        category_id=cat_map["headphones"],
        price=398.00,
        original_price=449.99,
        discount_percent=11,
        stock=30,
        rating=4.8,
        is_featured=True,
        thumbnail="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
        description="Industry leading active noise cancellation with Auto NC Optimizer and 30-hour battery life.",
        specifications_json=json.dumps({"Battery": "30 Hours", "Noise Cancellation": "Auto NC Optimizer", "Driver": "30mm Precision Driver"})
    )
    db.session.add(p3)
    db.session.flush()

    v3_1 = ProductVariant(
        product_id=p3.id,
        color_name="Matte Black",
        color_code="#111111",
        image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
        price=398.00,
        stock=15,
        description="Sleek soft-touch Matte Black color edition."
    )
    v3_2 = ProductVariant(
        product_id=p3.id,
        color_name="Silver Cream",
        color_code="#e6e2dd",
        image_url="https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
        price=398.00,
        stock=10,
        description="Elegant Off-White Silver Cream edition with copper accents."
    )
    v3_3 = ProductVariant(
        product_id=p3.id,
        color_name="Midnight Blue (Limited Edition)",
        color_code="#1c2841",
        image_url="https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&auto=format&fit=crop&q=80",
        price=419.00, # Custom higher price for limited edition color!
        stock=5,
        description="Exclusive Midnight Blue limited collector color edition."
    )
    db.session.add_all([v3_1, v3_2, v3_3])

    # Other products...
    p4 = Product(
        title="Logitech MX Master 3S Mouse",
        slug="logitech-mx-master-3s",
        brand="Logitech",
        category_id=cat_map["mouse"],
        price=99.99,
        original_price=119.99,
        discount_percent=16,
        stock=40,
        rating=4.9,
        is_featured=True,
        thumbnail="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
        description="Iconic ergonomic mouse with Quiet Clicks, 8K DPI sensor, and MagSpeed electromagnetic scrolling.",
        specifications_json=json.dumps({"DPI": "8000 DPI Sensor", "Battery": "70 Days", "Connection": "Bluetooth & Logi Bolt"})
    )
    db.session.add(p4)

    p5 = Product(
        title='LG UltraGear 27" 4K OLED Monitor',
        slug="lg-ultragear-27-4k-oled",
        brand="LG",
        category_id=cat_map["monitors"],
        price=999.99,
        original_price=1199.99,
        discount_percent=16,
        stock=6,
        rating=4.9,
        is_featured=True,
        thumbnail="https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
        description="Blazing fast 0.03ms response time 240Hz OLED gaming display with DisplayHDR True Black 400.",
        specifications_json=json.dumps({"Panel": "27-inch OLED", "Resolution": "3840 x 2160", "Refresh Rate": "240Hz"})
    )
    db.session.add(p5)

    db.session.commit()
    print("Database successfully seeded with color variants!")
