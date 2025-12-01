from app import db
from datetime import date

class NutritionEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, default=date.today, nullable=False)
    meal_name = db.Column(db.String(120), nullable=False)

    calories = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Meal {self.meal_name} on {self.date}>"
