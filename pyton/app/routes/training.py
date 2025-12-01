from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date, datetime
from app import db
from app.models.training import TrainingEntry, StepsEntry
from sqlalchemy import extract, func

training_bp = Blueprint("training", __name__, url_prefix="/training")


# ---------------------------------------
# HOME: Steps + Monats-Trainingsübersicht
# ---------------------------------------
@training_bp.route("/")
def training_home():
    today = date.today()

    # Steps – aktuelles Datum oder GET-Parameter
    date_str = request.args.get("day")
    if date_str:
        current_day = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        current_day = today

    steps_entry = StepsEntry.query.filter_by(date=current_day).first()
    all_steps = StepsEntry.query.order_by(StepsEntry.date.desc()).all()

    # Trainings – gruppiert nach Monat
    all_trainings = TrainingEntry.query.order_by(TrainingEntry.date.desc()).all()

    # Gruppieren nach year-month
    month_groups = {}
    for t in all_trainings:
        key = t.date.strftime("%Y-%m")
        if key not in month_groups:
            month_groups[key] = []
        month_groups[key].append(t)

    return render_template(
        "training/home.html",
        steps_entry=steps_entry,
        all_steps=all_steps,
        current_day=current_day,
        month_groups=month_groups,
    )


# ------------------------------
# Add / Update steps
# ------------------------------
@training_bp.route("/steps", methods=["POST"])
def save_steps():
    date_str = request.form.get("date")
    steps = int(request.form.get("steps"))

    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    entry = StepsEntry.query.filter_by(date=entry_date).first()
    if not entry:
        entry = StepsEntry(date=entry_date, steps=steps)
        db.session.add(entry)
    else:
        entry.steps = steps

    db.session.commit()

    return redirect(url_for("training.training_home", day=date_str))

@training_bp.route("/steps/delete/<int:sid>", methods=["POST"])
def delete_steps(sid):
    entry = StepsEntry.query.get_or_404(sid)
    entry_date = entry.date

    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for("training.training_home", day=entry_date))


# ------------------------------
# Add training
# ------------------------------
@training_bp.route("/add", methods=["POST"])
def add_training():
    date_str = request.form["date"]
    training_name = request.form["training_name"]
    distance = request.form["distance"]
    duration = request.form["duration"]
    notes = request.form["notes"]

    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    training = TrainingEntry(
        date=entry_date,
        training_name=training_name,
        distance=float(distance) if distance else None,
        duration=duration,
        notes=notes,
    )

    db.session.add(training)
    db.session.commit()

    return redirect(url_for("training.training_home", day=date_str))


# ------------------------------
# Edit training
# ------------------------------
@training_bp.route("/edit/<int:tid>")
def edit_training(tid):
    t = TrainingEntry.query.get_or_404(tid)
    return render_template("training/edit.html", t=t)


# ------------------------------
# Update training
# ------------------------------
@training_bp.route("/update/<int:tid>", methods=["POST"])
def update_training(tid):
    t = TrainingEntry.query.get_or_404(tid)

    t.training_name = request.form["training_name"]
    t.distance = float(request.form["distance"]) if request.form["distance"] else None
    t.duration = request.form["duration"]
    t.notes = request.form["notes"]

    db.session.commit()

    return redirect(url_for("training.training_home", day=t.date))


# ------------------------------
# Delete training
# ------------------------------
@training_bp.route("/delete/<int:tid>", methods=["POST"])
def delete_training(tid):
    t = TrainingEntry.query.get_or_404(tid)
    d = t.date

    db.session.delete(t)
    db.session.commit()

    return redirect(url_for("training.training_home", day=d))


# ------------------------------
# Chart data
# ------------------------------
@training_bp.route("/chart-data")
def training_chart_data():
    today = date.today()
    year_start = date(today.year, 1, 1)

    # Steps pro Tag
    steps = db.session.query(
        StepsEntry.date,
        StepsEntry.steps
    ).filter(StepsEntry.date >= year_start).all()

    # Trainings-Distanz pro Tag
    trainings = db.session.query(
        TrainingEntry.date,
        func.sum(TrainingEntry.distance)
    ).filter(TrainingEntry.date >= year_start).group_by(TrainingEntry.date).all()

    # Format für JS
    steps_data = [
        {"date": s.date.strftime("%Y-%m-%d"), "steps": s.steps}
        for s in steps
    ]

    training_data = [
        {"date": t[0].strftime("%Y-%m-%d"), "km": float(t[1] or 0)}
        for t in trainings
    ]

    return {
        "steps": steps_data,
        "training": training_data
    }
