
from .models import User, Card, Ratings
from app import main_app
from database import searchcards
from sqlalchemy import and_
from flask_login import login_user


def login_user_to_app(user):
    if user is not None:

        if user.logged_in is False:
            print(user)
            login_user(user)
            user.logged_in = True
            main_app.db.session.commit()


def switch_to_wait_card(wait_card_name):
    searchcards.current_card().current_selected = False
    colour_wait_card_selected = searchcards.get_card_by_name(wait_card_name)
    colour_wait_card_selected.current_selected = True
    main_app.db.session.commit()


def switch_to_next_card():
    searchcards.current_card().current_selected = False
    searchcards.next_card().current_selected = True
    main_app.db.session.commit()


def reset_ratings(card_id):
    Ratings.query.filter_by(id=card_id).delete()
    card = Card.query.filter_by(id=card_id).first()
    card.rating = None
    Ratings.query.filter_by(card_id=card_id).delete()
    main_app.db.session.commit()


def update_user_score_for_current_card(score, user):
    if score != '':
        current_card_id = Card.query.filter_by(current_selected=True).first().id
        current_user_id = User.query.filter_by(username=
                                               user.username).first().id
        tracker_obj = Ratings.query.filter((and_(Ratings.card_id == current_card_id,
                                                 Ratings.user_id == current_user_id))).first()
        if tracker_obj:
            # print('updated: ' + str(current_user_id) + ':' + str(current_card_id))
            tracker_obj.vote_score = score
        else:
            # print('added: ' + str(current_user_id) + ':' + str(current_card_id))
            main_app.db.session.add(Ratings(card_id=current_card_id,
                                   user_id=current_user_id,
                                   vote_score=score))
        main_app.db.session.commit()


def update_user_voting(user):
    active = User.query.filter_by(username=user.username).first()
    active.voting = True
    main_app.db.session.commit()


def update_user_not_voting(user):
    active = User.query.filter_by(username=user).first()
    if active:
        active.voting = False
        main_app.db.session.commit()


def add_user(username):
    user_exists = User.query.filter_by(username=username).first()
    if user_exists is None:
        # print('adding - ' + username)
        main_app.db.session.add(User(username=username.lower()))
        main_app.db.session.commit()
        return True
    else:
        return False


def delete_user(username):
    user_exists = User.query.filter_by(username=username).first()
    # print(user_exists)
    if user_exists:
        User.query.filter_by(id=user_exists.id).delete()
        main_app.db.session.commit()


def logout_voter(username):
    active = User.query.filter_by(username=username).first()
    if active:
        active.voting = False
        active.logged_in = False
        main_app.db.session.commit()