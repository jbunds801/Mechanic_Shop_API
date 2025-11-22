from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import ServiceTicket, db, Mechanic, Customer
from app.extensions import limiter, cache
from . import service_tickets_bp


# create new service ticket
@service_tickets_bp.route("/", methods=["POST"])
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
@limiter.limit("7 per hour")
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({"error": "Ticket or mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic not assigned to this ticket"})

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200


# gets all service tickets
@service_tickets_bp.route("/", methods=["GET"])
@limiter.limit("100 per day")
@cache.cached(timeout=60)
def get_service_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()

    if tickets:
        return service_tickets_schema.jsonify(tickets)
    return jsonify({"error": "No tickets found."}), 404


# get one service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@limiter.limit("100 per day")
def get_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if ticket:
        return service_ticket_schema.jsonify(ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404


# update service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
@limiter.limit("15 per day")
def update_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in service_ticket_data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# delete service ticket
@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
@limiter.limit("7 per day")
def delete_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    db.session.delete(ticket)
    db.session.commit()
    return (
        jsonify({"message": f"Service Ticket {ticket_id} successfully deleted."}),
        200,
    )
