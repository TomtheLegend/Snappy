__author__ = 'tomli'

from app import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class Card(db.Model):
    """
    Used to hold the card data and its average rating once determined.
    """
    __tablename__ = 'Card'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    rating = db.Column(db.Float, default=None)
    current_selected = db.Column(db.Boolean, default=False)
    card_image = db.Column(db.String(300))
    card_price = db.Column(db.String(50))
    card_rarity = db.Column(db.String(50))
    card_color = db.Column(db.String(50), default="")
    card_cmc = db.Column(db.String(50))
    time_taken = db.Column(db.String(50))

    # relationships
    trackers = relationship("Votes")
    rulings = relationship("Rulings")
    Card_colour = relationship("Card_colour")
    Card_Subtypes = relationship("Card_Subtypes")


class User(db.Model, UserMixin):
    """
    Used to hold the user information and see who is voting
    """
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True)
    voting = db.Column(db.Boolean, default=False)
    logged_in = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    tracker = relationship("Ratings")


class Ratings(db.Model):
    """
    Table to store each users rating
    """
    __tablename__ = 'Ratings'
    id = db.Column(db.Integer, primary_key=True)
    rating_score = db.Column(db.Integer, default=0)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))


class Rulings(db.Model):
    """
    Hold the rulings for each card if required
    """
    __tablename__ = 'Rulings'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    ruling = db.Column(db.String(1000))


class CardColour(db.Model):
    """
    Store all the colours associated with each card
    """
    __tablename__ = 'Card_colour'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    colour = db.Column(db.String(50))


class CardSubtypes(db.Model):
    __tablename__ = 'Card_Subtypes'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    subtype = db.Column(db.String(50))


class CardSupertypes(db.Model):
    __tablename__ = 'Card_Supertypes'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('Card.id'))
    supertype = db.Column(db.String(50))


class CardSupertypesMetrics(db.Model):
    """
    Used to easily assemble supertype metrics in a table.
    """
    __tablename__ = 'Card_Supertypes_Metrics'
    id = db.Column(db.Integer, primary_key=True)
    supertypes = db.Column(db.String(100))
    card_colour = db.Column(db.String(10))
    rarity = db.Column(db.String(50))
    card_count = db.Column(db.Integer)


class PowerAverages(db.Model):
    __tablename__ = 'Power_Averages'
    id = db.Column(db.Integer, primary_key=True)
    card_colour = db.Column(db.String(10))
    rarity = db.Column(db.String(50))
    cmc = db.Column(db.String(50))
    card_average = db.Column(db.Float)
    card_count = db.Column(db.Integer)


class ToughnessAverages(db.Model):
    __tablename__ = 'Toughness_Averages'
    id = db.Column(db.Integer, primary_key=True)
    card_colour = db.Column(db.String(10))
    rarity = db.Column(db.String(50))
    cmc = db.Column(db.String(50))
    card_average = db.Column(db.Float)
    card_count = db.Column(db.Integer)



