from flask import jsonify
from flask_jwt_extended import get_jwt_identity


def current_user_id():
    """The logged-in user's id, taken from the verified token."""
    return int(get_jwt_identity())


def forbid_unless_owner(user_id):
    """Return a 403 response if the logged-in user isn't `user_id`, otherwise None."""
    if current_user_id() != user_id:
        return jsonify({"error": "You can only access your own data"}), 403
    return None