from .schemas import mechanic_schema, mechanics_schema, login_schema
from ..service_tickets.schemas import service_tickets_schema
from flask import request, jsonify, g
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db, ServiceTicket
from app.extensions import limiter, cache
from . import mechanics_bp
from app.utils.util import encode_token, token_required


# mechanic login
@mechanics_bp.route("/login", methods=["POST"])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials["email"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalar_one_or_none()

    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id)  # , mechanic.role.role_name

        response = {
            "status": "Success",
            "message": "Successfully logged in.",
            "token": token,
        }

        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


# create new mechanic
@mechanics_bp.route("/", methods=["POST"])
@token_required
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
@token_required
@limiter.limit("100 per day")
@cache.cached(timeout=60)
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    if mechanics:
        return mechanics_schema.jsonify(mechanics)
    return jsonify({"error": "No mechanics found."}), 404


# get one mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
@token_required
@limiter.limit("100 per day")
@cache.cached(timeout=60)
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


# get service tickets for one mechanic
@mechanics_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_tickets():
    mechanic_id = g.mechanic_id
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    tickets = (
        db.session.query(ServiceTicket)
        .join(ServiceTicket.mechanics)
        .filter(Mechanic.id == mechanic_id)
        .all()
    )

    if not tickets:
        return jsonify({"error": "No tickets found for this mechanic"}), 404

    return service_tickets_schema.jsonify(tickets), 200


# get all tickets
@mechanics_bp.route("/all_tickets", methods=["GET"])
@token_required
def all_tickets():
    tickets = db.session.query(ServiceTicket).all()

    if not tickets:
        return jsonify({"error": "No tickets found."}), 404

    return service_tickets_schema.jsonify(tickets), 200


# update one mechanic
@mechanics_bp.route("/", methods=["PUT"])
@token_required
@limiter.limit("7 per day")
def update_mechanic():
    mechanic_id = g.mechanic_id
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
# @mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@mechanics_bp.route("/", methods=["DELETE"])
@token_required
@limiter.limit("7 per day")
def delete_mechanic():
    mechanic_id = g.mechanic_id
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"mechanic {mechanic_id} successfully deleted."}), 200
