# Ecommerce API

A RESTful API for managing users, products, and orders in an e-commerce application, built with Flask, MySQL, SQLAlchemy, and Marshmallow.

---

## 🚀 Features

- **User Management:** Create, update, delete, and fetch users (customers).
- **Product Management:** CRUD operations for products.
- **Order Management:** Place orders, link products to orders, manage order contents.
- **Prevents Duplicates:** Prevents duplicate products in any order.
- **Environment Variables:** Secure config using a `.env` file.
- **Fully Tested:** Includes a Postman collection for all endpoints.

---

## 🛠️ Setup Instructions

### 1. Set Up MySQL Database

- Open MySQL Workbench.
- Create a new database:

```sql
CREATE DATABASE ecommerce_api;
```

### 2. Configure Environment

- Set up a Python virtual environment:

```bash
python3 -m venv venv
```

- Activate it:

  - Windows:
    ```bash
    source venv/Scripts/activate
    ```

- Install dependencies:

```bash
pip install -r requirements.txt
```

## 🗃️ Database Models

- **User:** `id`, `name`, `address`, `email (unique)`
- **Product:** `id`, `product_name`, `price`
- **Order:** `id`, `order_date (DateTime)`, `user_id` (FK to User)
- **Order_Product:** Association table with `order_id` and `product_id` (prevents duplicates)

---

## 📦 Marshmallow Schemas

- `UserSchema`
- `ProductSchema`
- `OrderSchema` (with `include_fk = True` to serialize foreign keys)
- Schemas validate and serialize/deserialize input/output for all endpoints.

---

## 🛡️ Security

- **Environment variables:** All secrets (DB password, secret keys) are stored in `.env`.

---

## 📚 API Endpoints

### Users

- `GET /users` — List all users
- `GET /users/<id>` — Get user by ID
- `POST /users` — Create new user
- `PUT /users/<id>` — Update user
- `DELETE /users/<id>` — Delete user

### Products

- `GET /products` — List all products
- `GET /products/<id>` — Get product by ID
- `POST /products` — Create new product
- `PUT /products/<id>` — Update product
- `DELETE /products/<id>` — Delete product

### Orders

- `POST /orders` — Create new order
- `PUT /orders/<order_id>/add_product/<product_id>` — Add product to order (prevents duplicates)
- `DELETE /orders/<order_id>/remove_product/<product_id>` — Remove product from order
- `GET /orders/user/<user_id>` — Get all orders for a user
- `GET /orders/<order_id>/products` — Get all products in an order

---

## 🧪 Testing

- Use the included Postman collection:
  - Import `ecommerce_api.postman_collection.json` into Postman.
  - Set the `{{base_url}}` variable (e.g., `http://localhost:5000`).
  - Each endpoint has a pre-filled example request.
- Use MySQL Workbench to verify database contents after API operations.

---

## 📋 Deliverables

- Python code with all models, schemas, and endpoints.
- Postman collection: `ecommerce_api.postman_collection.json`
- `.env` file for environment variables (not committed).
- `.gitignore` to keep secrets and venv out of git.
- `requirements.txt` for all dependencies.
- README (this file).

---

## 📝 Notes

- Email field on User is unique; attempting to create a duplicate will result in an error.
- The Order_Product table prevents the same product from being added twice to the same order.
- Datetime fields (e.g., `order_date`) must be in the format: `MM.DD.YYYY HH:MM:SS`.

---

## 📖Learnings

- Gained experience in building a RESTful API using Flask.
- Learned how to manage database migrations with Flask-Migrate.
- Understood the importance of input validation and error handling.
- Explored the use of Marshmallow for data serialization and validation.
- Familiarized with Postman for API testing and documentation.
- Utilized MySQL Workbench for database management and queries.
- Implemented security best practices by using environment variables.
- Utilized Postman for API testing and documentation.

---

## Technologies Used

- **Flask:** Web framework for building the API.
- **Flask-SQLAlchemy:** ORM for database interactions.
- **Flask-Migrate:** Database migration tool.
- **Marshmallow:** Object serialization/deserialization and validation.
- **MySQL:** Relational database management system.
- **Postman:** API testing and documentation tool.
- **Python:** Programming language used for the API development.
- **dotenv:** For managing environment variables.
- **Git:** Version control system for managing code changes.
- **GitHub:** For hosting the code repository.
- **CMD:** Command line interface for running commands and scripts.
- **Git Bash:** For running commands and scripts locally.
- **GitHub Copilot:** AI-powered code completion tool for enhancing productivity and assistance in coding tasks.
