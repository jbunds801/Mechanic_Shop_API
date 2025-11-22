from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from app.extensions import limiter
from . import mechanics_bp


# create new mechanic
@mechanics_bp.route("/", methods=["POST"])
@limiter.limit("7 per day")
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    existing_mechanic = db.session.execute(query).scalars().first()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with an account"}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


# get all mechanics
@mechanics_bp.route("/", methods=["GET"])
@limiter.limit("100 per day")
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    if mechanics:
        return mechanics_schema.jsonify(mechanics)
    return jsonify({"error": "No mechanics found."}), 404


# get one mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
@limiter.limit("100 per day")
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


# update one mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("7 per day")
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# delete mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@limiter.limit("7 per day")
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"mechanic {mechanic_id} successfully deleted."}), 200
