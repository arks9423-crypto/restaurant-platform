from flask import Blueprint, render_template
from models import Category, Product
from routes.helpers import get_restaurant_or_404

menu_bp = Blueprint("menu", __name__)


@menu_bp.route("/menu")
def menu_page(slug):
    restaurant = get_restaurant_or_404(slug)
    categories = (
        Category.query.filter_by(restaurant_id=restaurant.id)
        .order_by(Category.sort_order)
        .all()
    )
    for cat in categories:
        cat.available_products = [
            p for p in cat.products if p.is_available
        ]
    return render_template("customer/menu.html", slug=slug,
                           restaurant=restaurant, categories=categories)
