#!/usr/bin/env python
__author__ = 'tomli'

import sys, os
import scrython
import requests
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

from app import app, db, socketio
from flask_script import Manager, prompt_bool
from app.models import Card, User, Rulings, Card_colour, Card_Subtypes

manager = Manager(app)

scryfall_String = 'https://api.scryfall.com/cards/search?q=set:grn%20order:color'

set_code = 'grn'

@manager.command
def initdb():
    # set up the db

    new_cards = scrython.cards.Search(q='set:{}'.format(set_code), order='color')
    all_cards = new_cards.data()
    if new_cards.has_more():
        next_set = requests.get(new_cards.next_page()).json()
        all_cards.extend(get_all_cards(next_set))

    db.create_all()
    #
    # add all cards
    for card in all_cards:
        # get all card attributes required
        print('Adding card: ' + card['name'] + card['collector_number'])
        # get the correct card image format
        if card['layout'] == 'normal' or 'split':
                image = card['image_uris']['normal'].split("?")[0]
        else:
            #transform cards
            if card['layout'] == 'transform':
                for face in card['card_faces']:
                    image = face['image_uris']['normal'].split("?")[0]

        #card price
        if "usd" in card:
            card_price = card["usd"]
        else:
            card_price = '0.0'

        #card rarity
        card_rarity = card['rarity']

        # potential card analysis here

        # add the card to the database
        db.session.add(Card(name=card['name'],
                            card_image=image,
                            card_price=card_price,
                            card_rarity=card_rarity))

        # card colour(s) to table
        if card['colors'] is not None:
            if len(card['colors']) == 0:
                # colourless
                #print('colourless')
                db.session.add(Card_colour(card_id=card['collector_number'],
                                       colour='colourless'))
            else:
                for colour in card['colors']:
                    #print(colour)
                    db.session.add(Card_colour(card_id=card['collector_number'],
                                       colour=colour))

        # card sub types -
        #check for sub types
        if '—' in card['type_line']:
            suptypes = card['type_line'].split('—')[1].split(' ')

            for sub in suptypes:
                # add to the db
                if sub is not '':
                    print(sub)
                    db.session.add(Card_Subtypes(card_id=card['collector_number'],
                                           subtype=sub.strip()))

        # add the card rulings
        # collector_number, card['collector_number']
        card_rulings = scrython.rulings.Code(code=set_code, collector_number=card['collector_number'])
        if card_rulings.data():
            for rule in card_rulings.data():
                if rule['source'] == 'wotc':
                    db.session.add(Rulings(card_id=card['collector_number'],
                                       ruling=rule['comment']))


    # add the wait card
    db.session.add(Card(name="Wait Card",
                            card_image='/static/img/a-pause-for-reflection.png',
                            card_price=None,
                            card_rarity=None))
    print('wait card added')
    db.session.commit()

    start = Card.query.filter_by(name="Wait Card").first()
    start.current_selected = True
    db.session.commit()

    #add the users
    db.session.add(User(username='tom'))
    db.session.add(User(username='bobtheadmin'))
    db.session.add(User(username='julie'))
    db.session.commit()

    print('Added Users')

    print('Initalised the DB')


def get_all_cards(all_card_data):
    card_data = all_card_data['data']
    #if has more
    if all_card_data['has_more']:
        #request new uri
        next_set = requests.get(all_card_data['next_page']).json()
        return card_data.extend(get_all_cards(next_set))
    else:
        return card_data

@manager.command
def dropdb():
    if prompt_bool("are you sure want to drop DB, and lose all data"):
        db.drop_all()
        print('Dropped the DB')

@manager.command
def runserver():

    #check csv
    if True is False:
        all_cards = Card.query.all()
        votes_pos = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]

        for card in all_cards:
            card.rating = random.choice(votes_pos)
            print (card.rating)
        db.session.commit()

    current = Card.query.filter_by(current_selected=True).first()
    current.current_selected = False
    wait_card_selected = Card.query.filter_by(name="Wait Card").first()
    wait_card_selected.current_selected = True
    db.session.commit()

    all_users = User.query.all()
    for user in all_users:
        user.voting = False
        user.logged_in = False
        print(user.username)
        print(user.logged_in)
    db.session.commit()

    socketio.run(app, host='192.168.0.2')

if __name__ == '__main__':
    manager.run()