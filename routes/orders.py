import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import db, Order, OrderItem, Product
from routes.helpers import get_restaurant_or_404

orders_bp = Blueprint("orders", __name__)


def _generate_order_number():
    suffix = "".join(random.choices(string.digits, k=4))
    return f"ORD-{suffix}"


@orders_bp.route("/order/place", methods=["POST"])
def place_order(slug):
    restaurant = get_restaurant_or_404(slug)

    if not restaurant.is_open:
        return jsonify({"success": False, "message": "المطعم مغلق حالياً"}), 400

    data = request.get_json(silent=True) or {}
    car_plate = (data.get("car_plate") or "").strip()
    car_color = (data.get("car_color") or "").strip()
    car_model = (data.get("car_model") or "").strip() or None
    parking_spot = (data.get("parking_spot") or "").strip() or None
    notes = (data.get("notes") or "").strip() or None
    cart = data.get("cart", [])

    if not car_plate:
        return jsonify({"success": False, "message": "رقم اللوحة مطلوب"}), 400
    if not cart:
        return jsonify({"success": False, "message": "السلة فارغة"}), 400

    order_number = _generate_order_number()
    while Order.query.filter_by(order_number=order_number).first():
        order_number = _generate_order_number()

    order = Order(
        order_number=order_number,
        car_plate=car_plate,
        car_color=car_color,
        car_model=car_model,
        parking_spot=parking_spot,
        notes=notes,
        status="pending",
        restaurant_id=restaurant.id,
    )
    db.session.add(order)
    db.session.flush()

    total = 0
    for item in cart:
        product = Product.query.filter_by(
            id=item.get("id"), restaurant_id=restaurant.id, is_available=True
        ).first()
        if not product:
            continue
        qty = max(1, int(item.get("quantity", 1)))
        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=product.price,
            product_name_ar=product.name_ar,
            product_name_en=product.name_en,
        )
        db.session.add(oi)
        total += float(product.price) * qty

    order.total_amount = total
    db.session.commit()

    return jsonify({"success": True, "order_number": order_number})


@orders_bp.route("/order/status/<order_number>")
def order_status(slug, order_number):
    restaurant = get_restaurant_or_404(slug)
    order = Order.query.filter_by(
        order_number=order_number, restaurant_id=restaurant.id
    ).first_or_404()
    return jsonify({"status": order.status})


@orders_bp.route("/order/confirm/<order_number>")
def confirm(slug, order_number):
    restaurant = get_restaurant_or_404(slug)
    order = Order.query.filter_by(
        order_number=order_number, restaurant_id=restaurant.id
    ).first_or_404()
    return render_template("customer/confirm.html", slug=slug,
                           restaurant=restaurant, order=order)
