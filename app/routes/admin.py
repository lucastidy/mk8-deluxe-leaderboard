# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Leaderboard
from .. import db
import os

admin = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@admin.route("/pending")
@login_required
@admin_required
def pending():
    pending_entries = Leaderboard.query.filter_by(verified=False).all()
    return render_template("admin_pending.html", entries=pending_entries)

@admin.route("/verify/<int:entry_id>", methods=["POST"])
@login_required
@admin_required
def verify(entry_id):
    entry = Leaderboard.query.get_or_404(entry_id)
    entry.verified = True
    db.session.commit()
    flash("Entry verified", "success")
    return redirect(url_for("admin.pending"))

@admin.route("/reject/<int:entry_id>", methods=["POST"])
@login_required
@admin_required
def reject(entry_id):
    entry = Leaderboard.query.get_or_404(entry_id)
    try:
        if entry.screenshot_path and os.path.exists(entry.screenshot_path):
            os.remove(entry.screenshot_path) # make sure this deletes the ss file
    except Exception as e:
        print("Error deleting file:", e)
    db.session.delete(entry)
    db.session.commit()
    flash("Entry rejected and deleted", "invalid_time")
    return redirect(url_for("admin.pending"))
