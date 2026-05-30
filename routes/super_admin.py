from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from models import db, SuperAdmin, Restaurant, Order

super_admin_bp = Blueprint("super_admin", __name__)


def super_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("super_admin_logged_in"):
            return redirect(url_for("platform.unified_login"))
        return f(*args, **kwargs)
    return decorated


@super_admin_bp.route("/login")
def login():
    # Redirect old /platform/login URL to unified login
    return redirect(url_for("platform.unified_login"))


@super_admin_bp.route("/logout")
def logout():
    session.pop("super_admin_logged_in", None)
    return redirect(url_for("super_admin.login"))


@super_admin_bp.route("/dashboard")
@super_login_required
def dashboard():
    pending = Restaurant.query.filter_by(is_approved=False).order_by(
        Restaurant.created_at.desc()).all()
    active = Restaurant.query.filter_by(is_approved=True, is_active=True).order_by(
        Restaurant.created_at.desc()).all()
    inactive = Restaurant.query.filter_by(is_approved=True, is_active=False).order_by(
        Restaurant.created_at.desc()).all()

    order_counts = {}
    for r in active + inactive:
        order_counts[r.id] = Order.query.filter_by(restaurant_id=r.id).count()

    return render_template("platform/super_admin.html",
                           pending=pending, active=active, inactive=inactive,
                           order_counts=order_counts)


@super_admin_bp.route("/restaurants/<int:restaurant_id>/approve", methods=["POST"])
@super_login_required
def approve(restaurant_id):
    r = Restaurant.query.get_or_404(restaurant_id)
    r.is_approved = True
    r.is_active = True
    db.session.commit()
    flash(f"تم تفعيل مطعم {r.name_ar}", "success")
    return redirect(url_for("super_admin.dashboard"))


@super_admin_bp.route("/restaurants/<int:restaurant_id>/deactivate", methods=["POST"])
@super_login_required
def deactivate(restaurant_id):
    r = Restaurant.query.get_or_404(restaurant_id)
    r.is_active = False
    db.session.commit()
    flash(f"تم إيقاف مطعم {r.name_ar}", "warning")
    return redirect(url_for("super_admin.dashboard"))


@super_admin_bp.route("/restaurants/<int:restaurant_id>/activate", methods=["POST"])
@super_login_required
def activate(restaurant_id):
    r = Restaurant.query.get_or_404(restaurant_id)
    r.is_active = True
    db.session.commit()
    flash(f"تم إعادة تفعيل مطعم {r.name_ar}", "success")
    return redirect(url_for("super_admin.dashboard"))


@super_admin_bp.route("/restaurants/<int:restaurant_id>/reject", methods=["POST"])
@super_login_required
def reject(restaurant_id):
    r = Restaurant.query.get_or_404(restaurant_id)
    db.session.delete(r)
    db.session.commit()
    flash("تم رفض وحذف طلب التسجيل", "danger")
    return redirect(url_for("super_admin.dashboard"))
