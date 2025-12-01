from flask import Blueprint, render_template, request, redirect, url_for
from datetime import date, datetime
from app import db
from app.models.nutrition import NutritionEntry
from sqlalchemy import func

nutrition_bp = Blueprint("nutrition", __name__, url_prefix="/nutrition")


# ------------------------------
# Overview (graph + today)
# ------------------------------
@nutrition_bp.route("/")
def nutrition_home():
    today = date.today()

    # Aktuelles Datum aus Query
    date_str = request.args.get("day")
    if date_str:
        current_day = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        current_day = today

    # Tagesdaten (Detailtabelle)
    meals = NutritionEntry.query.filter_by(date=current_day).all()

    # -----------------------------------------------------------
    # Wöchentliche Durchschnittswerte seit Jahresbeginn
    # -----------------------------------------------------------
    year_start = date(today.year, 1, 1)

    weekly_stats = (
        db.session.query(
            func.strftime("%W", NutritionEntry.date).label("week"),
            func.avg(NutritionEntry.calories),
        )
        .filter(NutritionEntry.date >= year_start)
        .group_by("week")
        .all()
    )

    weeks = [int(w[0]) for w in weekly_stats]
    avg_cals = [int(w[1]) for w in weekly_stats]

    # -----------------------------------------------------------
    # Tägliche Gesamtkalorien (für Tagesbalken-Diagramm)
    # -----------------------------------------------------------
    daily_stats = (
        db.session.query(
            NutritionEntry.date,
            func.sum(NutritionEntry.calories)
        )
        .group_by(NutritionEntry.date)
        .order_by(NutritionEntry.date)
        .all()
    )

    daily_labels = [str(d[0]) for d in daily_stats]   # "YYYY-MM-DD"
    daily_values = [int(d[1]) for d in daily_stats]

    return render_template(
        "nutrition/home.html",
        meals=meals,
        current_day=current_day,

        # Für Wochen-Diagramm
        weeks=weeks,
        avg_cals=avg_cals,

        # Für Tages-Diagramm
        daily_labels=daily_labels,
        daily_values=daily_values,
    )


# ------------------------------
# Add meal
# ------------------------------
@nutrition_bp.route("/add", methods=["POST"])
def add_meal():
    date_str = request.form.get("date")
    meal_name = request.form.get("meal_name")
    calories = request.form.get("calories")
    carbs = request.form.get("carbs")
    protein = request.form.get("protein")
    fat = request.form.get("fat")

    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    entry = NutritionEntry(
        date=entry_date,
        meal_name=meal_name,
        calories=int(calories),
        carbs=float(carbs),
        protein=float(protein),
        fat=float(fat),
    )

    db.session.add(entry)
    db.session.commit()

    return redirect(url_for("nutrition.nutrition_home", day=date_str))


# ------------------------------
# Edit meal form (GET)
# ------------------------------
@nutrition_bp.route("/edit/<int:meal_id>")
def edit_meal(meal_id):
    meal = NutritionEntry.query.get_or_404(meal_id)
    return render_template("nutrition/edit.html", meal=meal)


# ------------------------------
# Update meal (POST)
# ------------------------------
@nutrition_bp.route("/update/<int:meal_id>", methods=["POST"])
def update_meal(meal_id):
    meal = NutritionEntry.query.get_or_404(meal_id)

    meal.meal_name = request.form["meal_name"]
    meal.calories = float(request.form["calories"])
    meal.carbs = float(request.form["carbs"])
    meal.protein = float(request.form["protein"])
    meal.fat = float(request.form["fat"])

    db.session.commit()

    return redirect(url_for("nutrition.nutrition_home", day=meal.date))


# ------------------------------
# Delete meal
# ------------------------------
@nutrition_bp.route("/delete/<int:meal_id>", methods=["POST"])
def delete_meal(meal_id):
    meal = NutritionEntry.query.get_or_404(meal_id)
    day = meal.date

    db.session.delete(meal)
    db.session.commit()

    return redirect(url_for("nutrition.nutrition_home", day=day))
