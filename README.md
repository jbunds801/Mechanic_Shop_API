# Mechanic Shop API

A RESTful API built with **Flask**, **SQLAlchemy**, and **Marshmallow** for managing a mechanic shop's core operations — including **customers**, **mechanics**, and **service tickets**.

This project demonstrates relational modeling, validation, and CRUD operations across multiple entities, plus many-to-many associations between mechanics and service tickets.

---

## 🚀 Features

### **Customers**

* Create, update, delete, and retrieve customers
* Prevent duplicate emails
* Connect customers to their service tickets
* **Pagination support** on list endpoint with customizable page size
* **Search by phone number** with hyphen-insensitive matching
* Sorted results by customer name

### **Mechanics**

* Create and manage mechanics
* Prevent duplicate mechanic emails
* Assign or remove mechanics from service tickets
* **View mechanics sorted by ticket count** (most active first)
* JWT token-based authentication for secure operations

### **Service Tickets**

* Create and update service tickets
* Business rules, data integrity and API safety with mechanic login requirements and admin-only operations
* Assign multiple mechanics and remove mechanics from tickets
* VIN length validation (17 characters)
* Many-to-many relationship between tickets and mechanics
* **Pagination support** on list endpoint with customizable page size
* **Search by customer phone number** with hyphen-insensitive matching
* **Sorted results** by creation date (newest first)

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
├── venv/                  # Virtual environment
|── app.py
├── README.md
├── requirements.txt
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

| Method | Endpoint  | Description                              | Auth Required |
| ------ | ----------| ---------------------------------------- | ------------- |
| GET    | `/`       | Get all customers (paginated)            | ✓             |
| GET    | `/<id>`   | Get customer by ID                       | ✓             |
| GET    | `/search` | Search customers by phone number         | ✓             |
| POST   | `/`       | Create customer                          | ✓             |
| PUT    | `/<id>`   | Update customer                          | ✓             |
| DELETE | `/<id>`   | Delete customer                          | ✓ (Admin)     |

**Query Parameters:**
- `page` (default: 1) - Page number for pagination
- `per_page` (default: 5) - Results per page
- `phone` - Phone number to search (e.g., `/search?phone=8018890000`)

---

### **Mechanics** `/mechanics`

| Method | Endpoint            | Description                              | Auth Required |
| ------ | ------------------- | ---------------------------------------- | ------------- |
| GET    | `/`                 | Get all mechanics                        | ✓             |
| GET    | `/<id>`             | Get mechanic by ID                       | ✓             |
| GET    | `/sort_by_mechanic` | Get mechanics sorted by ticket count     | ✓             |
| POST   | `/`                 | Create mechanic                          | ✓             |
| PUT    | `/<id>`             | Update mechanic                          | ✓             |
| DELETE | `/<id>`             | Delete mechanic                          | ✓ (Admin)     |

#### Mechanic ↔ Ticket Assignment

| Method | Endpoint                                                     | Description                  | Auth Required |
| ------ | ------------------------------------------------------------ | ---------------------------- | ------------- |
| PUT    | `/service_tickets/<ticket_id>/assign_mechanic/<mechanic_id>` | Assign mechanic to ticket    | ✓             |
| PUT    | `/service_tickets/<ticket_id>/remove_mechanic/<mechanic_id>` | Remove mechanic from ticket  | ✓             |

---

### **Service Tickets** `/service_tickets`

| Method | Endpoint                                      | Description                                 | Auth Required | Rate Limit |
| ------ | --------------------------------------------- | ------------------------------------------- | ------------- | ---------- |
| GET    | `/`                                           | Get all tickets (paginated, sorted)         | ✓             | 100/day    |
| GET    | `/<ticket_id>`                                | Get ticket by ID                            | ✓             |            |
| GET    | `/tickets_by_customer`                        | Search tickets by customer phone            | ✓             |            |
| POST   | `/`                                           | Create ticket                               | ✓             | 7/hour     |
| PUT    | `/<ticket_id>`                                | Update ticket                               | ✓             |            |
| PUT    | `/<ticket_id>/assign_mechanic/<mechanic_id>`  | Assign mechanic to ticket                   | ✓             |            |
| PUT    | `/<ticket_id>/remove_mechanic/<mechanic_id>`  | Remove mechanic from ticket                 | ✓             |            |
| PUT    | `/<ticket_id>/edit`                           | Add/remove multiple mechanics to ticket     | ✓             |            |
| DELETE | `/<ticket_id>`                                | Delete ticket                               | ✓ (Admin)     |            |

**Query Parameters:**
- `page` (default: 1) - Page number for pagination
- `per_page` (default: 5) - Results per page
- `phone` - Phone number to search customer (e.g., `/tickets_by_customer?phone=8018890000`)

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
  "name": "Kyle Reese",
  "email": "kyle.reese@example.com",
  "phone": "8889991111",
  "salary": 65000,
  "password": "password"
}
```

### Create Service Ticket

```json
{
  "VIN": "1HGCM82633A004352",
  "service_date": "2025-11-16",
  "service_desc": "Oil change",
  "customer_id": 1
}
```

---

## 🔐 Authentication & Authorization

### JWT Token-Based Auth

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

**How to get a token:**
1. Create a mechanic account: `POST /mechanics` with name, email, phone, salary, and password
2. The system generates a JWT token (valid for 10 hours)
3. Include the token in all subsequent requests

**Admin-Only Operations:**
- Deleting customers (`DELETE /customers/<id>`)
- Deleting mechanics (`DELETE /mechanics/<id>`)
- Deleting service tickets (`DELETE /service_tickets/<id>`)

Admin status is determined by mechanic role in the database.

### Rate Limiting

* **Service Ticket Creation:** 7 requests per hour per user
* **General API:** 100 requests per day for list endpoints
* Returns `429 Too Many Requests` when limit is exceeded

---

## 📊 Pagination

All list endpoints support pagination with the following query parameters:

- **`page`** (default: 1) - The page number to retrieve
- **`per_page`** (default: 5) - Number of results per page

**Example requests:**
```
GET /customers?page=1&per_page=10
GET /service_tickets?page=2&per_page=20
```

**Response format:**
```json
{
  "customers": [...],
  "total": 42,
  "pages": 5,
  "current_page": 1
}
```

---

## 🔍 Search & Filtering

### Customer Search
- **Endpoint:** `GET /customers/search?phone=<phone_number>`
- **Format:** Phone number without formatting (e.g., `8018890000` or `801-889-0000`)
- Returns customers matching the phone number (hyphen-insensitive)

### Service Ticket Search
- **Endpoint:** `GET /service_tickets/tickets_by_customer?phone=<phone_number>`
- **Format:** Phone number without formatting
- Returns all service tickets for customers matching the phone number

### Sorting
- **Customers list:** Sorted by customer name (A-Z)
- **Service Tickets list:** Sorted by creation date (newest first)
- **Mechanics by activity:** `GET /mechanics/sort_by_mechanic` returns mechanics sorted by ticket count (most active first)

---

## 🧰 Technologies Used

* **Flask 3.1.2** - Web framework
* **Flask-SQLAlchemy 3.1.1** - ORM and database management
* **Marshmallow 4.1.0** - Data serialization and validation
* **MySQL** - Relational database
* **Flask-Limiter** - Rate limiting for API protection
* **Flask-Caching** - Caching mechanism for optimized endpoints
* **python-jose 3.5.0** - JWT token generation and validation

---

## 📌 Notes & Recent Updates

### Core Functionality
* VIN field enforces a strict 17-character limit
* Unique constraints enforced at both DB and schema level
* Many-to-many table (`service_mechanics`) for flexible mechanic ↔ service ticket associations

### Recent Enhancements
* **Pagination implemented** across all list endpoints (customers, service tickets) with configurable page sizes
* **Phone search functionality** with hyphen-insensitive SQL queries (strips formatting automatically)
* **Lambda-based sorting** for consistent ordering across list endpoints:
  - Customers sorted by name
  - Service tickets sorted by creation date (descending)
  - Mechanics sortable by ticket count (most active first)
* **Rate limiting applied** to prevent abuse (7/hour for ticket creation, 100/day for general list endpoints)
* **JWT authentication** with token-based authorization on all protected endpoints
* **Optimized caching strategy** - static endpoints cached, paginated/search endpoints bypass cache for accuracy
* **Environment improvements** - resolved import/package management issues with virtual environment setup

### Database Constraints
* `Customer.email` - UNIQUE constraint
* `Mechanic.email` - UNIQUE constraint
* `ServiceTicket.VIN` - 17 character validation
* Foreign keys enforce referential integrity

### Best Practices Implemented
* Blueprint-based route organization for scalability
* Marshmallow schema validation on all inputs
* Try-except error handling with graceful fallbacks
* Proper HTTP status codes (200, 400, 401, 403, 404, 429, 500)
* Token required decorator for route protection

---

## 📜 License

MIT License — free to use and modify.

---
