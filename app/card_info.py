__author__ = 'tomli'

from flask_socketio import emit
from database.models import Card, User, Ratings, Rulings, CardColour, CardSubtypes
from app import db
import csv
import json

wait_card = True
wait_colour = None


def get_current_voters():
    user_voters_count = 0
    current_users = User.query.filter_by(voting=True).all()
    for user in current_users:
        user_voters_count += 1
    return user_voters_count


def get_current_vote_count():

    current_card = Card.query.filter_by(current_selected=True).first()
    Ratings_list = Ratings.query.filter_by(card_id=current_card.id).all()

    current_users = User.query.filter_by(voting=True).all()
    voted_number = 0

    for voter in current_users:
        for vote in Ratings_list:
            if voter.id == vote.user_id:
                voted_number += 1
                break

    print(voted_number)
    return str(voted_number)


def get_current_Ratings_string():
    return "{} / {} Ratings ".format(get_current_vote_count(), get_current_voters())


def send_update_vote_bar( disable_all=None):
    Ratings = get_current_Ratings_string()
    emit('vote_bar_message', {'button_disabled': disable_all, 'current_Ratings': Ratings, 'last_vote': ''},
                        namespace='/vote', broadcast=True)


def send_card_info():
    card_info = get_card_info()
    emit('card_data_message', card_info, namespace='/vote', broadcast=True)
    emit('card_data_message', card_info, namespace='/info', broadcast=True)


def get_card_info():
    '''
    collect info related to the current card
    dict is split into sections to copy the page, each section is added separately
    returns: dict of all data
    '''
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
    CardColours = CardColour.query.filter_by(card_id=current_card.id).all()
    for colour in CardColours:
        #cards in the colour
        sql_colour_str = 'SELECT COUNT(card_id) FROM ' \
                  '( SELECT card_id, colour FROM CardColour GROUP BY card_id HAVING COUNT(card_id) = 1 )AS ONLY_ONCE' \
                  ' WHERE ONLY_ONCE.colour = \'{}\''.format(str(colour.colour))
        solo_colour = db.session.execute(sql_colour_str).fetchall()
        card_dict['info'][str(colour.colour)] = ':all - ' + str(solo_colour[0][0])
        # rarity in the colour
        sql_rariry_str = 'SELECT COUNT(card_id) FROM ' \
                  '( SELECT CardColour.card_id, CardColour.colour, Card.card_rarity FROM CardColour ' \
                  'INNER JOIN Card ON CardColour.card_id=Card.id GROUP ' \
                  'BY CardColour.card_id HAVING COUNT(CardColour.card_id) = 1 )AS ONLY_ONCE' \
                  ' WHERE ONLY_ONCE.colour = \'{}\' ' \
                  'AND ONLY_ONCE.card_rarity = \'{}\''.format(str(colour.colour), current_card.card_rarity)
        solo_colour_rarity = db.session.execute(sql_rariry_str).fetchall()
        card_dict['info'][str(colour.colour)+':'+str(current_card.card_rarity)] = ' ' + str(solo_colour_rarity[0][0])


    # card sub types total
    all_CardSubtypes = CardSubtypes.query.filter_by(card_id=current_card.id).all()
    for subtype in all_CardSubtypes:
        sql_subtype_str = 'SELECT COUNT(card_id) FROM' \
                          ' CardSubtypes WHERE CardSubtypes.subtype = \'{}\''.format(str(subtype.subtype))
        solo_type = db.session.execute(sql_subtype_str).fetchall()
        # print (solo_type)
        card_dict['info'][str(subtype.subtype)] = ' ' + str(solo_type[0][0])

    return card_dict


def change_card():
    global wait_card
    # set wait_colour to none as default
    wait_colour = None
    # check if colour changing, if so select the wait card.
    current = Card.query.filter_by(current_selected=True).first()
    next = Card.query.filter_by(rating=None).first()
    # check for no colour to see if its a wait card.
    if next is None:
            # reached the end so output CSV
            make_CSV()
            wait_card = True
    else:
        if next.name == "Wait Card":
            make_CSV()
            wait_card = True

    # todo add in an end of voting card and have it loop at this card

    print('change card colour: ' + current.card_color + ' - ' + next.card_color)
    if current.card_color != next.card_color:
        print('not same colour')
        if next.card_color != "":
            wait_colour = current.card_color

    if wait_colour:
        #change to the relevant wait card for the colour
        print('load wait card')
        card_name = 'Wait Card {}'.format(wait_colour)
        current.current_selected = False
        colour_wait_card_selected = Card.query.filter_by(name=card_name).first()
        colour_wait_card_selected.current_selected = True
        db.session.commit()

    # check if the wait screen is required
    elif wait_card:

        current.current_selected = False
        wait_card_selected = Card.query.filter_by(name="Wait Card").first()
        wait_card_selected.current_selected = True
        db.session.commit()
        #send_update_vote_bar(True)

    else:
        current.current_selected = False
        next.current_selected = True
        db.session.commit()
            #send_update_vote_bar(False)

    send_card_info()
    send_update_vote_bar(wait_card)


def make_CSV():
    # output cards data to local CSV
    outfile = open('total_Ratings.csv', 'w', newline='')
    outcsv = csv.writer(outfile)

    sql_all_cards = 'SELECT * FROM Card'
    all_cards = db.session.execute(sql_all_cards)
    # print (all_cards.keys())
    outcsv.writerow(all_cards.keys())
    # dump rows
    outcsv.writerows(all_cards.fetchall())

    outfile.close()

    all_users = User.query.all()
    # loop through all users
    for user in all_users:
        # generate  csv for each user
        user_CSV(user)

    # set to card waiting forever
    wait_card_selected = Card.query.filter_by(name="Wait Card").first()
    wait_card_selected.current_selected = True
    db.session.commit()
    wait_card = True


def user_CSV(user):
    '''
    User: string value for the users name
    '''
    outfile = open('app/static/csvs/' + user.username + '.csv', 'w', newline='')
    outcsv = csv.writer(outfile)

    sql_all_cards = 'SELECT Card.*, Ratings.vote_score FROM Card ' \
                    'INNER JOIN Ratings ON Card.id=Ratings.card_id WHERE Ratings.user_id = \'{}\''.format(user.id)
    all_cards = db.session.execute(sql_all_cards)
    #print(all_cards.keys())
    outcsv.writerow(all_cards.keys())
    # dump rows
    outcsv.writerows(all_cards.fetchall())

    outfile.close()


def send_user_list():
    users = User.query.all()
    # get current card
    current_card = Card.query.filter_by(current_selected=True).first()
    #get voted list
    voted = Ratings.query.filter_by(card_id=current_card.id).all()
    voters = []
    for voter in voted:
        voters.append(voter.user_id)

    list_users = []
    list_voters = ''
    for user in users:
        user_str = user.username
        # print(user.username + '-' + str(user.voting))
        if user.voting:
            user_str += ' - Voter'
            if user.id in voters:
                list_voters += '<mark>' + user.username + '</mark>, '
            else:
                list_voters += user.username + ', '

        list_users.append(user_str)

    data = {'user': list_users}
    voters = {'user': list_voters}
    emit('users', data, namespace='/admin', broadcast=True)
    emit('users', voters, namespace='/info', broadcast=True)


def reset_Ratings(id):
    Ratings.query.filter_by(id=id).delete()
    card = Card.query.filter_by(id=id).first()
    card.rating = None
    Ratings.query.filter_by(card_id=id).delete()
    db.session.commit()

def re_vote(id):
    if id == 'current':
        current = Card.query.filter_by(current_selected=True).first()
        reset_Ratings(current.id)
    elif id == 'previous':
        current = Card.query.filter_by(current_selected=True).first()
        previous = current.id - 1
        if previous > 0:
            previous_card = Card.query.filter_by(id=previous).first()
            reset_Ratings(previous_card.id)
    else:
        reset_Ratings(id)


def send_ratings():
    # top 10 higest rated cards
    # name, rating, colour, rarity
    # print('send_ratings')
    current_card = Card.query.filter_by(current_selected=True).first()

    sql_card_rating_str = 'SELECT name, rating, card_color, card_rarity, card_image FROM' \
                          ' Card ORDER BY rating DESC LIMIT 10'
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = []
    for card_all in card_ratings_db:
        card_ratings.append(list(card_all))

    # todo add commons/ colour / power/ toughness/ supertypes? inbed card image for tooltip hover.
    CardColour_ratings = get_CardColour_page_info(current_card.card_color)

    all_card_ratings = {'card_ratings': card_ratings}
    all_card_ratings.update(CardColour_ratings)
    # print(card_ratings)
    emit('all_card_ratings', all_card_ratings, namespace='/info', broadcast=True)


def send_pervious_voted():
    # get the previous card. the last voted on card? if card not none rating sort desc?
    current = Card.query.filter_by(current_selected=True).first()

    next_id = current.id - 1
    if next_id>0:
        sql_prev_card_str = 'SELECT id, name, rating, card_color, card_rarity  FROM' \
                            ' Card WHERE id = \'{}\''.format(next_id)
        prev_card_db = db.session.execute(sql_prev_card_str).first()
        if prev_card_db:
            all_Ratings_sql = 'SELECT User.username, Ratings.vote_score FROM Ratings ' \
                      'INNER JOIN User ON User.id=Ratings.user_id WHERE Ratings.card_id = \'{}\''.format(prev_card_db[0])
            prev_card_Ratings_db = db.session.execute(all_Ratings_sql).fetchall()
            # print(prev_card_Ratings_db)
            card_ratings = []
            for card_all_prev in prev_card_Ratings_db:
                prev_list = list(card_all_prev)
                prev_list[1] = prev_list[1]/2
                card_ratings.append(prev_list)
            # get the card name and its vote, other info?

            # prev_Ratings = [[]]
            # prev_card_info = []
            previous_card_data = {'prev_card_info': [list(prev_card_db)], 'prev_card_Ratings':  card_ratings}
            # print (previous_card_data)
            emit('previous_card', previous_card_data, namespace='/info', broadcast=True)


def get_CardColour_page_info(colour):
    # all cards of the colour
    sql_card_rating_str = 'SELECT name, rating, card_rarity, card_image FROM' \
                          ' Card where card_color = \'{}\' ORDER BY rating DESC LIMIT 10'.format(colour)
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = []
    for card_all in card_ratings_db:
        card_ratings.append(list(card_all))

    # commons
    sql_card_common_rating_str = 'SELECT name, rating, card_color, card_image FROM' \
                                 ' Card where card_rarity = \'common\' ORDER BY' \
                                 ' rating DESC LIMIT 10'.format(colour)
    card_common_ratings_db = db.session.execute(sql_card_common_rating_str).fetchall()
    card_common_ratings = []
    for card_common_all in card_common_ratings_db:
        card_common_ratings.append(list(card_common_all))

    # background colour

    bg_colours = {'W': '#eadede',
                  'U': '#4b81d8',
                  'B': '#1c1d1e',
                  'R': '#af2626',
                  'G': '#339b41',
                  'multi-colour': '#bc3cba',
                  'colourless': '#898189'}

    bg_colour = '#FFFFFF'
    if colour in bg_colours:
        bg_colour = bg_colours[colour]

    all_card_ratings = {'CardColour_ratings': card_ratings, 'common_ratings': card_common_ratings,
                        'bg_colour': bg_colour, }

    return all_card_ratings

def save_json(data):
    with open('app/static/additional_info.json', 'w') as outfile:
        json.dump(data, outfile)


def load_json():
    with open('app/static/additional_info.json', 'r') as json_file:
        json_data = json.load(json_file)
    return json_data
