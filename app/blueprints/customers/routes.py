from .schemas import customer_schema, customers_schema
from flask import request, jsonify, g
from marshmallow import ValidationError
from sqlalchemy import select, func
from app.models import Customer, Mechanic, db
from app.extensions import limiter
from app.extensions import cache
from . import customers_bp
from app.utils.util import token_required


# create new customer
@customers_bp.route("/", methods=["POST"])
@token_required
@limiter.limit("15 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data["email"])
    existing_customer = db.session.execute(query).scalars().first()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account"}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# get all customers
@customers_bp.route("/", methods=["GET"])
# @token_required
@limiter.limit("100 per day")
def get_customers():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        query = select(Customer)
        paginated = db.paginate(query, page=page, per_page=per_page)

        sorted_customers = sorted(paginated.items, key=lambda customer: customer.name)

        return (
            jsonify(
                {
                    "customers": customers_schema.dump(sorted_customers),
                    "total": paginated.total,
                    "pages": paginated.pages,
                    "current_page": page,
                }
            ),
            200,
        )

    except (ValueError, TypeError):
        customers = db.session.query(Customer).all()

        if customers:
            return customers_schema.jsonify(customers), 200

        return jsonify({"error": "No customers found."}), 404


# get one customer
@customers_bp.route("/<int:customer_id>", methods=["GET"])
@token_required
@limiter.limit("100 per day")
@cache.cached(timeout=300)
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


# search for customer by phone number
@customers_bp.route("/search", methods=["GET"])
# @token_required
def search_customer():
    phone = request.args.get("phone")

    if not phone:
        return jsonify({"error": "Phone number required."}), 400

    query = select(Customer).where(
        func.replace(Customer.phone, "-", "").like(f"%{phone}%")
    )
    customers = db.session.execute(query).scalars().all()

    if customers:
        return customers_schema.jsonify(customers)
    return jsonify({"error": "No customers found."}), 404


# update one customer
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@token_required
@limiter.limit("15 per day")
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer_data = customers_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customers_schema.jsonify(customer), 200


# delete customer
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@token_required
@limiter.limit("7 per day")
def delete_customer(customer_id):
    current_mechanic = db.session.get(Mechanic, g.mechanic_id)

    if not current_mechanic:
        return jsonify({"error": "Unauthorized: mechanic not found"}), 403

    if not current_mechanic.is_admin:
        return jsonify({"error": "Unauthorized: admin only"}), 403

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer_id} successfully deleted."}), 200


""" @customers_bp.route("/debug", methods=["GET"])
def debug_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return jsonify({"count": len(customers), "phones": [c.phone for c in customers]}) """
