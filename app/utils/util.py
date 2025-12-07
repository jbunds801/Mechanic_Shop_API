from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta, timezone
from jose import jwt
import jose

SECRET_KEY = "a secret key"


def encode_token(mechanic_id):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(mechanic_id),
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

            if not token:
                return jsonify({"message": "Missing Token"}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                g.mechanic_id = int(data["sub"])

                print("DEBUG: g.mechanic_id =", g.mechanic_id)

            except jose.exceptions.ExpiredSignatureError:
                return jsonify({"message": "Expired Token"}), 401
            except jose.exceptions.JWTError:
               
                return jsonify({"message": "Invalid Token"}), 401

            return f(*args, **kwargs)

        else:
            return jsonify({"message": "You must be logged in to access."}), 401

    return decorated