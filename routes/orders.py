from decimal import Decimal
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from auth import current_user_id
from extensions import db
from models import Order, OrderItem, Product

orders_bp = Blueprint("orders", __name__)


def serialize_order(order):
    return {
        "id": order.id,
        "status": order.status,
        "total_price": str(order.total_price),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_purchase": str(item.price_at_purchase),
            }
            for item in order.items
        ],
    }


def get_own_order(order_id):
    order = db.session.get(Order, order_id)
    if not order or order.user_id != current_user_id():
        return None
    return order


@orders_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_my_orders():
    orders = Order.query.filter_by(user_id=current_user_id()).all()
    return jsonify([serialize_order(order) for order in orders]), 200


@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    order = get_own_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(serialize_order(order)), 200


@orders_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    items_data = request.get_json().get("items")

    if not items_data or not isinstance(items_data, list):
        return jsonify({"error": "items must be a non-empty list"}), 400

    total_price = Decimal("0")
    order_items = []

    for item in items_data:
        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if not product_id or not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            return jsonify({"error": "Each item needs a product_id and a positive integer quantity"}), 400

        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({"error": f"Product with id {product_id} not found"}), 404

        total_price += product.price * quantity
        order_items.append(OrderItem(
            product_id=product_id,
            quantity=quantity,
            price_at_purchase=product.price,
        ))

    new_order = Order(
        user_id=current_user_id(),
        status="pending",
        total_price=total_price,
        items=order_items,
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Order created successfully", "order_id": new_order.id}), 201


@orders_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_order(order_id):
    order = get_own_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "pending":
        return jsonify({"error": "Only pending orders can be cancelled"}), 409

    order.status = "cancelled"
    db.session.commit()
    return jsonify({"message": "Order cancelled"}), 200