from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List
from sqlalchemy import String, select, delete
from marshmallow import ValidationError, fields
from dotenv import load_dotenv
import os

load_dotenv()
# --- Flask App Setup ---

app = Flask(__name__)

# Database config
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# Database URL string
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# --- Base Class ---
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

# --- Models ---

class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)

    orders: Mapped[List['Orders']] = db.relationship("Orders", back_populates="customer")


# Association Table for Many-to-Many between Orders and Products
order_products = db.Table(
    'order_products',
    Base.metadata,
    db.Column('order_id', db.ForeignKey('orders.id')),
    db.Column('product_id', db.ForeignKey('products.id'))
)


class Orders(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customer.id"), nullable=False)

    customer: Mapped["Customer"] = db.relationship("Customer", back_populates="orders")
    products: Mapped[List['Products']] = db.relationship("Products", secondary=order_products, back_populates="orders")


class Products(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(200), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    orders: Mapped[List['Orders']] = db.relationship("Orders", secondary=order_products, back_populates="products")


# --- Initialize the database ---
with app.app_context():
    db.create_all()
    # db.drop_all()  # Uncomment to reset tables


# --- Schemas ---
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True


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

# --- Customer (GET) ---
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

# --- Product (POST) ---
@app.route("/products", methods=["POST"])
def add_products():
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

# --- Product (GET) ---
@app.route("/products", methods=["GET"])
def get_products():
    query = select(Products)
    results = db.session.execute(query).scalars() #Execute query, and convert row objects into scalar objects (python useable)
    products = results.all() #Packs objects into a list
    return products_schema.jsonify(products)

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
def add_product(order_id, product_id):
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

if __name__ == '__main__':
    app.run(debug=True)
