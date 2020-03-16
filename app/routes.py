__author__ = 'tomli'

from flask import render_template, url_for, flash, redirect, request
from app import app, db, socketio, card_info
from flask_socketio import emit
from database.models import Card, User, Votes
from flask_login import login_required, login_user, current_user
from app.main.forms import LoginForm
import datetime
from app.monitor import MonitorThread
from sqlalchemy import and_

thread_monitor = None
###############
##  Routes  ###
###############

@app.route('/')
@app.route('/index')
@login_required
def index():
    thread_check()

    return render_template('index.html')


@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    card_im = Card.query.filter_by(current_selected=True).first().card_image
    # Card.next_card()
    return render_template('vote.html', card_image=card_im)

# todo info, add blueprints set up app to work more cleanly

@app.route('/info', methods=['GET', 'POST'])
def info():
    # Card.next_card()
    metric_data = dict()
    metric_data['supertypes'] = get_supertypes()
    metric_data['powerav'] = get_averages('Power_Averages')
    metric_data['toughnessav'] = get_averages('Toughness_Averages')
    print(metric_data['powerav'])
    return render_template('infonew.html', **metric_data)


@app.route('/colourinfo/<colour>')
def colour_info(colour):

    # all cards
    card_data = card_info.get_card_colour_page_info(colour)

    return render_template('info_colour.html', **card_data)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    print(current_user.is_authenticated)
    print(current_user.admin)
    if current_user.admin:
    # Card.next_card()
        return render_template('admin.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # validate the user
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.logged_in is False:
                login_user(user)
                user.logged_in = True
                db.session.commit()
                flash("login Success")
                return redirect(request.args.get('next') or url_for('index'))
            return render_template('login.html', form=form)
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)

######################
## Socket io checks ##
######################

### vote ###
@socketio.on('score', namespace='/vote')
def score_recived(data):
    # handle the sent
    if card_info.wait_card is False:
        score = data['score']
        if score != '':
            print('score pressed')
            # Card.next_card()
            current_card_id = Card.query.filter_by(current_selected=True).first().id
            current_user_id = User.query.filter_by(username=current_user.username).first().id
            tracker_obj = Votes.query.filter((and_(Votes.card_id == current_card_id, Votes.user_id == current_user_id))).first()
            if tracker_obj:
                print('updated: ' + str(current_user_id) + ':' + str(current_card_id))
                tracker_obj.vote_score = score
            else:
                print('added: ' + str(current_user_id) + ':' + str(current_card_id))
                db.session.add(Votes(card_id=current_card_id, user_id=current_user_id, vote_score=score))

            db.session.commit()

            emit('vote_bar_message', {'button_disabled': True, 'current_votes': '', 'last_vote': ''})

    # emit('card_response', {'data': card_im})


@socketio.on('connect', namespace='/vote')
def voter_connect():
    # set the user to voting in the database
    print('login: ' + current_user.username)
    active = User.query.filter_by(username=current_user.username).first()
    active.voting = True
    db.session.commit()
    thread_check()

    card_info.send_card_info()


@socketio.on('disconnect', namespace='/vote')
def voter_disconnect():
    # set the user to no longer voting in the database
    active = User.query.filter_by(username=current_user.username).first()
    active.voting = False
    db.session.commit()

    print('disconnect: ' + str(current_user.username) + ' ' + str(datetime.datetime.now()))


### admin ###
@socketio.on('wait_card', namespace='/admin')
def wait_change(data):
    # set the wait_card bool to the required value
    # and change the card
    if 'wait' in data:
        card_info.wait_card = data['wait']
        print('wait_card: ' + str(card_info.wait_card))
        card_info.change_card()


@socketio.on('add_user', namespace='/admin')
def add_user(username):
    user_name = username
    user_exists = User.query.filter_by(username=user_name).first()
    if user_exists is None:
        print('adding - ' + user_name)
        db.session.add(User(username=user_name))
        db.session.commit()
        card_info.send_user_list()


@socketio.on('del_user', namespace='/admin')
def del_user(username):
    user_name = username
    print(username)
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    user_exists = User.query.filter_by(username=user_name).first()
    print(user_exists)
    User.query.filter_by(id=user_exists.id).delete()
    db.session.commit()
    card_info.send_user_list()


@socketio.on('re-vote', namespace='/admin')
def re_vote(data):
    card_info.re_vote(data)


@socketio.on('enable_vote_buttons', namespace='/admin')
def enable_vote_button():
    card_info.send_update_vote_bar(False)


@socketio.on('remove_voter', namespace='/admin')
def remove_voter(username):
    user_name = username
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    active = User.query.filter_by(username=user_name).first()
    active.voting = False
    db.session.commit()


@socketio.on('logout_voter', namespace='/admin')
def remove_voter(username):
    user_name = username
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    active = User.query.filter_by(username=user_name).first()
    active.voting = False
    active.logged_in = False
    db.session.commit()


def thread_check():
    # need visibility of the global thread object
    global thread_monitor
    # Start the monitoring thread if it hasn't already
    if thread_monitor is None:
        print("Starting Monitor Thread")
        thread_monitor = MonitorThread()
        thread_monitor.start()


def get_averages(table):
    return_averages = {}
    sql_average_cmc_sting = 'SELECT DISTINCT cmc FROM' \
                            ' {} '.format(table)
    card_cmcs_db = db.session.execute(sql_average_cmc_sting).fetchall()
    card_cmcs = []
    for card_cmc in card_cmcs_db:
        card_cmcs.append(list(card_cmc))

    for cmc in card_cmcs:
        return_averages[cmc[0]] = get_averge_by_cmc(cmc[0], table)
        print(return_averages[cmc[0]])
    return return_averages


def get_averge_by_cmc(cmc, table):
    sql_average_cmc_sting = 'SELECT card_colour, rarity, cmc, card_average, card_count FROM ' \
                           '{} WHERE cmc = \'{}\''.format(table, cmc)
    # print(sql_average_cmc_sting)
    card_averages_db = db.session.execute(sql_average_cmc_sting).fetchall()

    card_averages = []
    for card_db in card_averages_db:
        card_averages.append(list(card_db))

    return_dict = {'all': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'W': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'U': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'B': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'R': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'G': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'colourless': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   'multi-colour': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    rarity_pos = {'all': 1, 'common': 3, 'uncommon': 5, 'rare': 7, 'mythic': 9}

    for card_av in card_averages:
        # cmc
        num_position = rarity_pos[card_av[1]]
        #print(card_av[0])
        #print(return_dict)
        return_dict[card_av[0]][(num_position-1)] = card_av[3]
        return_dict[card_av[0]][num_position] = card_av[4]
        #print(return_dict[card_av[0]])

    return return_dict


def get_supertypes():
    return_averages = {}
    sql_average_supertype_sting = 'SELECT DISTINCT supertypes FROM' \
                            ' Card_Supertypes_Metrics '.format()
    card_supertypes_db = db.session.execute(sql_average_supertype_sting).fetchall()
    card_supertypes = []
    for card_supertype in card_supertypes_db:
        card_supertypes.append(list(card_supertype))

    for supertype in card_supertypes:
        return_averages[supertype[0]] = get_supertypes_by_type(supertype[0])
        #print(return_averages[cmc[0]])
    return return_averages


def get_supertypes_by_type(supertype):
    sql_average_cmc_sting = 'SELECT rarity, card_colour, card_count FROM ' \
                           'Card_Supertypes_Metrics WHERE supertypes = \'{}\''.format(supertype)
    # print(sql_average_cmc_sting)
    card_averages_db = db.session.execute(sql_average_cmc_sting).fetchall()

    card_averages = []
    for card_db in card_averages_db:
        card_averages.append(list(card_db))

    return_dict = {'All': [0, 0, 0, 0, 0],
                   'W': [0, 0, 0, 0, 0],
                   'U': [0, 0, 0, 0, 0],
                   'B': [0, 0, 0, 0, 0],
                   'R': [0, 0, 0, 0, 0],
                   'G': [0, 0, 0, 0, 0],
                   'colourless': [0, 0, 0, 0, 0],
                   'multi-colour': [0, 0, 0, 0, 0]}
    rarity_pos = {'All': 0, 'common': 1, 'uncommon': 2, 'rare': 3, 'mythic': 4}

    for card_av in card_averages:
        num_position = rarity_pos[card_av[0]]
        return_dict[card_av[1]][num_position] = card_av[2]

    return return_dict
