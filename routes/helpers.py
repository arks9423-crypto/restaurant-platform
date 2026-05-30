import os
from flask import abort, current_app
from werkzeug.utils import secure_filename
from models import Restaurant


def get_restaurant_or_404(slug: str) -> Restaurant:
    r = Restaurant.query.filter_by(slug=slug, is_active=True, is_approved=True).first()
    if not r:
        abort(404)
    return r


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_upload(file, subfolder: str, slug: str) -> str:
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], slug, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return filename
