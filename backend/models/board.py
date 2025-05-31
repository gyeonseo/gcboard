from . import db
import datetime

class Board(db.Model):
    __tablename__ = 'boards'
    board_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    posts = db.relationship('Post', backref='board', lazy=True)
