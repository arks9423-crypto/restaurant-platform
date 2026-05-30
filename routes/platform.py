import re
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, session)
from models import db, Restaurant, SuperAdmin, THEME_DEFAULTS

platform_bp = Blueprint("platform", __name__)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$")


@platform_bp.route("/")
def index():
    return render_template("platform/landing.html")


@platform_bp.route("/login", methods=["GET", "POST"])
def unified_login():
    # Already logged in as super admin → dashboard
    if session.get("super_admin_logged_in"):
        return redirect(url_for("super_admin.dashboard"))

    disambiguation = None
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        chosen_slug = request.form.get("chosen_slug", "").strip()

        # Step 2: user chose a restaurant from disambiguation list
        if chosen_slug:
            r = Restaurant.query.filter_by(
                slug=chosen_slug, admin_username=username,
                is_active=True, is_approved=True
            ).first()
            if r and r.check_password(password):
                session["admin_restaurant_id"] = r.id
                return redirect(url_for("admin.dashboard", slug=r.slug))
            error = "حدث خطأ، حاول مرة أخرى"
            return render_template("platform/login.html", error=error)

        # Step 1: try super admin first
        sa = SuperAdmin.query.filter_by(username=username).first()
        if sa and sa.check_password(password):
            session["super_admin_logged_in"] = True
            return redirect(url_for("super_admin.dashboard"))

        # Try all approved restaurants with this username
        matching = [
            r for r in Restaurant.query.filter_by(
                admin_username=username, is_active=True, is_approved=True
            ).all()
            if r.check_password(password)
        ]

        if len(matching) == 1:
            session["admin_restaurant_id"] = matching[0].id
            return redirect(url_for("admin.dashboard", slug=matching[0].slug))
        elif len(matching) > 1:
            # Same username in multiple restaurants — let user pick
            disambiguation = matching
        else:
            error = "اسم المستخدم أو كلمة المرور غير صحيحة"

    return render_template("platform/login.html", error=error,
                           disambiguation=disambiguation)


@platform_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name_ar = request.form.get("name_ar", "").strip()
        name_en = request.form.get("name_en", "").strip()
        slug = request.form.get("slug", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        admin_username = request.form.get("admin_username", "").strip()
        admin_password = request.form.get("admin_password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not name_ar:
            errors.append("اسم المطعم بالعربي مطلوب")
        if not name_en:
            errors.append("Restaurant name in English is required")
        if not slug or not SLUG_RE.match(slug):
            errors.append("المعرف يجب أن يكون أحرف إنجليزية صغيرة وأرقام وشرطات فقط (3-50 حرف)")
        elif Restaurant.query.filter_by(slug=slug).first():
            errors.append("هذا المعرف مستخدم بالفعل، اختر معرفاً آخر")
        if not phone and not email:
            errors.append("يجب إدخال رقم الهاتف أو البريد الإلكتروني على الأقل")
        if not admin_username:
            errors.append("اسم المستخدم مطلوب")
        if len(admin_password) < 8:
            errors.append("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
        if admin_password != confirm_password:
            errors.append("كلمة المرور وتأكيدها غير متطابقتين")

        if errors:
            return render_template("platform/register.html", errors=errors,
                                   form=request.form)

        restaurant = Restaurant(
            slug=slug,
            name_ar=name_ar,
            name_en=name_en,
            phone=phone or None,
            email=email or None,
            admin_username=admin_username,
            theme_key="amber",
            primary_color=THEME_DEFAULTS["amber"]["primary"],
            secondary_color=THEME_DEFAULTS["amber"]["secondary"],
            is_active=False,
            is_approved=False,
        )
        restaurant.set_password(admin_password)
        db.session.add(restaurant)
        db.session.commit()
        return redirect(url_for("platform.register_pending"))

    return render_template("platform/register.html", errors=[], form={})


@platform_bp.route("/register/pending")
def register_pending():
    return render_template("platform/register_pending.html")


@platform_bp.route("/api/check-slug")
def check_slug():
    slug = request.args.get("slug", "").strip().lower()
    if not slug or not SLUG_RE.match(slug):
        return jsonify({"available": False, "reason": "invalid"})
    exists = Restaurant.query.filter_by(slug=slug).first() is not None
    return jsonify({"available": not exists})
