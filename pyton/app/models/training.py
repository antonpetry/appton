from app import db
from datetime import date, timedelta

class StepsEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today, unique=True, nullable=False)
    steps = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Steps {self.steps} on {self.date}>"

class TrainingEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, default=date.today, nullable=False)
    training_name = db.Column(db.String(120), nullable=False)

    distance = db.Column(db.Float, nullable=True)  # Einheit abhängig vom Sport
    duration = db.Column(db.String(20), nullable=True)  # "hh:mm:ss"
    notes = db.Column(db.String(255), nullable=True)

    # Einheit wird abgeleitet, nicht gespeichert
    def detect_unit(self):
        name = self.training_name.lower()

        if "lauf" in name or "jog" in name or "run" in name:
            return "km"
        if "rad" in name or "bike" in name:
            return "km"
        if "schwimm" in name or "swim" in name:
            return "Bahnen (25m)"

        return "m"  # Default

    def __repr__(self):
        return f"<Training {self.training_name} on {self.date}>"
