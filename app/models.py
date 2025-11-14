from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from datetime import date
from sqlalchemy import select


db = SQLAlchemy()


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
