__author__ = 'tomli'

from app import socketio
from flask_socketio import emit
from app.models import Card, User, Votes, Rulings, Card_colour
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


def get_current_votes_string(self):
    return "{} / {} votes ".format(self.get_current_vote_count(), self.get_current_voters())


def send_update_vote_bar(self, disable_all=None):
    votes = self.get_current_votes_string()
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

    # card info
    card_dict['info']['card price $'] = current_card.card_price

    # get colours
    card_colours = Card_colour.query.filter_by(card_id=current_card.id).all()
    for colour in card_colours:
        current_colour_count = Card_colour.query.filter_by(colour=str(colour.colour)).distinct()

        card_dict['info'][str(colour)] = 'all - 1/' + str(current_colour_count.count())

    return card_dict