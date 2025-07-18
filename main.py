from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, fields
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, select, delete, Float, DateTime, ForeignKey, Table, Column
from datetime import date
from typing import List
from dotenv import load_dotenv
import os

# --- Load Environment Variables ---
load_dotenv()
# --- Flask App Setup ---
app = Flask(__name__)

# ---Database config ---
# Loads details from .env file
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# Database URL string
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save resources

# --- Base Class ---
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

# --- Models ---

# Customer Table
class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True) # autoincrement is set to default for primary keys
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)

    orders: Mapped[List['Orders']] = db.relationship("Orders", back_populates="customer")




# --- Products Table ---
class Products(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    # MARK: FIXME: Use String/Float instead of db.String due to imports. Test prior to utilizing
    product_name: Mapped[str] = mapped_column(db.String(200), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    orders: Mapped[List['Orders']] = db.relationship("Orders", secondary=order_products, back_populates="products")


# Association Table for Many-to-Many between Orders and Products
order_products = Table(
    'order_products',
    Base.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True),  # Composite PK: prevents duplicate entries
)

# --- Orders Table ---
class Orders(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customer.id"), nullable=False)

    customer: Mapped["Customer"] = db.relationship("Customer", back_populates="orders")
    products: Mapped[List['Products']] = db.relationship("Products", secondary=order_products, back_populates="orders")

# --- Initialize the database ---
with app.app_context():
    db.create_all()
    # db.drop_all()  # Uncomment to reset tables


# --- Marshmallow Schemas ---
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True  # Allows loading instances from the database


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products
        load_instance = True  # Allows loading instances from the database


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True
        load_instance = True
        order_date = fields.Date(
            required=True, format='%m.%d.%Y', 
            error_messages={
                'required': 'Order date is required.',
                'invalid': 'Invalid date format. Please use MM.DD.YYYY.'
            }
        )  # Ensure date is in the correct format


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


# --- Routes ---
@app.route('/')
def home():
    return "Home"

# ----------- Customer Endpoints -----------

# --- Customers (GET) ---
@app.route("/customers", methods=["GET"])
def get_customers():
    query = select(Customer)
    results = db.session.execute(query).scalars() # Execute query, and convert row objects into scalar objects (python useable)
    customers = results.all() # Packs objects into a list
    return customers_schema.jsonify(customers)

# --- Customer (GET by ID) ---
@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    query = select(Customer).where(Customer.id == id)
    result = db.session.execute(query).scalars().first()  # Get the first result
   
    if result is None:
        return jsonify({"error": "Customer not found"}), 404

    return customer_schema.jsonify(result)

# --- Customer (POST) ---
@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_customer = Customer(
        name=customer_data["name"],
        email=customer_data["email"],
        address=customer_data["address"]
    )

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({
        "Message": "Customer created successfully",
        "customer": customer_schema.dump(new_customer)
    }), 201
    
# --- Customer (PUT) ---
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer_data = customer_schema.load(request.json, instance=customer)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.commit()

    return jsonify({
        "Message": "Customer updated successfully",
        "customer": customer_schema.dump(customer)
    }), 200

# --- Customer (DELETE) ---
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"Message": "Customer deleted successfully"}), 200

# ----------- Product Endpoints -----------

# --- Products (GET) ---
@app.route("/products", methods=["GET"])
def get_products():
    query = select(Products)
    results = db.session.execute(query).scalars() #Execute query, and convert row objects into scalar objects (python useable)
    products = results.all() #Packs objects into a list
    return products_schema.jsonify(products)

# --- Product (GET by ID) ---
@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    query = select(Products).where(Products.id == id)
    result = db.session.execute(query).scalars().first()
    if result is None:
        return jsonify({"error": "Product not found"}), 404
    return product_schema.jsonify(result)

# --- Product (POST) ---
@app.route("/products", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_product = Products(
        product_name=product_data["product_name"],
        price=product_data["price"]
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "Message": "Product created successfully",
        "product": product_schema.dump(new_product)
    }), 201

# --- Product (PUT) ---
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = db.session.get(Products, id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        product_data = product_schema.load(request.json, instance=product)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.commit()

    return jsonify({
        "Message": "Product updated successfully",
        "product": product_schema.dump(product)
    }), 200
    
# --- Product (DELETE) ---
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = db.session.get(Products, id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"Message": "Product deleted successfully"}), 200

# ----------- Order Endpoints -----------

#----Create Order (POST)---
@app.route("/orders", methods=["POST"])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    # Retrieve the customer by id
    customer = db.session.get(Customer, order_data["customer_id"])
    
    # check if customer exists
    if customer:
        new_order = Orders(
            order_date=order_data["order_date"],
            customer_id=order_data["customer_id"]
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "Message": "Order created successfully",
            "order": order_schema.dump(new_order)
        }), 201
        
    else:
        return jsonify({"error": "Customer not found"}), 400
    
#----Add Product to Order (PUT)---
@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Orders, order_id)  # Can use .get when querying using primary key
    product = db.session.get(Products, product_id)
    
    if order and product: #Check to see if both exist
        if product not in order.products: #Ensure the product is not already in the order
            order.products.append(product) #Create relationship from order to product
            db.session.commit()  # Commit the changes to the database
            return jsonify({"Message": "Product added to order successfully"}), 200
        else:
            return jsonify({"error": "Product already in order"}), 400
    else:
        return jsonify({"error": "Order or Product not found"}), 404
    
#----Get Order by ID (GET)---
@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    order = db.session.get(Orders, id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return order_schema.jsonify(order)

#---- Get Orders for Customer (GET) ---
@app.route("/customers/<int:customer_id>/orders", methods=["GET"])
def get_orders_for_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    orders = db.session.query(Orders).filter_by(customer_id=customer_id).all()
    return orders_schema.jsonify(orders)

#----Get Products in Order (GET)---
@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_products_in_order(order_id):
    order = db.session.get(Orders, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    return products_schema.jsonify(order.products, many=True)

if __name__ == '__main__':
    app.run(debug=True)
