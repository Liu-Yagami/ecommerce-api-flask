from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Wishlist
from flask_jwt_extended import create_access_token, jwt_required
from auth import forbid_unless_owner

users_bp = Blueprint("users", __name__)

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from auth import forbid_unless_owner
from extensions import db
from models import User, Wishlist

users_bp = Blueprint("users", __name__)


# ---------- Public routes ----------

@users_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([first_name, last_name, username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200


# ---------- Restricted routes ----------

@users_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    denied = forbid_unless_owner(user_id)
    if denied:
        return denied

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email
    }), 200


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    denied = forbid_unless_owner(user_id)
    if denied:
        return denied

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    denied = forbid_unless_owner(user_id)
    if denied:
        return denied

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


@users_bp.route("/users/<int:user_id>/wishlist", methods=["GET"])
@jwt_required()
def get_user_wishlist(user_id):
    denied = forbid_unless_owner(user_id)
    if denied:
        return denied

    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": item.id, "product_id": item.product_id}
        for item in wishlist_items
    ]), 200


@users_bp.route("/users/<int:user_id>/wishlist", methods=["POST"])
@jwt_required()
def add_to_wishlist(user_id):
    denied = forbid_unless_owner(user_id)
    if denied:
        return denied

    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    existing_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_item:
        return jsonify({"error": "Product already in wishlist"}), 409

    new_wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(new_wishlist_item)
    db.session.commit()

    return jsonify({"message": "Product added to wishlist", "wishlist_item_id": new_wishlist_item.id}), 201