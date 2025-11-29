# Mechanic Shop API

A RESTful API built with **Flask**, **SQLAlchemy**, and **Marshmallow** for managing a mechanic shop's core operations — including **customers**, **mechanics**, and **service tickets**.

This project demonstrates relational modeling, validation, and CRUD operations across multiple entities, plus many-to-many associations between mechanics and service tickets.

---

## 🚀 Features

### **Customers**

* Create, update, delete, and retrieve customers
* Prevent duplicate emails
* Connect customers to their service tickets

### **Mechanics**

* Create and manage mechanics
* Prevent duplicate mechanic emails
* Assign or remove mechanics from service tickets

### **Service Tickets**

* Create and update service tickets
* Assign customers and mechanics
* VIN length validation
* Many-to-many relationship between tickets and mechanics

---

## 📁 Project Structure

```
Mechanic_Shop_API/
│
├── app/
│   ├── __init__.py        # Application factory
│   ├── models.py          # SQLAlchemy models
│   ├── extensions.py      # db and ma instances
│   ├── blueprints/
│   │   ├── customers/
│   │   │   ├── routes.py
│   │   │   ├── schemas.py
│   │   ├── mechanics/
│   │   │   ├── routes.py
│   │   │   ├── schemas.py
│   │   ├── service_tickets/
│   │       ├── routes.py
│   │       ├── schemas.py
│   └── ...
│
├── migrations/            # Alembic migrations
├── venv/                  # Virtual environment
├── requirements.txt
├── README.md
└── run.py
```

---

## 🛠️ Installation & Setup

### 1. **Clone the Repository**

```bash
git clone https://github.com/jbunds801/Mechanic_Shop_API.git
cd Mechanic_Shop_API
```

### 2. **Create a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Set Up the Database**

Update your MySQL connection string in:

```
app/__init__.py
```

Example:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@localhost/mechanic_shop"
```

Run migrations:

```bash
flask db upgrade
```

### 5. **Start the Server**

```bash
flask run
```

The API will run at:

```
http://127.0.0.1:5000/
```

---

## 📬 API Endpoints

### **Customers** `/customers`

| Method | Endpoint | Description        |
| ------ | -------- | ------------------ |
| GET    | `/`      | Get all customers  |
| GET    | `/<id>`  | Get customer by ID |
| POST   | `/`      | Create customer    |
| PUT    | `/<id>`  | Update customer    |
| DELETE | `/<id>`  | Delete customer    |

---

### **Mechanics** `/mechanics`

| Method | Endpoint         | Description        |
| ------ | ---------------- | ------------------ |
| GET    | `/`              | Get all mechanics  |
| GET    | `/<id>`          | Get mechanic by ID |
| POST   | `/`              | Create mechanic    |
| PUT    | `/<mechanic_id>` | Update mechanic    |
| DELETE | `/<mechanic_id>` | Delete mechanic    |

#### Mechanic ↔ Ticket Relationship

| Method | Endpoint                                                     | Description                 |
| ------ | ------------------------------------------------------------ | --------------------------- |
| PUT    | `/service_tickets/<ticket_id>/assign-mechanic/<mechanic_id>` | Assign mechanic to ticket   |
| PUT    | `/service_tickets/<ticket_id>/remove_mechanic/<mechanic_id>` | Remove mechanic from ticket |

---

### **Service Tickets** `/service_tickets`

| Method | Endpoint       | Description      |
| ------ | -------------- | ---------------- |
| GET    | `/`            | Get all tickets  |
| GET    | `/<ticket_id>` | Get ticket by ID |
| POST   | `/`            | Create ticket    |
| PUT    | `/<ticket_id>` | Update ticket    |
| DELETE | `/<ticket_id>` | Delete ticket    |

---

## 🧪 Sample JSON Bodies

### Create Customer

```json
{
  "first_name": "Sarah",
  "last_name": "Connor",
  "email": "sarah@example.com"
}
```

### Create Mechanic

```json
{
  "first_name": "Kyle",
  "last_name": "Reese",
  "email": "kyle.reese@example.com"
}
```

### Create Service Ticket

```json
{
  "description": "Oil change",
  "VIN": "1HGCM82633A004352",
  "customer_id": 1
}
```

---

## 🧰 Technologies Used

* **Flask**
* **Flask SQLAlchemy**
* **Marshmallow + marshmallow-sqlalchemy**
* **MySQL**
* **Flask-Migrate / Alembic**

---

## 📌 Notes

* VIN field enforces a strict 17-character limit.
* Unique constraints enforced at DB and schema level.
* Many-to-many table used for mechanics ↔ service tickets.

---

## 📜 License

MIT License — free to use and modify.

---
