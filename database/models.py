__author__ = 'tomli'

from app import main_app
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class Card(main_app.db.Model):
    """
    Used to hold the card data and its average rating once determined.
    """
    __tablename__ = 'Card'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    name = main_app.db.Column(main_app.db.String(200))
    rating = main_app.db.Column(main_app.db.Float, default=None)
    current_selected = main_app.db.Column(main_app.db.Boolean, default=False)
    card_image = main_app.db.Column(main_app.db.String(300))
    card_price = main_app.db.Column(main_app.db.String(50))
    card_rarity = main_app.db.Column(main_app.db.String(50))
    card_color = main_app.db.Column(main_app.db.String(50), default="")
    card_cmc = main_app.db.Column(main_app.db.String(50))
    time_taken = main_app.db.Column(main_app.db.String(50))

    # relationships
    trackers = relationship("Ratings")
    rulings = relationship("Rulings")
    Card_colour = relationship("CardColour")
    Card_Subtypes = relationship("CardSubtypes")


class User(main_app.db.Model, UserMixin):
    """
    Used to hold the user information and see who is voting
    """
    __tablename__ = 'User'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    username = main_app.db.Column(main_app.db.String(200), unique=True)
    voting = main_app.db.Column(main_app.db.Boolean, default=False)
    logged_in = main_app.db.Column(main_app.db.Boolean, default=False)
    admin = main_app.db.Column(main_app.db.Boolean, default=False)
    tracker = relationship("Ratings")


class Ratings(main_app.db.Model):
    """
    Table to store each users rating
    """
    __tablename__ = 'Ratings'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    rating_score = main_app.db.Column(main_app.db.Integer, default=0)
    card_id = main_app.db.Column(main_app.db.Integer, main_app.db.ForeignKey('Card.id'))
    user_id = main_app.db.Column(main_app.db.Integer, main_app.db.ForeignKey('User.id'))


class Rulings(main_app.db.Model):
    """
    Hold the rulings for each card if required
    """
    __tablename__ = 'Rulings'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    card_id = main_app.db.Column(main_app.db.Integer, main_app.db.ForeignKey('Card.id'))
    ruling = main_app.db.Column(main_app.db.String(1000))


class CardColour(main_app.db.Model):
    """
    Store all the colours associated with each card
    """
    __tablename__ = 'Cardcolour'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    card_id = main_app.db.Column(main_app.db.Integer, main_app.db.ForeignKey('Card.id'))
    colour = main_app.db.Column(main_app.db.String(50))


class CardSubtypes(main_app.db.Model):
    __tablename__ = 'CardSubtypes'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    card_id = main_app.db.Column(main_app.db.Integer, main_app.db.ForeignKey('Card.id'))
    subtype = main_app.db.Column(main_app.db.String(50))


class CardSupertypes(main_app.db.Model):
    __tablename__ = 'CardSupertypes'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    card_id = main_app.db.Column(main_app.db.Integer, main_app.db.ForeignKey('Card.id'))
    supertype = main_app.db.Column(main_app.db.String(50))


class CardSupertypesMetrics(main_app.db.Model):
    """
    Used to easily assemble supertype metrics in a table.
    """
    __tablename__ = 'CardSupertypesMetrics'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    supertypes = main_app.db.Column(main_app.db.String(100))
    card_colour = main_app.db.Column(main_app.db.String(10))
    rarity = main_app.db.Column(main_app.db.String(50))
    card_count = main_app.db.Column(main_app.db.Integer)


class PowerAverages(main_app.db.Model):
    __tablename__ = 'PowerAverages'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    card_colour = main_app.db.Column(main_app.db.String(10))
    rarity = main_app.db.Column(main_app.db.String(50))
    cmc = main_app.db.Column(main_app.db.String(50))
    card_average = main_app.db.Column(main_app.db.Float)
    card_count = main_app.db.Column(main_app.db.Integer)


class ToughnessAverages(main_app.db.Model):
    __tablename__ = 'ToughnessAverages'
    id = main_app.db.Column(main_app.db.Integer, primary_key=True)
    card_colour = main_app.db.Column(main_app.db.String(10))
    rarity = main_app.db.Column(main_app.db.String(50))
    cmc = main_app.db.Column(main_app.db.String(50))
    card_average = main_app.db.Column(main_app.db.Float)
    card_count = main_app.db.Column(main_app.db.Integer)



