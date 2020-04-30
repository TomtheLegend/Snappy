from .models import Card, CardColour, CardSubtypes, Rulings, Ratings
from ..app import db
from app.settings import config

# todo rename to keep standards, get_all, get etc


def get_top_cards_by_rating():
    sql_card_rating_str = 'SELECT name, rating, card_color, card_rarity, card_image FROM' \
                          ' Card ORDER BY rating DESC LIMIT  \'{}\''.format(config['LIMIT'])
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = [list(card_all) for card_all in card_ratings_db]
    return card_ratings


def get_top_cards_by_current_card_colour():
    sql_card_rating_str = 'SELECT name, rating, card_rarity, card_image FROM ' \
                          'Card where card_color = \'{}\' ' \
                          'ORDER BY rating DESC LIMIT ' \
                          '\'{}\''.format(current_card().card_color,
                                          config['LIMIT'])
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = [list(card_all) for card_all in card_ratings_db]
    return card_ratings


def get_top_common_cards_by_current_card_colour():
    sql_card_common_rating_str = 'SELECT name, rating, card_color, card_image FROM' \
                                 ' Card where card_rarity = \'common\' ORDER BY' \
                                 ' rating DESC LIMIT \'{}\'' \
                                 ''.format(current_card().card_color,
                                           config['LIMIT'])
    card_common_ratings_db = db.session.execute(sql_card_common_rating_str).fetchall()
    card_ratings = [list(card_all) for card_all in card_common_ratings_db]
    return card_ratings


def get_all_card_metrics_by_cmc(table, cmc):
    sql_average_cmc_string = 'SELECT card_colour, rarity, cmc, card_average, card_count FROM ' \
                               '{} WHERE cmc = \'{}\''.format(table, cmc)
    # print(sql_average_cmc_sting)
    card_averages_db = db.session.execute(sql_average_cmc_string).fetchall()

    card_ratings = [list(card_all) for card_all in card_averages_db]
    return card_ratings


def current_card():
    # return the currently selected card
    return Card.query.filter_by(current_selected=True).first()


def next_card():
    return Card.query.filter_by(rating=None).first()


def previous_card():
    next_id = current_card().id - 1
    if next_id > 0:
        sql_prev_card_str = 'SELECT id, name, rating, card_color, card_rarity  FROM' \
                            ' Card WHERE id = \'{}\''.format(next_id)
        return db.session.execute(sql_prev_card_str).first()
    else:
        return None


def get_card_by_name(card_name):
    return Card.query.filter_by(name=card_name).first()


def get_card_by_id(card_id):
    return Card.query.filter_by(id=card_id).first()


def get_all_distinct_by_cmc(table):
    sql_distinct_cmc_string = 'SELECT DISTINCT cmc FROM' \
                            ' {} '.format(table)
    card_cmcs_db = db.session.execute(sql_distinct_cmc_string).fetchall()
    card_ratings = [list(card_all) for card_all in card_cmcs_db]
    return card_ratings


def get_top_cards_by_colour(colour):
    sql_card_colour_str = 'SELECT name, rating, card_rarity, card_image FROM' \
                         ' Card where card_color = \'{}\' ' \
                          'ORDER BY rating DESC LIMIT \'{}\''.format(colour,
                                                                     config['LIMIT'])
    card_colour_db = db.session.execute(sql_card_colour_str).fetchall()
    card_colours = [list(card_all) for card_all in card_colour_db]
    return card_colours


def get_top_common_cards_by_colour(colour):
    sql_card_common_rating_str = 'SELECT name, rating, card_color, card_image FROM' \
                                 ' Card where card_rarity = \'common\' ORDER BY' \
                                 ' rating DESC LIMIT \'{}\''.format(colour,
                                                                    config['LIMIT'])
    card_common_ratings_db = db.session.execute(sql_card_common_rating_str).fetchall()
    card_common_ratings = [list(card_all) for card_all in card_common_ratings_db]
    return card_common_ratings


def get_current_card_rulings():
    card_rulings = Rulings.query.filter_by(card_id=current_card().id).all()
    rulings = [list(card_rule) for card_rule in card_rulings]
    return rulings


def get_card_rulings(card):
    card_rulings = Rulings.query.filter_by(card_id=card.id).all()
    rulings = [list(card_rule) for card_rule in card_rulings]
    return rulings


def get_current_card_colours():
    raw_colours = CardColour.query.filter_by(card_id=current_card().id).all()
    return [col.colour for col in raw_colours]


def get_cards_colour_count(colour):
    sql_colour_str = 'SELECT COUNT(card_id) FROM ' \
                     '( SELECT card_id, colour FROM CardColour GROUP BY card_id HAVING COUNT(card_id) = 1 )AS ONLY_ONCE' \
                     ' WHERE ONLY_ONCE.colour = \'{}\''.format(str(colour))
    solo_colour = db.session.execute(sql_colour_str).fetchall()
    return solo_colour[0][0]


def get_cards_colour_count_current_card_rarity(colour):
    sql_rariry_str = 'SELECT COUNT(card_id) FROM ' \
                     '( SELECT CardColour.card_id, CardColour.colour, Card.card_rarity FROM CardColour ' \
                     'INNER JOIN Card ON CardColour.card_id=Card.id GROUP ' \
                     'BY CardColour.card_id HAVING COUNT(CardColour.card_id) = 1 )AS ONLY_ONCE' \
                     ' WHERE ONLY_ONCE.colour = \'{}\' ' \
                     'AND ONLY_ONCE.card_rarity = \'{}\''.format(str(colour),
                                                                 current_card().card_rarity)
    solo_colour_rarity = db.session.execute(sql_rariry_str).fetchall()
    return solo_colour_rarity[0][0]


def get_current_card_suptypes():
    raw_subtypes = CardSubtypes.query.filter_by(card_id=current_card().id).all()
    return [sub.subtype for sub in raw_subtypes]


def get_card_subtype_count(subtype):
    sql_subtype_str = 'SELECT COUNT(card_id) FROM' \
                      ' CardSubtypes WHERE CardSubtypes.subtype = \'{}\''.format(str(subtype))
    solo_type = db.session.execute(sql_subtype_str).fetchall()
    return solo_type[0][0]


def get_current_card_ratings():
    return Ratings.query.filter_by(card_id=current_card().id).all()


def get_previous_card_all_user_ratings():
    prev = previous_card()
    if prev:
        all_ratings_sql = 'SELECT User.username, Ratings.vote_score FROM Ratings ' \
                          'INNER JOIN User ON User.id=Ratings.user_id' \
                          ' WHERE Ratings.card_id = \'{}\''.format(prev[0])
        prev_card_ratings_db = db.session.execute(all_ratings_sql).fetchall()
        card_ratings = [[card_all_prev[0], (card_all_prev[1] / 2)]
                        for card_all_prev in prev_card_ratings_db]
        return card_ratings
    else:
        return None


def get_distinct_supertypes():
    sql_average_supertype_sting = 'SELECT DISTINCT supertypes FROM' \
                                  ' Card_Supertypes_Metrics '
    card_supertypes_db = db.session.execute(sql_average_supertype_sting).fetchall()
    card_supertypes = [list(card_all) for card_all in card_supertypes_db]
    return card_supertypes


def get_supertypes_by_type(supertype):
    sql_average_cmc_sting = 'SELECT rarity, card_colour, card_count FROM ' \
                            'Card_Supertypes_Metrics WHERE supertypes = \'{}\''.format(supertype)
    # print(sql_average_cmc_sting)
    card_supertypes_db = db.session.execute(sql_average_cmc_sting).fetchall()
    card_supertypes = [list(card_all) for card_all in card_supertypes_db]
    return card_supertypes

