import json
from models import db
from models.user import User
from models.product import Category, Product

def seed_database():
    """Seeds initial categories, products, and default admin/customer users."""
    if User.query.first():
        return # Already seeded

    print("Seeding initial ElectroHub database...")

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

    # Categories as requested: laptops, mobiles, headphones, keyboards, mouse, monitors, speakers, accessories
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

    # Sample Tech Products
    products_data = [
        # Laptops
        {
            "title": 'Apple MacBook Pro 16" M3 Max',
            "slug": "apple-macbook-pro-16-m3-max",
            "brand": "Apple",
            "category_id": cat_map["laptops"],
            "price": 3499.00,
            "original_price": 3799.00,
            "discount_percent": 8,
            "stock": 15,
            "rating": 4.9,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80",
            "description": "Unleash extreme power with the M3 Max chip. 36GB Unified Memory, 1TB SSD, Liquid Retina XDR display, up to 22 hours of battery life.",
            "specifications_json": json.dumps({"Processor": "Apple M3 Max 16-Core", "RAM": "36GB Unified", "Storage": "1TB NVMe SSD", "Display": '16.2" Liquid Retina XDR (3456 x 2234)', "Weight": "2.16 kg", "OS": "macOS Sequoia"})
        },
        {
            "title": "ASUS ROG Strix SCAR 18 Gaming Laptop",
            "slug": "asus-rog-strix-scar-18",
            "brand": "ASUS",
            "category_id": cat_map["laptops"],
            "price": 2899.99,
            "original_price": 3199.99,
            "discount_percent": 9,
            "stock": 8,
            "rating": 4.8,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800&auto=format&fit=crop&q=80",
            "description": "Dominating gaming performance featuring Intel Core i9-14900HX and NVIDIA GeForce RTX 4090 GPU with 240Hz Nebula HDR Display.",
            "specifications_json": json.dumps({"Processor": "Intel Core i9-14900HX", "GPU": "NVIDIA RTX 4090 16GB", "RAM": "32GB DDR5", "Storage": "2TB PCIe 4.0 SSD", "Display": '18" QHD+ 240Hz Mini LED'})
        },
        {
            "title": "Dell XPS 15 9530 Ultrabook",
            "slug": "dell-xps-15-9530",
            "brand": "Dell",
            "category_id": cat_map["laptops"],
            "price": 1899.00,
            "original_price": 2099.00,
            "discount_percent": 10,
            "stock": 12,
            "rating": 4.6,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800&auto=format&fit=crop&q=80",
            "description": "Sleek aluminum chassis with 3.5K OLED Touch Display, Intel Core i7 13th Gen, and RTX 4060 graphics.",
            "specifications_json": json.dumps({"Processor": "Intel i7-13700H", "RAM": "16GB DDR5", "Storage": "1TB SSD", "Display": '15.6" 3.5K OLED Touch'})
        },
        # Mobiles
        {
            "title": "iPhone 15 Pro Max (512GB - Natural Titanium)",
            "slug": "iphone-15-pro-max-512gb",
            "brand": "Apple",
            "category_id": cat_map["mobiles"],
            "price": 1399.00,
            "original_price": 1499.00,
            "discount_percent": 7,
            "stock": 20,
            "rating": 4.9,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80",
            "description": "Aerospace-grade titanium design with A17 Pro chip, Action Button, 5x Optical Telephoto zoom, and USB-C speed.",
            "specifications_json": json.dumps({"Chipset": "A17 Pro", "Camera": "48MP Main + 12MP Ultra-wide + 12MP 5x Telephoto", "Display": '6.7" Super Retina XDR ProMotion', "Storage": "512GB"})
        },
        {
            "title": "Samsung Galaxy S24 Ultra 5G (256GB)",
            "slug": "samsung-galaxy-s24-ultra",
            "brand": "Samsung",
            "category_id": cat_map["mobiles"],
            "price": 1299.99,
            "original_price": 1399.99,
            "discount_percent": 7,
            "stock": 18,
            "rating": 4.8,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80",
            "description": "Galaxy AI powered flagship with built-in S Pen, 200MP camera system, Snapdragon 8 Gen 3 for Galaxy, and Titanium frame.",
            "specifications_json": json.dumps({"Processor": "Snapdragon 8 Gen 3", "Main Camera": "200MP Quad Camera", "Battery": "5000 mAh", "Display": '6.8" Dynamic AMOLED 2X 120Hz'})
        },
        # Headphones
        {
            "title": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones",
            "slug": "sony-wh-1000xm5",
            "brand": "Sony",
            "category_id": cat_map["headphones"],
            "price": 398.00,
            "original_price": 449.99,
            "discount_percent": 11,
            "stock": 30,
            "rating": 4.8,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80",
            "description": "Industry leading active noise cancellation with Auto NC Optimizer, 30-hour battery life, and crystal-clear hands-free calling.",
            "specifications_json": json.dumps({"Battery Life": "Up to 30 Hours", "Noise Cancellation": "Dual Processor Auto NC", "Drivers": "30mm Precision Driver", "Weight": "250g"})
        },
        {
            "title": "Apple AirPods Max (Space Gray)",
            "slug": "apple-airpods-max",
            "brand": "Apple",
            "category_id": cat_map["headphones"],
            "price": 549.00,
            "original_price": 599.00,
            "discount_percent": 8,
            "stock": 10,
            "rating": 4.7,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop&q=80",
            "description": "Apple-designed dynamic driver provides high-fidelity audio. Computational audio with H1 chip and Spatial Audio support.",
            "specifications_json": json.dumps({"Chip": "Apple H1 in each ear cup", "Audio Tech": "Spatial Audio with Dynamic Head Tracking", "Battery": "20 hours with ANC enabled"})
        },
        # Keyboards
        {
            "title": "Keychron K2 Pro QMK/VIA Wireless Mechanical Keyboard",
            "slug": "keychron-k2-pro-mechanical-keyboard",
            "brand": "Keychron",
            "category_id": cat_map["keyboards"],
            "price": 119.99,
            "original_price": 139.99,
            "discount_percent": 14,
            "stock": 25,
            "rating": 4.7,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=80",
            "description": "75% compact wireless custom mechanical keyboard with hot-swappable Keychron K Pro switches, RGB backlight, and Mac/Windows layout.",
            "specifications_json": json.dumps({"Layout": "75% Compact", "Switch Type": "Gateron G Pro Red / Brown", "Connectivity": "Bluetooth 5.1 & Type-C Wired", "Battery": "4000 mAh"})
        },
        {
            "title": "Razer BlackWidow V4 Pro Mechanical Gaming Keyboard",
            "slug": "razer-blackwidow-v4-pro",
            "brand": "Razer",
            "category_id": cat_map["keyboards"],
            "price": 229.99,
            "original_price": 249.99,
            "discount_percent": 8,
            "stock": 14,
            "rating": 4.6,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=800&auto=format&fit=crop&q=80",
            "description": "Full-size gaming keyboard with Razer Command Dial, 8 dedicated macro keys, Chroma RGB lighting, and magnetic wrist rest.",
            "specifications_json": json.dumps({"Switch": "Razer Green Clicky / Yellow Linear", "Polling Rate": "8000 Hz", "Lighting": "Razer Chroma RGB per-key", "Wrist Rest": "Plush Leatherette"})
        },
        # Mouse
        {
            "title": "Logitech MX Master 3S Wireless Performance Mouse",
            "slug": "logitech-mx-master-3s",
            "brand": "Logitech",
            "category_id": cat_map["mouse"],
            "price": 99.99,
            "original_price": 119.99,
            "discount_percent": 16,
            "stock": 40,
            "rating": 4.9,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&auto=format&fit=crop&q=80",
            "description": "Iconic ergonomic mouse with Quiet Clicks, 8K DPI track-on-glass sensor, MagSpeed electromagnetic scrolling, and multi-device pairing.",
            "specifications_json": json.dumps({"DPI": "8000 DPI Darkfield Sensor", "Buttons": "7 Programmable Buttons", "Battery": "Up to 70 days per charge", "Connection": "Bluetooth & Logi Bolt"})
        },
        {
            "title": "Logitech G Pro X Superlight 2 Wireless Gaming Mouse",
            "slug": "logitech-g-pro-x-superlight-2",
            "brand": "Logitech",
            "category_id": cat_map["mouse"],
            "price": 159.00,
            "original_price": 179.00,
            "discount_percent": 11,
            "stock": 19,
            "rating": 4.8,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=80",
            "description": "Ultra-lightweight 60g esports mouse with HERO 2 sensor, LIGHTFORCE hybrid switches, and 95-hour battery life.",
            "specifications_json": json.dumps({"Weight": "60g", "Sensor": "HERO 2 (32000 DPI)", "Polling Rate": "4000 Hz", "Switches": "LIGHTFORCE Hybrid Optical-Mechanical"})
        },
        # Monitors
        {
            "title": 'LG UltraGear 27" 4K OLED 240Hz Gaming Monitor',
            "slug": "lg-ultragear-27-4k-oled",
            "brand": "LG",
            "category_id": cat_map["monitors"],
            "price": 999.99,
            "original_price": 1199.99,
            "discount_percent": 16,
            "stock": 6,
            "rating": 4.9,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=80",
            "description": "Blazing fast 0.03ms response time 240Hz OLED gaming display with DisplayHDR True Black 400 and NVIDIA G-SYNC compatibility.",
            "specifications_json": json.dumps({"Panel": "27-inch OLED", "Resolution": "3840 x 2160 (4K)", "Refresh Rate": "240Hz", "Response Time": "0.03ms (GtG)", "Ports": "HDMI 2.1 x2, DisplayPort 1.4"})
        },
        {
            "title": 'Dell UltraSharp 34" Curved USB-C Hub Monitor (U3423WE)',
            "slug": "dell-ultrasharp-34-curved",
            "brand": "Dell",
            "category_id": cat_map["monitors"],
            "price": 749.00,
            "original_price": 849.00,
            "discount_percent": 11,
            "stock": 10,
            "rating": 4.7,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1547119957-637f8679db1e?w=800&auto=format&fit=crop&q=80",
            "description": "Immersive WQHD IPS Black panel with 2000:1 contrast ratio, integrated 90W USB-C PD hub, and KVM switch.",
            "specifications_json": json.dumps({"Resolution": "3440 x 1440 WQHD", "Panel": "IPS Black", "Curvature": "1900R", "USB-C Power": "90W Power Delivery"})
        },
        # Speakers
        {
            "title": "JBL Charge 5 Portable Waterproof Bluetooth Speaker",
            "slug": "jbl-charge-5-bluetooth-speaker",
            "brand": "JBL",
            "category_id": cat_map["speakers"],
            "price": 149.95,
            "original_price": 179.95,
            "discount_percent": 16,
            "stock": 35,
            "rating": 4.8,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop&q=80",
            "description": "Delivers bold JBL Original Pro Sound with long excursion driver, separate tweeter and dual passive bass radiators. IP67 waterproof and built-in powerbank.",
            "specifications_json": json.dumps({"Battery": "20 Hours Playtime", "Waterproof Rating": "IP67 Dust & Water Proof", "Output Power": "40W RMS", "Weight": "0.96 kg"})
        },
        {
            "title": "Sonos Era 300 Smart Speaker with Spatial Audio",
            "slug": "sonos-era-300-smart-speaker",
            "brand": "Sonos",
            "category_id": cat_map["speakers"],
            "price": 449.00,
            "original_price": 499.00,
            "discount_percent": 10,
            "stock": 11,
            "rating": 4.7,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&auto=format&fit=crop&q=80",
            "description": "Next-level audio performance featuring 6 optimally positioned drivers for Dolby Atmos Spatial Audio streaming.",
            "specifications_json": json.dumps({"Audio Tech": "Dolby Atmos Spatial Audio", "Voice Control": "Sonos Voice & Alexa", "Connectivity": "Wi-Fi 6, Bluetooth 5.0, AirPlay 2"})
        },
        # Accessories
        {
            "title": "Anker 737 Power Bank (PowerCore 24K 140W)",
            "slug": "anker-737-power-bank-140w",
            "brand": "Anker",
            "category_id": cat_map["accessories"],
            "price": 109.99,
            "original_price": 149.99,
            "discount_percent": 26,
            "stock": 45,
            "rating": 4.9,
            "is_featured": True,
            "thumbnail": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&auto=format&fit=crop&q=80",
            "description": "Ultra-powerful 24,000mAh portable battery pack with 140W bi-directional fast charging and smart digital color display.",
            "specifications_json": json.dumps({"Capacity": "24,000 mAh", "Max Output": "140W USB-C PD 3.1", "Ports": "2x USB-C, 1x USB-A", "Display": "Smart Digital OLED"})
        },
        {
            "title": "CalDigit TS4 Thunderbolt 4 Docking Station (18 Ports)",
            "slug": "caldigit-ts4-thunderbolt-4-dock",
            "brand": "CalDigit",
            "category_id": cat_map["accessories"],
            "price": 379.95,
            "original_price": 399.95,
            "discount_percent": 5,
            "stock": 14,
            "rating": 4.8,
            "is_featured": False,
            "thumbnail": "https://images.unsplash.com/photo-1544652478-6653e09f18a2?w=800&auto=format&fit=crop&q=80",
            "description": "The ultimate workstation dock featuring 18 ports of connectivity, 98W laptop charging, 2.5Gb Ethernet, and dual 4K / single 8K support.",
            "specifications_json": json.dumps({"Host Charging": "98W", "Ports": "18 Total (3x TB4, 5x USB-A, 3x USB-C, SD 4.0)", "Ethernet": "2.5 Gigabit"})
        }
    ]

    for prod_dict in products_data:
        p = Product(**prod_dict)
        db.session.add(p)

    db.session.commit()
    print("Database successfully seeded!")
