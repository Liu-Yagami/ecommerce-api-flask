from flask import Blueprint, jsonify, request
from extensions import db
from models import Wishlist

wishlists_bp = Blueprint("wishlists", __name__)

@wishlists_bp.route("/wishlists", methods=["GET"])
def get_wishlists():
    wishlists = Wishlist.query.all()
    wishlists_data = [
        {"id": wishlist.id, "user_id": wishlist.user_id, "product_id": wishlist.product_id}
        for wishlist in wishlists
    ]
    return jsonify(wishlists_data), 200

@wishlists_bp.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlist(wishlist_id):
    wishlist = Wishlist.query.get(wishlist_id)
    if not wishlist:
        return jsonify({"error": "Wishlist not found"}), 404

    wishlist_data = {"id": wishlist.id, "user_id": wishlist.user_id, "product_id": wishlist.product_id}
    return jsonify(wishlist_data), 200

@wishlists_bp.route("/wishlists", methods=["POST"])
def create_wishlist():
    data = request.get_json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    if not user_id or not product_id:
        return jsonify({"error": "Missing required fields"}), 400

    new_wishlist = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(new_wishlist)
    db.session.commit()

    return jsonify({"message": "Wishlist created successfully", "wishlist_id": new_wishlist.id}), 201

@wishlists_bp.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlist(wishlist_id):
    wishlist = Wishlist.query.get(wishlist_id)
    if not wishlist:
        return jsonify({"error": "Wishlist not found"}), 404

    db.session.delete(wishlist)
    db.session.commit()

    return jsonify({"message": "Wishlist deleted successfully"}), 200