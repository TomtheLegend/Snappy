__author__ = 'tomli'

from app import db
from flask_login import UserMixin

from sqlalchemy.orm import relationship



class Card(db.Model):
    __tablename__ = 'Card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    rating = db.Column(db.Float, default=None)
    current_selected = db.Column(db.Boolean, default=False)
    card_image = db.Column(db.String(300))
    card_price = db.Column(db.String(50))
    card_rarity = db.Column(db.String(50))
    # relationships
    trackers = relationship("Votes")
    rulings = relationship("Rulings")
    Card_colour = relationship("Card_colour")
    Card_Subtypes = relationship("Card_Subtypes")

    @staticmethod
    def next_card():
        current = Card.query.filter_by(current_selected=True).first()
        current.current_selected = False
        next_id = current.id + 1
        next = Card.query.filter_by(id=next_id).first()
        next.current_selected = True
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    voting = db.Column(db.Boolean, default=False)
    logged_in = db.Column(db.Boolean, default=False)
    tracker = relationship("Votes")

class Votes(db.Model):
    __tablename__ = 'Votes'
    id = db.Column(db.Integer, primary_key=True)
    vote_score = db.Column(db.Integer, default=0)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

class Rulings(db.Model):
    __tablename__ = 'Rulings'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    ruling = db.Column(db.String(1000))

class Card_colour(db.Model):
    __tablename__ = 'Card_colour'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    colour = db.Column(db.String(50))

class Card_Subtypes(db.Model):
    __tablename__ = 'Card_Subtypes'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    subtype = db.Column(db.String(50))

