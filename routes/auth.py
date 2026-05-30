from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session)
from models import Restaurant
from routes.helpers import get_restaurant_or_404

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated(slug, *args, **kwargs):
        restaurant = get_restaurant_or_404(slug)
        if session.get("admin_restaurant_id") != restaurant.id:
            return redirect(url_for("auth.login", slug=slug))
        return f(slug, *args, **kwargs)
    return decorated


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def login(slug):
    restaurant = Restaurant.query.filter_by(slug=slug).first()

    if not restaurant:
        return render_template("admin/login.html", slug=slug,
                               error="المطعم غير موجود", restaurant=None)

    if not restaurant.is_approved:
        return render_template("admin/login.html", slug=slug,
                               error="طلبك في انتظار الموافقة من الإدارة", restaurant=restaurant)

    if not restaurant.is_active:
        return render_template("admin/login.html", slug=slug,
                               error="هذا الحساب موقوف، تواصل مع الدعم", restaurant=restaurant)

    if session.get("admin_restaurant_id") == restaurant.id:
        return redirect(url_for("admin.dashboard", slug=slug))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == restaurant.admin_username and restaurant.check_password(password):
            session["admin_restaurant_id"] = restaurant.id
            return redirect(url_for("admin.dashboard", slug=slug))
        error = "اسم المستخدم أو كلمة المرور غير صحيحة"

    return render_template("admin/login.html", slug=slug,
                           restaurant=restaurant, error=error)


@auth_bp.route("/admin/logout")
def logout(slug):
    session.pop("admin_restaurant_id", None)
    return redirect(url_for("auth.login", slug=slug))
