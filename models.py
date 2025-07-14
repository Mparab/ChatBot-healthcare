from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    symptoms = db.Column(db.String(500), nullable=False)
    prediction = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref="history")