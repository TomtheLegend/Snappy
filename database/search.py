
from sqlalchemy.orm import join
from .models import User, Card, CardColour, CardSubtypes, CardSupertypes
from ..app import db
# todo add desc limits to config file? so easier to update?


def top_10_cards_by_rating():
    sql_card_rating_str = 'SELECT name, rating, card_color, card_rarity, card_image FROM' \
                          ' Card ORDER BY rating DESC LIMIT 10'
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = [list(card_all) for card_all in card_ratings_db]

    return card_ratings


def top_10_cards_by_current_card_colour():
    sql_card_rating_str = 'SELECT name, rating, card_rarity, card_image FROM ' \
                          'Card where card_color = \'{}\' ' \
                          'ORDER BY rating DESC LIMIT 10'.format(current_card().card_color)
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = [list(card_all) for card_all in card_ratings_db]
    return card_ratings


def top_10_common_cards_by_current_card_colour():
    sql_card_common_rating_str = 'SELECT name, rating, card_color, card_image FROM' \
                                 ' Card where card_rarity = \'common\' ORDER BY' \
                                 ' rating DESC LIMIT 10'.format(current_card().card_color)
    card_common_ratings_db = db.session.execute(sql_card_common_rating_str).fetchall()
    card_ratings = [list(card_all) for card_all in card_common_ratings_db]
    return card_ratings


def current_card():
    # return the currently selected card
    return Card.query.filter_by(current_selected=True).first()

