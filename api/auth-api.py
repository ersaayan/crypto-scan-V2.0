from functools import wraps
from flask import Flask, request, jsonify, g
from flask_pymongo import PyMongo
from datetime import datetime, timedelta, timezone
import jwt
import uuid  # For generating one-time tokens
import random
import string
from bson import ObjectId, json_util

app = Flask(__name__)
app.config[
    "MONGO_URI"
] = "mongodb+srv://admin:aHIv2Z7YqntADkCP@ersaayan.tgvsjsr.mongodb.net/crypto_scan_auth_db"
mongo = PyMongo(app)

app.config["SECRET_KEY"] = "aX3ZmJddJ-z_pMAVuI8"


def token_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                return jsonify({"message": "Invalid token format!"}), 401

            token = token.split(" ")[1]

            if not token:
                return jsonify({"message": "Token is missing!"}), 401

            try:
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                g.user = data
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired!"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token!"}), 401

            user = mongo.db.users.find_one({"username": g.user["username"]})
            if not user or user.get("token") != token:
                return jsonify({"message": "Invalid token!"}), 401

            if "exp" not in g.user or g.user["exp"] < datetime.now().timestamp():
                return jsonify({"message": "Token has expired!"}), 401

            if role == "admin" and ("role" not in g.user or g.user["role"] != "admin"):
                return jsonify({"message": "Permission denied! Admins only!"}), 403
            if role == "user" and ("role" not in g.user or g.user["role"] != "user"):
                return jsonify({"message": "Permission denied! Users only!"}), 403
            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/login", methods=["POST"])
@token_required("user")
def login():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"message": "Username and password are required!"}), 400

    user = mongo.db.users.find_one(
        {"username": data["username"], "password": data["password"]}
    )
    if not user:
        return jsonify({"message": "Invalid credentials!"}), 401

    return jsonify({"message": "Login successful!"})


@app.route("/user", methods=["GET"])
@token_required("user")
def get_user():
    remaining_time_seconds = datetime.fromtimestamp(g.user["exp"]).replace(
        tzinfo=timezone.utc
    ) - datetime.now(timezone.utc)
    remaining_time_days = remaining_time_seconds.total_seconds() / (24 * 60 * 60)
    return jsonify(
        {"username": g.user["username"], "remaining_time_days": remaining_time_days}
    )


@app.route("/admin/create_user", methods=["POST"])
@token_required("admin")
def create_user():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"message": "Username and password are required!"}), 400

    if mongo.db.users.find_one({"username": data["username"]}):
        return jsonify({"message": "Username already exists!"}), 400

    new_user = {
        "username": data["username"],
        "password": data["password"],
        "role": data["role"],
    }

    mongo.db.users.insert_one(new_user)

    # Create a new token for the new user
    token_payload = {
        "username": data["username"],
        "exp": datetime.now() + timedelta(days=30),
        "role": data["role"],  # Include the 'role' information
    }

    token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

    # Save the token to the database
    mongo.db.users.update_one(
        {"username": data["username"]}, {"$set": {"token": token}}
    )

    return jsonify({"message": "User created successfully!", "token": token})


@app.route("/admin/delete_user/<username>", methods=["DELETE"])
@token_required("admin")
def delete_user(username):
    if not mongo.db.users.find_one({"username": username}):
        return jsonify({"message": "User not found!"}), 404

    mongo.db.users.delete_one({"username": username})

    return jsonify({"message": "User deleted successfully!"})


@app.route("/admin/renew_token/<username>", methods=["PUT"])
@token_required("admin")
def renew_token(username):
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"message": "User not found!"}), 404

    # Create a new token for the user
    token_payload = {
        "username": user["username"],
        "exp": datetime.now() + timedelta(days=30),
        "role": user["role"],  # Include the 'role' information
    }

    token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

    # Save the new token to the database and delete the old one
    mongo.db.users.update_one({"username": username}, {"$set": {"token": token}})

    return jsonify({"new_token": token})


@app.route("/admin/create-one-cre", methods=["GET"])
def create_one_cre():
    # Check if there are no users in the database
    if mongo.db.users.count_documents({}) == 0:
        # Generate a random username, password, and token
        random_username = "".join(random.choices(string.ascii_lowercase, k=8))
        random_password = "".join(
            random.choices(string.ascii_letters + string.digits, k=12)
        )

        new_user = {
            "username": random_username,
            "password": random_password,
            "role": "admin",
        }

        # Insert the new user into the database
        result = mongo.db.users.insert_one(new_user)

        # Get the inserted user document, including the ObjectId
        inserted_user = mongo.db.users.find_one({"_id": result.inserted_id})

        # Convert the ObjectId to a string using json_util
        inserted_user["_id"] = json_util.dumps(inserted_user["_id"])

        # Create a new token for the new user
        token_payload = {
            "username": random_username,
            "exp": datetime.now() + timedelta(days=30),
            "role": "admin",  # Include the 'role' information
        }

        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        # Save the token to the database
        mongo.db.users.update_one(
            {"username": random_username}, {"$set": {"token": token}}
        )

        return jsonify(
            {
                "message": "User created successfully!",
                "user": inserted_user,
                "token": token,
            }
        )

    else:
        return jsonify({"message": "Users already exist in the database!"}), 400


if __name__ == "__main__":
    app.run(debug=True)
