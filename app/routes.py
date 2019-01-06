__author__ = 'tomli'

from flask import Flask, render_template, url_for, flash, redirect, request, session
from app import app, db, socketio, card_info
from flask_socketio import emit
from app.models import Card, User, Votes
from flask_login import login_required, login_user, current_user
from app.forms import LoginForm
import time, datetime
from app.monitor import MonitorThread, thread

from sqlalchemy import and_, exists


@app.route('/')
@app.route('/index')
@login_required
def index():
    # need visibility of the global thread object
    global thread
    #Start the monitoring thread if it hasn't already
    if not thread.isAlive():
        print("Starting Thread")
        thread = MonitorThread()
        thread.start()

    return render_template('index.html')


@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    card_im = Card.query.filter_by(current_selected=True).first().card_image
    # Card.next_card()
    return render_template('vote.html', card_image=card_im)


@app.route('/info', methods=['GET', 'POST'])
def info():
    # Card.next_card()
    return render_template('info.html')


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
                print('updated: ' +str(current_user_id) + ':' + str(current_card_id))
                tracker_obj.vote_score = score
            else:
                print('added: ' +str(current_user_id) + ':' + str(current_card_id))
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
    if '-' in user_name:
        user_name = user_name.split('-')[0].strip()
    user_exists = User.query.filter_by(username=user_name).first()
    User.query.filter_by(id=user_exists.id).delete()
    db.session.commit()
    card_info.send_user_list()


@socketio.on('re-vote', namespace='/admin')
def re_vote(data):
    card_info.re_vote(data)
