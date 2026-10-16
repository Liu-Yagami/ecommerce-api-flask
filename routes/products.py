from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from extensions import db
from models import Product
from schemas import product_schema, products_schema

products_bp = Blueprint("products", __name__)

@products_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify(products_schema.dump(products)), 200

@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_schema.dump(product)), 200

@products_bp.route("/products", methods=["POST"])
def create_product():
    data = product_schema.load(request.get_json())  

    new_product = Product(name=data["name"], price=data["price"], description=data.get("description"))
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product created successfully", "product_id": new_product.id}), 201

@products_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = product_schema.load(request.get_json(), partial=True)  

    if "name" in data:
        product.name = data["name"]
    if "price" in data:
        product.price = data["price"]
    if "description" in data:
        product.description = data["description"]

    db.session.commit()
    return jsonify({"message": "Product updated successfully"}), 200

@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200