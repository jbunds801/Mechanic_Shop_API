from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from datetime import date
from sqlalchemy import select


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:rootpoot666@localhost/mechanic_shop"
)


db = SQLAlchemy()
ma = Marshmallow()

db.init_app(app)
ma.init_app(app)


service_mechanics = db.Table(
    "service_mechanics",
    db.Column("ticket_id", db.Integer, db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanics.id")),
)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(360))
    phone = db.Column(db.String(15), nullable=False)

    tickets = db.relationship("ServiceTicket", back_populates="customer")


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    VIN = db.Column(db.String(17), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    service_desc = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))

    customer = db.relationship("Customer", back_populates="tickets")
    mechanics = db.relationship(
        "Mechanic", secondary=service_mechanics, back_populates="tickets"
    )


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(260), nullable=False)
    email = db.Column(db.String(360), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    salary = db.Column(nullable=False)

    tickets = db.relationship(
        "ServiceTicket", secondary=service_mechanics, back_populates="mechanics"
    )


# ===Schemas===


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = False


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# ===Routes===


# create new customer
@app.route("/customers", methods=["POST"])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data["email"])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account"}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# get all customers
@app.route("/customers", methods=["GET"])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)


# get one customer
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Member not found."}), 400


# update one customer
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 400

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# delete customer
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer_id} successfully deleted."}), 200



with app.app_context():
    db.create_all()
app.run(debug=True)
