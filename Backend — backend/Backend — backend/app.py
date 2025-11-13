# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Product, Inventory, Order, OrderItem
from decimal import Decimal
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "shop.db")
DATABASE_URI = f"sqlite:///{DB_PATH}"

def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/")
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    CORS(app)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/products", methods=["GET"])
    def get_products():
        products = Product.query.all()
        return jsonify([p.to_dict() for p in products])

    @app.route("/api/checkout", methods=["POST"])
    def checkout():
        """
        Expected payload:
        {
          "items": [{"product_id": 1, "quantity": 2}, ...]
        }
        """
        data = request.get_json() or {}
        items = data.get("items", [])
        if not items:
            return jsonify({"error": "No items provided"}), 400

        # Validate items
        product_ids = [int(i["product_id"]) for i in items]
        products = {p.product_id: p for p in Product.query.filter(Product.product_id.in_(product_ids)).with_for_update().all()}

        # Use a DB transaction
        session = db.session
        try:
            total = Decimal("0.00")
            # Check inventory availability
            for it in items:
                pid = int(it["product_id"])
                qty = int(it["quantity"])
                if qty <= 0:
                    raise ValueError("Quantity must be > 0")
                prod = products.get(pid)
                if not prod:
                    return jsonify({"error": f"Product {pid} not found"}), 404
                inv = prod.inventory
                if inv is None or (inv.quantity - inv.reserved) < qty:
                    return jsonify({"error": f"Insufficient stock for {prod.name}"}), 400
                total += Decimal(str(prod.price)) * qty

            # All good -> create order
            order = Order(total_amount=total, status="PAID")  # for demo, treat as paid
            session.add(order)
            session.flush()  # get order.order_id

            # create order items and decrement inventory
            for it in items:
                pid = int(it["product_id"])
                qty = int(it["quantity"])
                prod = products[pid]
                line_total = Decimal(str(prod.price)) * qty
                oi = OrderItem(order_id=order.order_id, product_id=pid, product_name=prod.name,
                               unit_price=prod.price, quantity=qty, line_total=line_total)
                session.add(oi)
                # decrement quantity and reserved safety
                inv = prod.inventory
                inv.quantity = inv.quantity - qty
                inv.reserved = max(inv.reserved - qty, 0)

            session.commit()
            return jsonify({"ok": True, "order_id": order.order_id, "total": float(total)})
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    return app

if __name__ == "__main__":
    app = create_app()
    # create DB file if missing
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
