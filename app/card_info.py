__author__ = 'tomli'

from app import socketio
from flask_socketio import emit
from app.models import Card, User, Votes, Rulings, Card_colour, Card_Subtypes
from app import app, db


def get_current_voters():
    user_voters_count = 0
    current_users = User.query.filter_by(voting=True).all()
    for user in current_users:
        user_voters_count += 1
    return user_voters_count


def get_current_vote_count():
    current_card = Card.query.filter_by(current_selected=True).first()
    votes_list = Votes.query.filter_by(card_id=current_card.id).all()
    print(len(votes_list))
    return len(votes_list)


def get_current_votes_string():
    return "{} / {} votes ".format(get_current_vote_count(), get_current_voters())


def send_update_vote_bar( disable_all=None):
    votes = get_current_votes_string()
    emit('vote_bar_message', {'button_disabled': disable_all, 'current_votes': votes, 'last_vote': ''},  namespace='/', broadcast=True)


def get_card_info():
    # returns a dict of data
    #dict is split into sections to copy the page, each section is added seperately
    card_dict = {'card_image': '', 'rulings': [], 'info': {}}
    current_card = Card.query.filter_by(current_selected=True).first()

    #card_image
    card_dict['card_image'] = current_card.card_image

    # rulings
    card_rulings = Rulings.query.filter_by(card_id=current_card.id).all()
    for rule in card_rulings:
        card_dict['rulings'].append(rule.ruling)

    ### card info ###
    # card price
    card_dict['info']['card price $'] = current_card.card_price

    # card colour breakdown
    card_colours = Card_colour.query.filter_by(card_id=current_card.id).all()
    for colour in card_colours:
        #cards in the colour
        sql_colour_str = 'SELECT COUNT(card_id) FROM ' \
                  '( SELECT card_id, colour FROM Card_colour GROUP BY card_id HAVING COUNT(card_id) = 1 )AS ONLY_ONCE' \
                  ' WHERE ONLY_ONCE.colour = \'{}\''.format(str(colour.colour))
        solo_colour = db.session.execute(sql_colour_str).fetchall()
        card_dict['info'][str(colour.colour)] = ':all - 1/' + str(solo_colour[0][0])
        # rarity in the colour
        sql_rariry_str = 'SELECT COUNT(card_id) FROM ' \
                  '( SELECT Card_colour.card_id, Card_colour.colour, Card.card_rarity FROM Card_colour ' \
                  'INNER JOIN Card ON Card_colour.card_id=Card.id GROUP BY Card_colour.card_id HAVING COUNT(Card_colour.card_id) = 1 )AS ONLY_ONCE' \
                  ' WHERE ONLY_ONCE.colour = \'{}\' AND ONLY_ONCE.card_rarity = \'{}\''.format(str(colour.colour), current_card.card_rarity)
        solo_colour_rarity = db.session.execute(sql_rariry_str).fetchall()
        card_dict['info'][str(colour.colour)+':'+str(current_card.card_rarity)] = '- 1/' + str(solo_colour_rarity[0][0])


    #card sup types total
    card_subtypes = Card_Subtypes.query.filter_by(card_id=current_card.id).all()
    for subtype in card_subtypes:
        sql_subtype_str = 'SELECT COUNT(card_id) FROM' \
                          ' Card_Subtypes WHERE Card_Subtypes.subtype = \'{}\''.format(str(subtype.subtype))
        solo_type = db.session.execute(sql_subtype_str).fetchall()
        print (solo_type)
        card_dict['info'][str(subtype.subtype)] = ': 1/' + str(solo_type[0][0])



    return card_dict