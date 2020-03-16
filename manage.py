#!/usr/bin/env python
__author__ = 'tomli'

# todo clean up manage, get everything in its own file and contained.
import eventlet
eventlet.monkey_patch()

import sys, os
import scrython
import requests
import card_data
import itertools

import random
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

from app import app, db, socketio
from flask_script import Manager, prompt_bool
from database.models import Card, User, Rulings, CardColour,\
    CardSubtypes, Votes, CardSupertypes, ToughnessAverages, PowerAverages,\
    CardSupertypesMetrics
from urllib import request

manager = Manager(app)

set_code = 'thb'

@manager.command
def initdb():
    '''
    set up the db, add cards, wait cards, users.
    # get the types and colour associations.
    # work out relevent metrics
    '''
    # set up variables for averages
    average_power = {}
    average_power_count = {}
    average_toughness = {}
    average_toughness_count = {}
    # setup lists of dics for averages for all values of power and toughness.
    # power for cmc for rarity and colour
    all_rarities = ['all', 'common', 'uncommon', 'rare', 'mythic']
    all_colours = ['all', 'W', 'U', 'B', 'R', 'G', 'colourless', 'multi-colour']

    for i in range(0, 15, 1):
        average_power[str(i)] = {}
        average_power_count[str(i)] = {}
        average_toughness[str(i)] = {}
        average_toughness_count[str(i)] = {}
        for colour in all_colours:
            average_power[str(i)][colour] = {}
            average_power_count[str(i)][colour] = {}
            average_toughness[str(i)][colour] = {}
            average_toughness_count[str(i)][colour] = {}
            for rarity in all_rarities:
                # assign power nested dicts
                average_power[str(i)][colour][rarity] = 0
                average_power_count[str(i)][colour][rarity] = 0
                # average_power_count[str(i)] = {'all': {}, 'common': 0, 'uncommon': 0, 'rare': 0, 'mythic': 0}
                #
                average_toughness[str(i)][colour][rarity] = 0
                average_toughness_count[str(i)][colour][rarity] = 0

    #set up vars for supertypes
    possible_supertypes = []
    all_cards = card_data.get_all_cards()

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
            # transform cards
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

        cwd = os.getcwd()
        image_loc = '/static/img/cards/' + card_location_name + '.jpg'
        with open(cwd + '/app/static/img/cards/' + card_location_name + '.jpg', 'wb+') as f:
            f.write(request.urlopen(str(image_url)).read())

        #card price
        if "usd" in card:
            card_price = card["usd"]
        else:
            card_price = '0.0'

        #card rarity
        card_rarity = card['rarity']

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
                # print('colourless')
                db.session.add(CardColour(card_id=card['collector_number'],
                                       colour='colourless'))
            else:
                for colour in card['colors']:
                    # print(colour)
                    db.session.add(CardColour(card_id=card['collector_number'],
                                       colour=colour))

        #### card analysis ###

        # check if has power
        if "power" in card:
            # update relevant average power stats

            if representsint(card['power']):
                # print('power : ' +card['power'])
                power_int = int(card['power'])
                card_cmc = str(int(card['cmc']))
                # cmc , color, rarities
                # add to all
                average_power[card_cmc]['all']['all'] += power_int
                average_power_count[card_cmc]['all']['all'] += 1

                # add to all rarity
                average_power[card_cmc]['all'][card_rarity] += power_int
                average_power_count[card_cmc]['all'][card_rarity] += 1

                # add to all colour
                average_power[card_cmc][card_color]['all'] += power_int
                average_power_count[card_cmc][card_color]['all'] += 1

                # add to color rarity
                average_power[card_cmc][card_color][card_rarity] += power_int
                average_power_count[card_cmc][card_color][card_rarity] += 1

        # check for toughness

        if "toughness" in card:
            # update relevant average power stats

            if representsint(card['toughness']):
                # print('power : ' +card['power'])
                toughness_int = int(card['toughness'])
                card_cmc = str(int(card['cmc']))
                # cmc , color, rarities
                # add to all
                average_toughness[card_cmc]['all']['all'] += toughness_int
                average_toughness_count[card_cmc]['all']['all'] += 1

                # add to all rarity
                average_toughness[card_cmc]['all'][card_rarity] += toughness_int
                average_toughness_count[card_cmc]['all'][card_rarity] += 1

                # add to all colour
                average_toughness[card_cmc][card_color]['all'] += toughness_int
                average_toughness_count[card_cmc][card_color]['all'] += 1

                # add to color rarity
                average_toughness[card_cmc][card_color][card_rarity] += toughness_int
                average_toughness_count[card_cmc][card_color][card_rarity] += 1

        # card super and sub types #
        # super types - sub types
        if '—' in card['type_line']:
            card_types = card['type_line'].split('—')
            subtypes = card_types[1].split(' ')
            supertypes = card_types[0].split(' ')
            possible_supertypes.append(list(filter(None, supertypes)))
            for sub in subtypes:
                if sub != '':
                    # print(sub)
                    db.session.add(CardSubtypes(card_id=card['collector_number'],
                                           subtype=sub.strip()))

            for sup in supertypes:
                if sup != '':
                    db.session.add(CardSupertypes(card_id=card['collector_number'],
                                                 supertype=sup.strip()))
        else:
            supertypes = card['type_line'].split(' ')
            possible_supertypes.append(supertypes)
            for sup in supertypes:
                if sup != '':
                    db.session.add(CardSupertypes(card_id=card['collector_number'],
                                                 supertype=sup.strip()))


        # add the card rulings
        # collector_number, card['collector_number']
        card_rulings = scrython.rulings.Code(code=set_code, collector_number=card['collector_number'])
        if card_rulings.data():
            for rule in card_rulings.data():
                if rule['source'] == 'wotc':
                    db.session.add(Rulings(card_id=card['collector_number'],
                                       ruling=rule['comment']))

    db.session.commit()
    print('all Cards added')

    # for each distinct supertype combination find all cards relating to it.
    possible_supertypes.sort()
    possible_supertypes_distinct = list(possible_supertypes for possible_supertypes, _ in itertools.groupby(possible_supertypes))
    supertype_calculation(possible_supertypes_distinct)
    print('SuperTypes Assesed')
    ### calculate metrics ###
    # power
    for key_cmc, value_cmc in average_power.items():
        for key_colour, value_colour in value_cmc.items():
            for key_rarity, value_rarity in value_colour.items():
                # print ('{}, {}:{}'.format(value_cmc[key_rarity], value_rarity, average_power_count[key_cmc][key_rarity]))
                if average_power_count[key_cmc][key_colour][key_rarity] > 0:
                    average_power[key_cmc][key_colour][key_rarity] = round(float(value_rarity / average_power_count[key_cmc][key_colour][key_rarity]), 3)
                    db.session.add(PowerAverages(CardColour=str(key_colour),
                            rarity=str(key_rarity),
                            cmc=str(key_cmc),
                            card_average=float(average_power[key_cmc][key_colour][key_rarity]),
                            card_count=int(average_power_count[key_cmc][key_colour][key_rarity]))
                                   )

    # toughness
    # power
    for t_key_cmc, t_value_cmc in average_toughness.items():
        for t_key_colour, t_value_colour in t_value_cmc.items():
            for t_key_rarity, t_value_rarity in t_value_colour.items():
                # print ('{}, {}:{}'.format(value_cmc[key_rarity], value_rarity, average_power_count[key_cmc][key_rarity]))
                if average_toughness_count[t_key_cmc][t_key_colour][t_key_rarity] > 0:
                    average_toughness[t_key_cmc][t_key_colour][t_key_rarity] = round(
                        float(t_value_rarity / average_toughness_count[t_key_cmc][t_key_colour][t_key_rarity]), 3)

                    db.session.add(ToughnessAverages(CardColour=str(t_key_colour),
                                                 rarity=str(t_key_rarity),
                                                 cmc=str(t_key_cmc),
                                                 card_average=float(average_toughness[t_key_cmc][t_key_colour][t_key_rarity]),
                                                 card_count=int(average_toughness_count[t_key_cmc][t_key_colour][t_key_rarity]))
                                   )

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

    # add the users
    db.session.add(User(username='tom'))
    db.session.add(User(username='bobtheadmin', admin=True))
    db.session.add(User(username='julie'))
    db.session.commit()

    print('Added Users')

    print('Initialised the DB')


def get_all_cards(all_card_data):
    card_data = all_card_data['data']
    # if has more
    if all_card_data['has_more']:
        # print(all_card_data['next_page'])
        # request new uri
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

    # todo split of clearing ratings to an additional manage command
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

    socketio.run(app, host='192.168.1.70', port='5000')
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


def supertype_calculation(possible_supertypes_distinct):
    for supertype_list in possible_supertypes_distinct:
        sql_where = ''
        for supertype in supertype_list:
            sql_where += ' \'' + supertype + '\','
        sql_where = sql_where[:-1]
        sql_supertype_cards = 'SELECT COUNT(card_id) FROM ' \
                  '( SELECT CardSupertypes.card_id, Card.card_color, Card.card_rarity FROM CardSupertypes ' \
                  'INNER JOIN Card ON CardSupertypes.card_id=Card.id ' \
                              'WHERE CardSupertypes.supertype IN ({}) GROUP ' \
                  'BY CardSupertypes.card_id HAVING COUNT(CardSupertypes.card_id) = {} )AS SUPERTYPE_COUNT' \
                  .format(sql_where, len(supertype_list))
        #print(sql_supertype_cards)
        count_cards_by_supertype = db.session.execute(sql_supertype_cards).fetchall()[0][0]

        db.session.add(CardSupertypesMetrics(CardColour=str('All'),
                                         rarity=str('All'),
                                         supertypes=(sql_where.replace('\'','').strip()),
                                         card_count=int(count_cards_by_supertype))
                       )

        colour_list = ['W', 'U', 'B', 'R', 'G', 'colourless', 'multi-colour']
        rarity_list = ['common', 'uncommon', 'rare', 'mythic']
        for colour in colour_list:
            for rarity in rarity_list:
                sql_supertype_cards = 'SELECT COUNT(card_id) FROM ' \
                                      '( SELECT CardSupertypes.card_id, Card.card_color, Card.card_rarity FROM CardSupertypes ' \
                                      'INNER JOIN Card ON CardSupertypes.card_id=Card.id ' \
                                      'WHERE CardSupertypes.supertype IN ({}) GROUP ' \
                                      'BY CardSupertypes.card_id HAVING COUNT(CardSupertypes.card_id) = {} )AS SUPERTYPE_COUNT' \
                                      ' WHERE SUPERTYPE_COUNT.card_color = \'{}\' ' \
                                      'AND SUPERTYPE_COUNT.card_rarity = \'{}\' '\
                        .format(sql_where, len(supertype_list), colour, rarity)
                # print(sql_supertype_cards)
                count_cards_by_supertype = db.session.execute(sql_supertype_cards).fetchall()[0][0]

                db.session.add(CardSupertypesMetrics(CardColour=str(colour),
                                                      rarity=str(rarity),
                                                      supertypes=(sql_where.replace('\'', '').strip()),
                                                      card_count=int(count_cards_by_supertype))
                               )

    db.session.commit()


if __name__ == '__main__':
    manager.run()

