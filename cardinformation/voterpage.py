from flask_socketio import emit
from database import searchcards, searchusers, update
from cardinformation.cardchecks import get_card_info
from cardinformation.colourpage import get_card_colour_page_info
from app.settings import config


def get_current_voters():
    user_voters_count = 0
    current_users = searchusers.get_all_users()
    if current_users:
        for _ in current_users:
            user_voters_count += 1
    return user_voters_count


def get_current_vote_count():

    current_card = searchcards.current_card()
    ratings_list = searchcards.get_current_card_ratings()

    current_users = searchusers.get_all_users()
    voted_number = 0

    for voter in current_users:
        for vote in ratings_list:
            if voter.id == vote.user_id:
                voted_number += 1
                break

    # print(voted_number)
    return str(voted_number)


def get_current_ratings_string():
    return "{} / {} Ratings ".format(get_current_vote_count(), get_current_voters())


def send_update_vote_bar(disable_all=None):
    Ratings = get_current_ratings_string()
    emit('vote_bar_message',
         {'button_disabled': disable_all, 'current_Ratings': Ratings, 'last_vote': ''},
         namespace='/vote',
         broadcast=True)


def send_card_info():
    card_info = get_card_info()
    emit('card_data_message', card_info, namespace='/vote', broadcast=True)
    emit('card_data_message', card_info, namespace='/info', broadcast=True)


def send_user_list():
    users = searchusers.get_all_users()
    # get voted list
    voted = searchcards.get_current_card_ratings()
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


def change_card():
    wait_card = config['wait_card']
    # set wait_colour to none as default
    wait_colour = None
    # check if colour changing, if so select the wait card.
    current = searchcards.current_card()
    next_card = searchcards.next_card()
    # check for no colour to see if its a wait card.
    if next_card is None:
            # reached the end so output CSV
            # todo send link to download pages, download individual and total csvs
            # make_CSV()
            wait_card = True
    else:
        if next_card.name == "Wait Card":
            # make_CSV()
            wait_card = True

    # todo add in an end of voting card and have it loop at this card

    print('change card colour: ' + current.card_color + ' - ' + next_card.card_color)
    if current.card_color != next_card.card_color:
        print('not same colour')
        if next_card.card_color != "":
            wait_colour = current.card_color

    if wait_colour:
        # change to the relevant wait card for the colour
        print('load wait card')
        card_name = 'Wait Card {}'.format(wait_colour)
        update.switch_to_wait_card(card_name)
    # check if the wait screen is required
    elif wait_card:
        update.switch_to_wait_card("Wait Card")
    else:
        update.switch_to_next_card()
            #send_update_vote_bar(False)

    send_card_info()
    send_update_vote_bar(wait_card)


def re_vote(id):
    if id == 'current':
        current = searchcards.current_card()
        update.reset_ratings(current.id)
    elif id == 'previous':
        current = searchcards.current_card()
        previous = current.id - 1
        if previous > 0:
            previous_card = searchcards.get_card_by_id(previous)
            update.reset_ratings(previous_card.id)
    else:
        update.reset_ratings(id)


def send_ratings():
    # top 10 higest rated cards
    # name, rating, colour, rarity
    # print('send_ratings')
    card_ratings = searchcards.get_top_cards_by_rating()

    card_colour_ratings = get_card_colour_page_info(searchcards.current_card().card_color)

    all_card_ratings = {'card_ratings': card_ratings}
    all_card_ratings.update(card_colour_ratings)
    # print(card_ratings)
    emit('all_card_ratings', all_card_ratings, namespace='/info', broadcast=True)