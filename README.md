##Mechanic Shop API

A RESTful API for managing customers, mechanics, service tickets, and relationships between them.
Built with Flask, SQLAlchemy, and Marshmallow, this project simulates a mechanic shop workflow including assigning mechanics to service tickets, validating data, and preventing duplicate or invalid records.

##🚀 Features
#Customers
Create new customers
View all customers
View customer by ID
Update customer
Delete customer
Return helpful errors for invalid operations

#Mechanics
Create mechanics with email uniqueness validation
View all mechanics
View mechanic by ID
Update mechanic
Delete mechanic
Return helpful errors for invalid operations

#Service Tickets
Create service tickets with required customer_id
Add/Remove Mechanic from ticket with Mechanic ↔ Service Ticket Relationship
View all service tickets
View a ticket by ID
Update tickets
Delete tickets
Prevent duplicate assignments
Return helpful errors for invalid operations

#🛠️ Tech Stack
Python 3
Flask
Flask SQLAlchemy
Flask Marshmallow
Marshmallow-SQLAlchemy
MySQL
Postman for API testing

#📌 Validations Included
Customer email required + optional unique constraint
Mechanic email must be unique
Service Ticket VIN must be exactly 17 characters
Assign mechanic: prevents duplicate assignments
Remove mechanic: checks if mechanic is assigned before removing

#📂 Project Structure
Mechanic_Shop_API/
│
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── blueprints/
│   │   ├── customers/
│   │   ├── mechanics/
│   │   └── service_tickets/
│   ├── schemas/
│   └── extensions.py
│
├── venv/
├── requirements.txt
└── app.py

#⚙️ Setup Instructions
1. Clone the repository

git clone https://github.com/jbunds801/Mechanic_Shop_API.git
cd Mechanic_Shop_API


2. Create and activate a virtual environment

python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows

3. Install dependencies

pip install -r requirements.txt

4. Configure your database

Create a MySQL database:

CREATE DATABASE mechanic_shop;

Update your database URI in __init__.py:

mysql+pymysql://username:password@localhost/mechanic_shop

5. Run the application

flask run

Server runs at:

http://127.0.0.1:5000
