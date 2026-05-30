from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class SuperAdmin(db.Model):
    __tablename__ = "super_admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Restaurant(db.Model):
    __tablename__ = "restaurant"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), nullable=False, unique=True, index=True)
    name_ar = db.Column(db.String(120), nullable=False)
    name_en = db.Column(db.String(120), nullable=False)
    logo_filename = db.Column(db.String(256), nullable=True)
    logo_data = db.Column(db.Text, nullable=True)
    primary_color = db.Column(db.String(7), nullable=False, default="#FFB800")
    secondary_color = db.Column(db.String(7), nullable=False, default="#009B8D")
    theme_key = db.Column(db.String(30), nullable=False, default="amber")
    admin_username = db.Column(db.String(50), nullable=False)
    admin_password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address_ar = db.Column(db.String(200), nullable=True)
    address_en = db.Column(db.String(200), nullable=True)
    is_open = db.Column(db.Boolean, nullable=False, default=True)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    categories = db.relationship("Category", backref="restaurant", lazy=True,
                                  cascade="all, delete-orphan")
    products = db.relationship("Product", backref="restaurant", lazy=True,
                                cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="restaurant", lazy=True,
                              cascade="all, delete-orphan")

    def set_password(self, password):
        self.admin_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.admin_password_hash, password)


THEME_DEFAULTS = {
    "amber": {"primary": "#FFB800", "secondary": "#009B8D"},
    "ocean": {"primary": "#38BDF8", "secondary": "#0F172A"},
    "rose":  {"primary": "#F43F5E", "secondary": "#881337"},
    "slate": {"primary": "#6366F1", "secondary": "#334155"},
}


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)

    products = db.relationship("Product", backref="category", lazy=True,
                                cascade="all, delete-orphan")


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(120), nullable=False)
    name_en = db.Column(db.String(120), nullable=False)
    description_ar = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 3), nullable=False)
    image_filename = db.Column(db.String(256), nullable=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), nullable=False, unique=True)
    car_plate = db.Column(db.String(20), nullable=False)
    car_color = db.Column(db.String(40), nullable=False)
    car_model = db.Column(db.String(60), nullable=True)
    parking_spot = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    total_amount = db.Column(db.Numeric(10, 3), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)

    items = db.relationship("OrderItem", backref="order", lazy=True,
                             cascade="all, delete-orphan")


class PushSubscription(db.Model):
    __tablename__ = "push_subscription"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), nullable=False, index=True)
    endpoint = db.Column(db.Text, nullable=False)
    p256dh = db.Column(db.Text, nullable=False)
    auth = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class OrderItem(db.Model):
    __tablename__ = "order_item"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 3), nullable=False)
    product_name_ar = db.Column(db.String(120), nullable=False)
    product_name_en = db.Column(db.String(120), nullable=False)
