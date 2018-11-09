#!/usr/bin/env python
__author__ = 'tomli'

import sys, os
import scrython
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

from app import app, db, socketio
from flask_script import Manager, prompt_bool
from app.models import Card, User, Rulings

manager = Manager(app)

scryfall_String = 'https://api.scryfall.com/cards/search?q=set:grn%20order:color'

set_code = 'grn'

@manager.command
def initdb():
    # set up the db
    db.create_all()
    new_cards = scrython.cards.Search(q='set:{}'.format(set_code), order='color')
    # add all cards
    for card in new_cards.data():
        print('Adding card: ' + card['name'])
        # get the correct card image format
        if card['layout'] == 'normal' or 'split':
                image = card['image_uris']['normal'].split("?")[0]
        else:
            #transform cards
            if card['layout'] == 'transform':
                for face in card['card_faces']:
                    image = face['image_uris']['normal'].split("?")[0]
        db.session.add(Card(name=card['name'],
                            card_image=image))

        # add the card rulings
        # collector_number, card['collector_number']
        card_rulings = scrython.rulings.Code(code=set_code, collector_number=card['collector_number'])
        if card_rulings.data():
            for rule in card_rulings.data():
                if rule['source'] == 'wotc':
                    print (rule['comment'])
                    db.session.add(Rulings(card_id=card['collector_number'],
                                       ruling=rule['comment']))

    db.session.commit()
    start = Card.query.get(1)
    start.current_selected = True
    db.session.commit()

    #add the users
    db.session.add(User(username='tom'))
    db.session.add(User(username='bobtheadmin'))
    db.session.add(User(username='julie'))
    db.session.commit()
    print('Added Users')

    print('Initalised the DB')


@manager.command
def dropdb():
    if prompt_bool("are you sure want to drop DB, and lose all data"):
        db.drop_all()
        print('Dropped the DB')

@manager.command
def runserver():
    all_users = User.query.filter_by(voting=True).all()
    for user in all_users:
        user.voting = False
    db.session.commit()
    socketio.run(app, host='192.168.0.2')

if __name__ == '__main__':
    manager.run()