__author__ = 'tomli'
from threading import Thread, Event
from app import socketio
from app.models import Card, User, Votes
from app import app, db, card_info
from time import sleep
from flask_socketio import emit
from app import card_info
import time


thread = Thread()
thread_stop_event = Event()


class MonitorThread(Thread):
    def __init__(self):
        self.delay = 2
        super(MonitorThread, self).__init__()

    def monitor_function(self):
        """
        thread to monitor the db and to change cards and log the final score
        """
        with app.app_context():
            while not thread_stop_event.isSet():

                # get surrent card
                current_card = Card.query.filter_by(current_selected=True).first()
                print('current_card: ' + current_card.name)
                #get active users / count
                user_voters_count = 0
                current_users = User.query.filter_by(voting=True).all()
                for user in current_users:
                        user_voters_count += 1
                print('active_voters_count: ' + str(user_voters_count))
                card_info.send_update_vote_bar()

                # get tracker count, ensure all votes collected
                votes_list = Votes.query.filter_by(card_id=current_card.id).all()
                print('current_cast_votes: ' + str(len(votes_list)))

                all_voted = True
                # #  check the voters have actually voted.
                for voter in current_users:
                    voted = False
                    for vote in votes_list:
                        if voter.id == vote.user_id:
                            voted = True
                            break
                    if not voted:
                        all_voted = False
                        break

                if all_voted and user_voters_count > 0 and card_info.wait_card is False:
                    # calculate score and update the Card  table
                    average_vote = 0
                    for vote in votes_list:
                        average_vote += float(vote.vote_score)

                    # add all votes together, divide by user number and half for stars
                    vote_av_raw = (average_vote / len(votes_list)) / 2
                    average_vote = round((vote_av_raw*2), 1)/2
                    current_card.rating = average_vote
                    db.session.commit()

                    # update to next card
                    card_info.change_card()

                card_info.send_user_list()
                card_info.send_ratings()
                card_info.send_pervious_voted()
                sleep(self.delay)

    def run(self):
        self.monitor_function()






