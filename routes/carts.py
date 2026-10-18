from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from auth import current_user_id
from extensions import db
from models import Cart, Product

carts_bp = Blueprint("carts", __name__)


def serialize_cart(cart):
    return {"id": cart.id, "product_id": cart.product_id, "quantity": cart.quantity}


def valid_quantity(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def get_own_cart_item(cart_id):
    """Return the cart row only if it belongs to the logged-in user."""
    cart = db.session.get(Cart, cart_id)
    if not cart or cart.user_id != current_user_id():
        return None
    return cart


@carts_bp.route("/carts", methods=["GET"])
@jwt_required()
def get_my_cart():
    items = Cart.query.filter_by(user_id=current_user_id()).all()
    return jsonify([serialize_cart(item) for item in items]), 200


@carts_bp.route("/carts/<int:cart_id>", methods=["GET"])
@jwt_required()
def get_cart_item(cart_id):
    cart = get_own_cart_item(cart_id)
    if not cart:
        return jsonify({"error": "Cart item not found"}), 404
    return jsonify(serialize_cart(cart)), 200


@carts_bp.route("/carts", methods=["POST"])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not valid_quantity(quantity):
        return jsonify({"error": "product_id and a positive integer quantity are required"}), 400

    if not db.session.get(Product, product_id):
        return jsonify({"error": "Product not found"}), 404

    existing = Cart.query.filter_by(user_id=current_user_id(), product_id=product_id).first()
    if existing:
        existing.quantity += quantity
        db.session.commit()
        return jsonify({"message": "Cart updated successfully", "cart_id": existing.id}), 200

    new_item = Cart(user_id=current_user_id(), product_id=product_id, quantity=quantity)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Added to cart", "cart_id": new_item.id}), 201


@carts_bp.route("/carts/<int:cart_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(cart_id):
    cart = get_own_cart_item(cart_id)
    if not cart:
        return jsonify({"error": "Cart item not found"}), 404

    quantity = request.get_json().get("quantity")
    if not valid_quantity(quantity):
        return jsonify({"error": "A positive integer quantity is required"}), 400

    cart.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Cart updated successfully"}), 200


@carts_bp.route("/carts/<int:cart_id>", methods=["DELETE"])
@jwt_required()
def delete_cart_item(cart_id):
    cart = get_own_cart_item(cart_id)
    if not cart:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(cart)
    db.session.commit()
    return jsonify({"message": "Removed from cart"}), 200


@carts_bp.route("/carts", methods=["DELETE"])
@jwt_required()
def clear_my_cart():
    Cart.query.filter_by(user_id=current_user_id()).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared"}), 200