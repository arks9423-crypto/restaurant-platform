import os
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, current_app)
from models import db, Restaurant, Category, Product, Order, THEME_DEFAULTS
from routes.helpers import get_restaurant_or_404, allowed_file, save_upload
from routes.auth import login_required
import qrcode
import qrcode.image.pil
from io import BytesIO
import base64

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/")
@admin_bp.route("/admin/dashboard")
@login_required
def dashboard(slug):
    restaurant = get_restaurant_or_404(slug)
    pending = Order.query.filter_by(restaurant_id=restaurant.id, status="pending")\
        .order_by(Order.created_at.desc()).all()
    preparing = Order.query.filter_by(restaurant_id=restaurant.id, status="preparing")\
        .order_by(Order.created_at.desc()).all()
    ready = Order.query.filter_by(restaurant_id=restaurant.id, status="ready")\
        .order_by(Order.created_at.desc()).all()
    recent_delivered = Order.query.filter_by(restaurant_id=restaurant.id, status="delivered")\
        .order_by(Order.created_at.desc()).limit(20).all()
    return render_template("admin/dashboard.html", slug=slug, restaurant=restaurant,
                           pending=pending, preparing=preparing, ready=ready,
                           recent_delivered=recent_delivered)


@admin_bp.route("/admin/orders/<int:order_id>/print")
@login_required
def print_order(slug, order_id):
    restaurant = get_restaurant_or_404(slug)
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant.id).first_or_404()
    return render_template("admin/order_print.html", order=order, restaurant=restaurant)


@admin_bp.route("/admin/orders/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(slug, order_id):
    restaurant = get_restaurant_or_404(slug)
    order = Order.query.filter_by(id=order_id, restaurant_id=restaurant.id).first_or_404()
    new_status = request.form.get("status")
    valid = {"pending", "preparing", "ready", "delivered"}
    if new_status in valid:
        order.status = new_status
        db.session.commit()
    return redirect(url_for("admin.dashboard", slug=slug))


# ─── Categories ────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/categories", methods=["GET", "POST"])
@login_required
def categories(slug):
    restaurant = get_restaurant_or_404(slug)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            cat = Category(
                name_ar=request.form["name_ar"].strip(),
                name_en=request.form["name_en"].strip(),
                sort_order=int(request.form.get("sort_order", 0)),
                restaurant_id=restaurant.id,
            )
            db.session.add(cat)
            db.session.commit()
            flash("تمت إضافة القسم", "success")
        elif action == "edit":
            cat = Category.query.filter_by(
                id=int(request.form["cat_id"]), restaurant_id=restaurant.id
            ).first_or_404()
            cat.name_ar = request.form["name_ar"].strip()
            cat.name_en = request.form["name_en"].strip()
            cat.sort_order = int(request.form.get("sort_order", 0))
            db.session.commit()
            flash("تم تعديل القسم", "success")
        elif action == "delete":
            cat = Category.query.filter_by(
                id=int(request.form["cat_id"]), restaurant_id=restaurant.id
            ).first_or_404()
            db.session.delete(cat)
            db.session.commit()
            flash("تم حذف القسم", "danger")
        return redirect(url_for("admin.categories", slug=slug))

    cats = Category.query.filter_by(restaurant_id=restaurant.id)\
        .order_by(Category.sort_order).all()
    return render_template("admin/categories.html", slug=slug,
                           restaurant=restaurant, categories=cats)


# ─── Products ──────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/products", methods=["GET", "POST"])
@login_required
def products(slug):
    restaurant = get_restaurant_or_404(slug)
    cats = Category.query.filter_by(restaurant_id=restaurant.id)\
        .order_by(Category.sort_order).all()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            image_filename = None
            if "image" in request.files and request.files["image"].filename:
                f = request.files["image"]
                if allowed_file(f.filename):
                    image_filename = save_upload(f, "products", slug)
            product = Product(
                name_ar=request.form["name_ar"].strip(),
                name_en=request.form["name_en"].strip(),
                description_ar=request.form.get("description_ar", "").strip() or None,
                description_en=request.form.get("description_en", "").strip() or None,
                price=float(request.form["price"]),
                image_filename=image_filename,
                is_available="is_available" in request.form,
                category_id=int(request.form["category_id"]),
                restaurant_id=restaurant.id,
            )
            db.session.add(product)
            db.session.commit()
            flash("تمت إضافة المنتج", "success")

        elif action == "edit":
            product = Product.query.filter_by(
                id=int(request.form["product_id"]), restaurant_id=restaurant.id
            ).first_or_404()
            product.name_ar = request.form["name_ar"].strip()
            product.name_en = request.form["name_en"].strip()
            product.description_ar = request.form.get("description_ar", "").strip() or None
            product.description_en = request.form.get("description_en", "").strip() or None
            product.price = float(request.form["price"])
            product.is_available = "is_available" in request.form
            product.category_id = int(request.form["category_id"])
            if "image" in request.files and request.files["image"].filename:
                f = request.files["image"]
                if allowed_file(f.filename):
                    product.image_filename = save_upload(f, "products", slug)
            db.session.commit()
            flash("تم تعديل المنتج", "success")

        elif action == "delete":
            product = Product.query.filter_by(
                id=int(request.form["product_id"]), restaurant_id=restaurant.id
            ).first_or_404()
            db.session.delete(product)
            db.session.commit()
            flash("تم حذف المنتج", "danger")

        elif action == "toggle":
            product = Product.query.filter_by(
                id=int(request.form["product_id"]), restaurant_id=restaurant.id
            ).first_or_404()
            product.is_available = not product.is_available
            db.session.commit()

        return redirect(url_for("admin.products", slug=slug))

    prods = Product.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template("admin/products.html", slug=slug, restaurant=restaurant,
                           categories=cats, products=prods)


# ─── Settings ──────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/settings", methods=["GET", "POST"])
@login_required
def settings(slug):
    restaurant = get_restaurant_or_404(slug)
    if request.method == "POST":
        section = request.form.get("section")

        if section == "info":
            restaurant.name_ar = request.form["name_ar"].strip()
            restaurant.name_en = request.form["name_en"].strip()
            restaurant.phone = request.form.get("phone", "").strip() or None
            restaurant.address_ar = request.form.get("address_ar", "").strip() or None
            restaurant.address_en = request.form.get("address_en", "").strip() or None
            restaurant.is_open = "is_open" in request.form
            if "logo" in request.files and request.files["logo"].filename:
                f = request.files["logo"]
                if allowed_file(f.filename):
                    import base64 as _b64
                    logo_bytes = f.read()
                    mime = f.content_type or "image/jpeg"
                    restaurant.logo_data = f"data:{mime};base64,{_b64.b64encode(logo_bytes).decode()}"
            db.session.commit()
            flash("تم حفظ معلومات المطعم", "success")

        elif section == "branding":
            theme_key = request.form.get("theme_key", "amber")
            if theme_key in THEME_DEFAULTS:
                restaurant.theme_key = theme_key
                restaurant.primary_color = request.form.get(
                    "primary_color", THEME_DEFAULTS[theme_key]["primary"])
                restaurant.secondary_color = request.form.get(
                    "secondary_color", THEME_DEFAULTS[theme_key]["secondary"])
            db.session.commit()
            flash("تم حفظ إعدادات الثيم والألوان", "success")

        elif section == "credentials":
            new_username = request.form.get("new_username", "").strip()
            new_password = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")
            if new_username:
                restaurant.admin_username = new_username
            if new_password:
                if new_password != confirm:
                    flash("كلمتا المرور غير متطابقتين", "danger")
                    return redirect(url_for("admin.settings", slug=slug))
                if len(new_password) < 8:
                    flash("كلمة المرور يجب أن تكون 8 أحرف على الأقل", "danger")
                    return redirect(url_for("admin.settings", slug=slug))
                restaurant.set_password(new_password)
            db.session.commit()
            flash("تم تحديث بيانات الدخول", "success")

        return redirect(url_for("admin.settings", slug=slug))

    return render_template("admin/settings.html", slug=slug, restaurant=restaurant,
                           theme_defaults=THEME_DEFAULTS)


# ─── QR Code ───────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/qrcode")
@login_required
def qrcode_page(slug):
    restaurant = get_restaurant_or_404(slug)
    menu_url = request.host_url.rstrip("/") + url_for("menu.menu_page", slug=slug)

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(menu_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=restaurant.secondary_color, back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render_template("admin/qrcode.html", slug=slug, restaurant=restaurant,
                           qr_b64=qr_b64, menu_url=menu_url)
