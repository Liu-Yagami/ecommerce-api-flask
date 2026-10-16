import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from extensions import db, jwt, ma
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from routes.users import users_bp
from routes.products import products_bp
from routes.carts import carts_bp
from routes.orders import orders_bp
from routes.wishlists import wishlists_bp

load_dotenv()

app = Flask(__name__)
migrate = Migrate()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
ma.init_app(app)

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(carts_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(wishlists_bp)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    db.session.rollback()
    return jsonify({"error": "Database constraint violated (duplicate or invalid reference)"}), 409


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    db.session.rollback()
    app.logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({"error": "Validation failed", "details": e.messages}), 400

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code

    db.session.rollback()
    app.logger.error(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")
    app.run(debug=True)