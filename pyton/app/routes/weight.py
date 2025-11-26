from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, date
from app import db
from app.models.weight import WeightEntry

# Blueprint mit URL-Präfix
weight_bp = Blueprint("weight", __name__, url_prefix="/weight")


# ------------------------------
# Show all weight entries
# ------------------------------
@weight_bp.route("/")
def weight_page():
    entries = WeightEntry.query.order_by(WeightEntry.date.desc()).all()
    chart_entries = WeightEntry.query.order_by(WeightEntry.date.asc()).all()

    dates = [e.date.isoformat() for e in chart_entries]
    weights = [e.weight for e in chart_entries]

    return render_template(
        "weight/home.html",
        entries=entries,
        default_date=date.today().isoformat(),
        dates=dates,
        weights=weights
    )


# ------------------------------
# Add new entry
# ------------------------------
@weight_bp.route("/add", methods=["POST"])
def add_weight():
    date_str = request.form.get("date")
    weight_value = request.form.get("weight")

    if date_str:
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        entry_date = date.today()

    entry = WeightEntry(date=entry_date, weight=float(weight_value))
    db.session.add(entry)
    db.session.commit()

    return redirect(url_for("weight.weight_page"))


# ------------------------------
# Edit entry form (GET)
# ------------------------------
@weight_bp.route("/edit/<int:entry_id>")
def edit_weight(entry_id):
    entry = WeightEntry.query.get_or_404(entry_id)
    return render_template("weight/edit.html", entry=entry)


# ------------------------------
# Save edited entry (POST)
# ------------------------------
@weight_bp.route("/update/<int:entry_id>", methods=["POST"])
def update_weight(entry_id):
    entry = WeightEntry.query.get_or_404(entry_id)

    date_str = request.form.get("date")
    weight_value = request.form.get("weight")

    entry.date = datetime.strptime(date_str, "%Y-%m-%d").date()
    entry.weight = float(weight_value)

    db.session.commit()

    return redirect(url_for("weight.weight_page"))


# ------------------------------
# Delete entry
# ------------------------------
@weight_bp.route("/delete/<int:entry_id>", methods=["POST"])
def delete_weight(entry_id):
    entry = WeightEntry.query.get_or_404(entry_id)

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for("weight.weight_page"))
