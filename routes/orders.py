from flask import jsonify, request, Blueprint
from extensions import db
from models import Order, OrderItem, Product

orders_bp = Blueprint("orders", __name__)

def serialize_order(order):
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_price": order.total_price,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_purchase": item.price_at_purchase
            }
            for item in order.items
        ]
    }

@orders_bp.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.all()
    orders_data = [serialize_order(order) for order in orders]
    return jsonify(orders_data), 200

@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order_data = serialize_order(order)
    return jsonify(order_data), 200

@orders_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    items_data = data.get("items")

    if not user_id or not items_data:
        return jsonify({"error": "Missing required fields"}), 400

    total_price = 0
    order_items = []

    for item in items_data:
        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if not product_id or not quantity:
            return jsonify({"error": "Missing product_id or quantity"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": f"Product with id {product_id} not found"}), 404

        price_at_purchase = product.price
        total_price += price_at_purchase * quantity

        order_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price_at_purchase=price_at_purchase
        )
        order_items.append(order_item)

    new_order = Order(
        user_id=user_id,
        status="pending",
        total_price=total_price,
        items=order_items
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Order created successfully", "order_id": new_order.id}), 201

@orders_bp.route("/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    status = data.get("status")

    if status:
        order.status = status

    db.session.commit()

    return jsonify({"message": "Order updated successfully"}), 200

@orders_bp.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": "Order deleted successfully"}), 200