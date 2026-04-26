from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

""" 
service_mechanics = db.Table(
    "service_mechanics",
    db.Column(
        "ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True
    ),
    db.Column(
        "mechanic_id", db.Integer, db.ForeignKey("mechanics.id"), primary_key=True
    ),
)
 """

class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(360))
    phone = db.Column(db.String(15), nullable=False)

    tickets = db.relationship("ServiceTicket", back_populates="customer")


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    VIN = db.Column(db.String(17), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    service_date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    service_desc = db.Column(db.String(255), nullable=False)
    is_open = db.Column(db.Boolean, default=True, nullable=False)

    customer = db.relationship("Customer", back_populates="tickets")
    mechanics = db.relationship(
        "MechanicServiceTicket", back_populates="ticket"
    )


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(260), nullable=False, unique=True)
    email = db.Column(db.String(360), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    tickets = db.relationship(
        "MechanicServiceTicket", back_populates="mechanic"
    )


class MechanicServiceTicket(db.Model):
    __tablename__ = "mechanic_service_tickets"
     
    id = db. Column(db.Integer, primary_key=True)
    mechanic_id = db.Column(db.Integer, db.ForeignKey("mechanics.id"), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("service_tickets.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    started_at = db.Column(db.Date, nullable=True)
     
    mechanic = db.relationship("Mechanic", back_populates="tickets")
    ticket = db.relationship("ServiceTicket", back_populates="mechanics")   
    
    
