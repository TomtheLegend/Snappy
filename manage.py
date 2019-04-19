#!/usr/bin/env python
__author__ = 'tomli'

import eventlet
eventlet.monkey_patch()

import sys, os
import scrython
import requests
import random
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

from app import app, db, socketio
from flask_script import Manager, prompt_bool
from app.models import Card, User, Rulings, Card_colour, Card_Subtypes, Votes

from urllib import request

manager = Manager(app)

scryfall_String = 'https://api.scryfall.com/cards/search?q=set:grn%20order:color'

set_code = 'war'

@manager.command
def initdb():
    ''' set up the db, add cards, wait cards, users.
    # get the types and colour associations.
    # work out relevent metrics
    '''

    #set up variables for averages
    average_power = {}
    average_power_count = {}
    average_toughness = {}
    average_toughness_count = {}
    for i in range(0, 15, 1):
        average_power[str(i)] = {'all': 0, 'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}
        average_power_count[str(i)] = {'all': 0, 'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}

        average_toughness[str(i)] = {'all': 0, 'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}
        average_toughness_count[str(i)] = {'all': 0, 'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}


    new_cards = scrython.cards.Search(q='set:{} is:booster'.format(set_code), order='color')
    all_cards = new_cards.data()
    #print(new_cards.next_page())
    if new_cards.has_more():
        next_set = requests.get(new_cards.next_page()).json()
        all_cards.extend(get_all_cards(next_set))

    db.create_all()
    # add all cards
    for card in all_cards:
        # get all card attributes required
        image_url = ''
        print('Adding card: ' + card['name'] + ' - ' + card['collector_number'])
        # get the correct card image format
        if card['layout'] == 'normal' or 'split':
                image_url = card['image_uris']['normal'].split("?")[0]
        else:
            #transform cards
            if card['layout'] == 'transform':
                for face in card['card_faces']:
                    image_url = face['image_uris']['normal'].split("?")[0]

        card_location_name = card['name']
        if '/' in card_location_name:
            card_location_name = card_location_name.replace("/", "")
        if '%' in card_location_name:
            card_location_name = card_location_name.replace("%", "")
        if '&' in card_location_name:
            card_location_name = card_location_name.replace("&", "")
        if '\"' in card_location_name:
            card_location_name = card_location_name.replace("\"", "")

        image_loc = '/static/img/cards/' + card_location_name + '.jpg'
        f = open('D:/Programming/Snappy/app/static/img/cards/' + card_location_name + '.jpg', 'wb+')
        f.write(request.urlopen(str(image_url)).read())
        f.close()

        #card price
        if "usd" in card:
            card_price = card["usd"]
        else:
            card_price = '0.0'

        #card rarity
        card_rarity = card['rarity']

        #### card analysis ###

        # check if has power
        if "power" in card:
            # update relevant average power stats

            if representsint(card['power']):
                #print('power : ' +card['power'])
                power_int = int(card['power'])
                average_power[str(int(card['cmc']))]['all'] += power_int
                average_power_count[str(int(card['cmc']))]['all'] += 1

                average_power[str(int(card['cmc']))][card['rarity']] += power_int
                average_power_count[str(int(card['cmc']))][card['rarity']] += 1

        # check for toughness
        if "toughness" in card:
            # update relevant average power stats

            if representsint(card['toughness']):
                #print('toughness : ' +card['toughness'])
                toughness_int = int(card['toughness'])
                average_toughness[str(int(card['cmc']))]['all'] += toughness_int
                average_toughness_count[str(int(card['cmc']))]['all'] += 1

                average_toughness[str(int(card['cmc']))][card['rarity']] += toughness_int
                average_toughness_count[str(int(card['cmc']))][card['rarity']] += 1

        # card colour
        card_color = ''
        if card['colors'] is not None:

            if len(card['colors']) == 0:
                card_color = 'colourless'
            elif len(card['colors']) > 1:
                card_color = 'multi-colour'
            else:
                card_color = card['colors'][0]
        # add the card to the database
        db.session.add(Card(id=card['collector_number'],
                            name=card['name'],
                            card_image=image_loc,
                            card_price=card_price,
                            card_rarity=card_rarity,
                            card_color=card_color,
                            card_cmc=str(int(card['cmc']))))

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
                    #print(sub)
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



    print('all Cards added')

    ### calculate metrics ###
    #power
    for key_cmc, value_cmc in average_power.items():
        for key_rarity, value_rarity in value_cmc.items():
            #print ('{}, {}:{}'.format(value_cmc[key_rarity], value_rarity, average_power_count[key_cmc][key_rarity]))
            if average_power_count[key_cmc][key_rarity] > 0:
                value_cmc[key_rarity] = round(float(value_rarity / average_power_count[key_cmc][key_rarity]), 3)

    #toughness
    for key_cmc, value_cmc in average_toughness.items():
        for key_rarity, value_rarity in value_cmc.items():
            #print ('{}, {}:{}'.format(value_cmc[key_rarity], value_rarity, average_power_count[key_cmc][key_rarity]))
            if average_toughness_count[key_cmc][key_rarity] > 0:
                value_cmc[key_rarity] = round(float(value_rarity / average_toughness_count[key_cmc][key_rarity]), 3)

    save_dict = {'average_power': average_power, 'average_toughness': average_toughness}
    save_json(save_dict)

    print('Average power & toughness calculated')

    #### add the wait cards ####
    db.session.add(Card(name="Wait Card colourless",
                        card_image='/static/img/colourless break.png',
                        card_price=None,
                        card_rarity=None))
    db.session.add(Card(name="Wait Card W",
                        card_image='/static/img/plains break.png',
                        card_price=None,
                        card_rarity=None))
    db.session.add(Card(name="Wait Card U",
                        card_image='/static/img/island break.png',
                        card_price=None,
                        card_rarity=None))
    db.session.add(Card(name="Wait Card B",
                        card_image='/static/img/swamp break.png',
                        card_price=None,
                        card_rarity=None))
    db.session.add(Card(name="Wait Card R",
                        card_image='/static/img/mountain break.png',
                        card_price=None,
                        card_rarity=None))
    db.session.add(Card(name="Wait Card G",
                        card_image='/static/img/forest break.png',
                        card_price=None,
                        card_rarity=None))
    db.session.add(Card(name="Wait Card multi-colour",
                        card_image='/static/img/multi colour break.png',
                        card_price=None,
                        card_rarity=None))

    #add, multi, artifact.

    # add the control wait card for player use.
    db.session.add(Card(name="Wait Card",
                        card_image='/static/img/a-pause-for-reflection.png',
                        card_price=None,
                        card_rarity=None,
                        card_color=None))


    print('wait cards added')
    db.session.commit()

    start = Card.query.filter_by(name="Wait Card").first()
    start.current_selected = True
    db.session.commit()

    #add the users
    db.session.add(User(username='tom'))
    db.session.add(User(username='bobtheadmin', admin=True))
    db.session.add(User(username='julie'))
    db.session.commit()

    print('Added Users')

    print('Initialised the DB')


def get_all_cards(all_card_data):
    card_data = all_card_data['data']
    #if has more
    if all_card_data['has_more']:
        #print(all_card_data['next_page'])
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
    # check csv
    if True is False:
        all_cards = Card.query.all()
        votes_pos = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        #votes_pos = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, None]

        for card in all_cards:
            if card.id in range(1, 40):
                card.rating = random.choice(votes_pos)
            else:
            #card.rating = random.choice(votes_pos)
                card.rating = None
                card_votes = Votes.query.filter_by(card_id=card.id).delete()
            # print (card.rating)

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

    socketio.run(app, host='192.168.0.187', port='5000')
    #192.168.1.117
    #192.168.0.14

def representsint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def save_json(data):
    with open('app/static/additional_info.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == '__main__':
    manager.run()