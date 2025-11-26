from app import db
from datetime import date

class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    weight = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<WeightEntry {self.date} - {self.weight}>"
