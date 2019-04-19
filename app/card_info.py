__author__ = 'tomli'

from app import socketio
from flask_socketio import emit
from app.models import Card, User, Votes, Rulings, Card_colour, Card_Subtypes
from app import app, db
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
    votes_list = Votes.query.filter_by(card_id=current_card.id).all()
    print(len(votes_list))
    return len(votes_list)


def get_current_votes_string():
    return "{} / {} votes ".format(get_current_vote_count(), get_current_voters())


def send_update_vote_bar( disable_all=None):
    votes = get_current_votes_string()
    emit('vote_bar_message', {'button_disabled': disable_all, 'current_votes': votes, 'last_vote': ''},
                        namespace='/vote', broadcast=True)


def send_card_info():
    card_info = get_card_info()
    emit('card_data_message', card_info, namespace='/vote', broadcast=True)
    emit('card_data_message', card_info, namespace='/info', broadcast=True)


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
        card_dict['info'][str(colour.colour)+':'+str(current_card.card_rarity)] = ' ' + str(solo_colour_rarity[0][0])


    #card sup types total
    card_subtypes = Card_Subtypes.query.filter_by(card_id=current_card.id).all()
    for subtype in card_subtypes:
        sql_subtype_str = 'SELECT COUNT(card_id) FROM' \
                          ' Card_Subtypes WHERE Card_Subtypes.subtype = \'{}\''.format(str(subtype.subtype))
        solo_type = db.session.execute(sql_subtype_str).fetchall()
        # print (solo_type)
        card_dict['info'][str(subtype.subtype)] = ' ' + str(solo_type[0][0])


    #card average power / toughness
    average_data = load_json()
    if current_card.card_cmc is not None:
        card_dict['info']['Average Power: All CMC ' + str(current_card.card_cmc)] = ' ' + str(average_data['average_power'][current_card.card_cmc]['all'])
        card_dict['info']['Average Toughness: All CMC ' + str(current_card.card_cmc)] = ' ' + str(average_data['average_toughness'][current_card.card_cmc]['all'])
        cmc_text = 'CMC ' + str(current_card.card_cmc) + ' ' + str(current_card.card_rarity)
        card_dict['info']['Average Power: ' + cmc_text] = ' ' + str(average_data['average_power'][current_card.card_cmc][current_card.card_rarity])
        card_dict['info']['Average Toughness: ' + cmc_text] = ' ' + str(average_data['average_toughness'][current_card.card_cmc][current_card.card_rarity])

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
        if next.name is "Wait Card":
            make_CSV()
            wait_card = True

    print('change card colour: ' + current.card_color + ' - ' + next.card_color)
    if current.card_color != next.card_color:
        print('not same colour')
        if next.card_color is not "":
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
    outfile = open('total_votes.csv', 'w', newline='')
    outcsv = csv.writer(outfile)

    sql_all_cards = 'SELECT * FROM Card'
    all_cards = db.session.execute(sql_all_cards)
    #print (all_cards.keys())
    outcsv.writerow(all_cards.keys())
    # dump rows
    outcsv.writerows(all_cards.fetchall())

    outfile.close()

    all_users = User.query.all()
    #loop through all users
    for user in all_users:
        #generate  csv for each user
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

    sql_all_cards = 'SELECT Card.*, Votes.vote_score FROM Card ' \
                    'INNER JOIN Votes ON Card.id=Votes.card_id WHERE Votes.user_id = \'{}\''.format(user.id)
    all_cards = db.session.execute(sql_all_cards)
    #print(all_cards.keys())
    outcsv.writerow(all_cards.keys())
    # dump rows
    outcsv.writerows(all_cards.fetchall())

    outfile.close()

def send_user_list():
    users = User.query.all()
    list_users = []
    list_voters = ''
    for user in users:
        user_str = user.username
        # print(user.username + '-' + str(user.voting))
        if user.voting:
            user_str += ' - Voter'
            list_voters += user.username + ', '

        list_users.append(user_str)

    data = {'user': list_users}
    voters = {'user': list_voters}
    emit('users', data, namespace='/admin', broadcast=True)
    emit('users', voters, namespace='/info', broadcast=True)

def reset_votes(id):
    Votes.query.filter_by(id=id).delete()
    card = Card.query.filter_by(id=id).first()
    card.rating = None
    Votes.query.filter_by(card_id=id).delete()
    db.session.commit()

def re_vote(id):
    if id == 'current':
        current = Card.query.filter_by(current_selected=True).first()
        reset_votes(current.id)
    elif id == 'previous':
        current = Card.query.filter_by(current_selected=True).first()
        previous = current.id - 1
        if previous > 0:
            previous_card = Card.query.filter_by(id=previous).first()
            reset_votes(previous_card.id)
    else:
        reset_votes(id)


def send_ratings():
    # top 10 higest rated cards
    # name, rating, colour, rarity
    # print('send_ratings')
    sql_card_rating_str = 'SELECT name, rating, card_color, card_rarity FROM' \
                          ' Card ORDER BY rating DESC LIMIT 15'
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = []
    for card_all in card_ratings_db:
        card_ratings.append(list(card_all))

    all_card_ratings = {'card_ratings': card_ratings}

    # print(card_ratings)
    emit('all_card_ratings', all_card_ratings, namespace='/info', broadcast=True)


def send_pervious_voted():
    # get the previous card. the last voted on card? if card not none rating sort desc?
    current = Card.query.filter_by(current_selected=True).first()

    next_id = current.id - 1
    if next_id>0:
        sql_prev_card_str = 'SELECT id, name, rating, card_color, card_rarity FROM' \
                            ' Card WHERE id = \'{}\''.format(next_id)
        prev_card_db = db.session.execute(sql_prev_card_str).first()
        if prev_card_db:
            all_votes_sql = 'SELECT User.username, Votes.vote_score FROM Votes ' \
                      'INNER JOIN User ON User.id=Votes.user_id WHERE Votes.card_id = \'{}\''.format(prev_card_db[0])
            prev_card_votes_db = db.session.execute(all_votes_sql).fetchall()
            # print(prev_card_votes_db)
            card_ratings = []
            for card_all_prev in prev_card_votes_db:
                prev_list = list(card_all_prev)
                prev_list[1] = prev_list[1]/2
                card_ratings.append(prev_list)
            #get the card name and its vote, other info?

            # prev_votes = [[]]
            # prev_card_info = []
            previous_card_data = {'prev_card_info': [list(prev_card_db)], 'prev_card_votes':  card_ratings}
            # print (previous_card_data)
            emit('previous_card', previous_card_data, namespace='/info', broadcast=True)

def get_card_colour_page_info(colour):
    #all cards of the colour
    sql_card_rating_str = 'SELECT name, rating, card_rarity FROM' \
                          ' Card where card_color = \'{}\' ORDER BY rating DESC LIMIT 20'.format(colour)
    card_ratings_db = db.session.execute(sql_card_rating_str).fetchall()
    card_ratings = []
    for card_all in card_ratings_db:
        card_ratings.append(list(card_all))

    # commons in the colour
    sql_card_common_rating_str = 'SELECT name, rating, card_rarity FROM' \
                                 ' Card where card_color = \'{}\' and ' \
                                 'card_rarity = \'common\' ORDER BY rating DESC LIMIT 20'.format(colour)
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


    all_card_ratings = {'card_ratings': card_ratings, 'common_ratings': card_common_ratings, 'bg_colour': bg_colour}

    return all_card_ratings


def save_json(data):
    with open('app/static/additional_info.json', 'w') as outfile:
        json.dump(data, outfile)


def load_json():
    with open('app/static/additional_info.json', 'r') as json_file:
        json_data = json.load(json_file)
    return json_data