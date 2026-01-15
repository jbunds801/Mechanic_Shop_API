from .schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_ticket_schema,
)
from flask import request, jsonify, g
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, db, Mechanic, Customer
from app.extensions import limiter, cache
from . import service_tickets_bp
from app.utils.util import token_required


# create new service ticket
@service_tickets_bp.route("/", methods=["POST"])
@token_required
@limiter.limit("7 per hour")
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, service_ticket_data["customer_id"])
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    query = select(ServiceTicket).where(
        ServiceTicket.VIN == service_ticket_data["VIN"],
        ServiceTicket.service_date == service_ticket_data["service_date"],
    )
    existing_ticket = db.session.execute(query).scalars().first()
    if existing_ticket:
        return (
            jsonify({"error": "A ticket already exsists for this VIN on this date"}),
            400,
        )

    new_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_ticket), 201


# add mechanic to service ticket
@service_tickets_bp.route("/<ticket_id>/assign_mechanic/<mechanic_id>", methods=["PUT"])
# @token_required
@limiter.limit("15 per hour")
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned"}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# remove mechanic from ticket
@service_tickets_bp.route("/<ticket_id>/remove_mechanic/<mechanic_id>", methods=["PUT"])
@token_required
@limiter.limit("7 per hour")
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic not assigned to this ticket"}), 400

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# assign/remove multiple mechanics
@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
# @token_required
@limiter.limit("10 per day")
@cache.cached(timeout=60)
def edit_ticket_mechanics(ticket_id):

    try:
        ticket_edit_mechanics = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    for mechanic_id in ticket_edit_mechanics["add_mechanic_ids"]:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    for mechanic_id in ticket_edit_mechanics["remove_mechanic_ids"]:
        mechanic = db.session.get(Mechanic, mechanic_id)

        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket)


# gets all service tickets
@service_tickets_bp.route("/", methods=["GET"])
# @token_required
@limiter.limit("100 per day")
@cache.cached(timeout=60)
def all_tickets():
    tickets = db.session.query(ServiceTicket).all()

    if tickets:
        return service_tickets_schema.jsonify(tickets), 200

    tickets.sort(key=lambda ticket: ticket.created_at, reverse=True)

    return jsonify({"error": "No tickets found."}), 404


# get one service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@token_required
@limiter.limit("100 per day")
def get_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404


# update service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
@token_required
@limiter.limit("15 per day")
def update_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    if "VIN" in service_ticket_update and not g.mechanic.is_admin:
        return jsonify({"error": "Only admins can update VIN"}), 403

    if not ticket.is_open:
        return jsonify({"error": "Closed tickets cannot be edited"}), 403

    try:
        service_ticket_update = service_ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in service_ticket_update.items():
        setattr(ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# delete service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
@token_required
@limiter.limit("7 per day")
def delete_service_ticket(ticket_id):
    current_mechanic = db.session.get(Mechanic, g.mechanic_id)

    if not current_mechanic:
        return jsonify({"error": "Unauthorized: mechanic not found"}), 403

    if not current_mechanic.is_admin:
        return jsonify({"error": "Unauthorized: admin only"}), 403

    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    db.session.delete(ticket)
    db.session.commit()
    return (
        jsonify({"message": f"Service Ticket {ticket_id} successfully deleted."}),
        200,
    )


@service_tickets_bp.route("/sortbymechanic", methods=["GET"])
# @token_required
@limiter.limit("100 per day")
def sort_by_mechanic():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    grouped_tickets = {}
    for mechanic in mechanics:
        grouped_tickets[mechanic.id] = {
            "mechanic_id": mechanic.id,
            "mechanic_name": mechanic.name,
            "tickets": service_tickets_schema.dump(mechanic.tickets),
        }

    return jsonify(grouped_tickets), 200


""" tickets = sorted(
    tickets, key=lambda ticket: ticket.created_at, reverse=True) """
