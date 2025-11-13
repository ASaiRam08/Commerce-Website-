# db_init.py
from app import create_app
from models import db, Product, Inventory
from decimal import Decimal

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    # sample products
    p1 = Product(sku="SKU-1001", name="Wireless Mouse", description="Ergonomic wireless mouse", price=Decimal("499.00"))
    p2 = Product(sku="SKU-2001", name="Learning SQL Book", description="Intro to SQL", price=Decimal("799.00"))
    p3 = Product(sku="SKU-3001", name="Cotton T-Shirt", description="Comfort tee", price=Decimal("299.00"))
    db.session.add_all([p1, p2, p3])
    db.session.flush()

    inv1 = Inventory(product_id=p1.product_id, quantity=50, reserved=0)
    inv2 = Inventory(product_id=p2.product_id, quantity=20, reserved=0)
    inv3 = Inventory(product_id=p3.product_id, quantity=100, reserved=0)
    db.session.add_all([inv1, inv2, inv3])
    db.session.commit()
    print("Database initialized with sample products.")
