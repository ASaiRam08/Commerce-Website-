# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    inventory = db.relationship("Inventory", back_populates="product", uselist=False)
    def to_dict(self):
        inv = self.inventory
        available = 0
        if inv:
            available = inv.quantity - inv.reserved
        return {
            "product_id": self.product_id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "available_qty": int(available)
        }

class Inventory(db.Model):
    __tablename__ = "inventory"
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reserved = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship("Product", back_populates="inventory")

class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    total_amount = db.Column(db.Numeric(12,2), nullable=False)
    status = db.Column(db.String(32), default="PENDING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    __tablename__ = "order_items"
    order_item_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Numeric(12,2), nullable=False)
