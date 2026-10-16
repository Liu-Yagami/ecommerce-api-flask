from flask import Blueprint, jsonify, request
from extensions import db
from models import Cart

carts_bp = Blueprint("carts", __name__)

@carts_bp.route("/carts", methods=["GET"])
def get_carts():
    carts = Cart.query.all()
    carts_data = [
        {"id": cart.id, "user_id": cart.user_id, "product_id": cart.product_id, "quantity": cart.quantity}
        for cart in carts
    ]
    return jsonify(carts_data), 200

@carts_bp.route("/carts/<int:cart_id>", methods=["GET"])
def get_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    cart_data = {"id": cart.id, "user_id": cart.user_id, "product_id": cart.product_id, "quantity": cart.quantity}
    return jsonify(cart_data), 200

@carts_bp.route("/carts", methods=["POST"])
def create_cart():
    data = request.get_json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not user_id or not product_id or quantity is None:
        return jsonify({"error": "Missing required fields"}), 400

    new_cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(new_cart)
    db.session.commit()

    return jsonify({"message": "Cart created successfully", "cart_id": new_cart.id}), 201


@carts_bp.route("/carts/<int:cart_id>", methods=["PUT"])
def update_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    data = request.get_json()
    quantity = data.get("quantity")

    if quantity is None:
        return jsonify({"error": "Missing required field: quantity"}), 400

    cart.quantity = quantity
    db.session.commit()

    return jsonify({"message": "Cart updated successfully"}), 200


@carts_bp.route("/carts/<int:cart_id>", methods=["DELETE"])
def delete_cart(cart_id):
    cart = Cart.query.get(cart_id)
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    db.session.delete(cart)
    db.session.commit()

    return jsonify({"message": "Cart deleted successfully"}), 200

@carts_bp.route("/carts/user/<int:user_id>", methods=["GET"])
def get_carts_by_user(user_id):
    carts = Cart.query.filter_by(user_id=user_id).all()
    if not carts:
        return jsonify({"error": "No carts found for this user"}), 404

    carts_data = [
        {"id": cart.id, "user_id": cart.user_id, "product_id": cart.product_id, "quantity": cart.quantity}
        for cart in carts
    ]
    return jsonify(carts_data), 200

@carts_bp.route("/carts/user/<int:user_id>", methods=["DELETE"])
def delete_carts_by_user(user_id):
    carts = Cart.query.filter_by(user_id=user_id).all()
    if not carts:
        return jsonify({"error": "No carts found for this user"}), 404

    for cart in carts:
        db.session.delete(cart)
    db.session.commit()

    return jsonify({"message": "All carts for the user deleted successfully"}), 200