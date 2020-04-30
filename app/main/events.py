from app import main_app
from flask_login import current_user
from flask_socketio import emit
from app.settings import config
from cardinformation.voterpage import change_card, send_user_list, re_vote, send_update_vote_bar
from database import update


@main_app.socket_io.on('score', namespace='/vote')
def score_recived(data):
    # handle the sent
    if config['wait_card'].wait_card is False:
        score = data['score']
        update.update_user_score_for_current_card(score, current_user)
        emit('vote_bar_message', {'button_disabled': True, 'current_votes': '', 'last_vote': ''})

    # emit('card_response', {'data': card_im})


@main_app.socket_io.on('connect', namespace='/vote')
def voter_connect():
    # set the user to voting in the database
    # print('login: ' + current_user.username)
    main_app.thread_check()
    # card_info.send_card_info()


@main_app.socket_io.on('disconnect', namespace='/vote')
def voter_disconnect():
    # set the user to no longer voting in the database
    update.update_user_voting(current_user)

    # print('disconnect: ' + str(current_user.username) + ' ' + str(datetime.datetime.now()))


### admin ###
@main_app.socket_io.on('wait_card', namespace='/admin')
def wait_change(data):
    # set the wait_card bool to the required value
    # and change the card
    if 'wait' in data:
        config['wait_card'] = data['wait']
        print('wait_card: ' + str(data['wait']))
        change_card()


@main_app.socket_io.on('add_user', namespace='/admin')
def add_user(username):
    if add_user(username):
        send_user_list()


@main_app.socket_io.on('del_user', namespace='/admin')
def del_user(username):
    user_name = username
    # print(username)
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    send_user_list()


@main_app.socket_io.on('re-vote', namespace='/admin')
def re_vote(data):
    re_vote(data)


@main_app.socketio.on('enable_vote_buttons', namespace='/admin')
def enable_vote_button():
    send_update_vote_bar(False)


@main_app.socket_io.on('remove_voter', namespace='/admin')
def remove_voter(username):
    user_name = username
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    update.update_user_not_voting(user_name)


@main_app.socket_io.on('logout_voter', namespace='/admin')
def logout_voter(username):
    user_name = username
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    update.logout_voter(user_name)
