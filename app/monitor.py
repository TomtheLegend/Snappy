__author__ = 'tomli'
from threading import Thread, Event
from database.models import Card, User, Ratings
from app import main_app
from time import sleep
from cardinformation import voterpage, infopage
from app.settings import config

thread = Thread()
thread_stop_event = Event()


class MonitorThread(Thread):
    def __init__(self, app):
        self.delay = 2
        self.app = app
        super(MonitorThread, self).__init__()

    def monitor_function(self):
        """
        thread to monitor the db and to change cards and log the final score
        """
        with self.app.app_context():
            while not thread_stop_event.isSet():

                # get current card
                current_card = Card.query.filter_by(current_selected=True).first()
                print('current_card: ' + current_card.name)
                # get active users / count
                user_voters_count = 0
                current_users = User.query.filter_by(voting=True).all()
                for _ in current_users:
                    user_voters_count += 1
                print('active_voters_count: ' + str(user_voters_count))
                voterpage.send_update_vote_bar()

                # get tracker count, ensure all Ratings collected
                ratings_list = Ratings.query.filter_by(card_id=current_card.id).all()
                print('current_cast_Ratings: ' + str(len(ratings_list)))

                all_voted = True
                # #  check the voters have actually voted.
                for voter in current_users:
                    voted = False
                    for vote in ratings_list:
                        if voter.id == vote.user_id:
                            voted = True
                            break
                    if not voted:
                        all_voted = False
                        break

                if all_voted and user_voters_count > 0 and config['wait_card'] is False:
                    # calculate score and update the Card  table
                    average_vote = 0
                    for vote in ratings_list:
                        average_vote += float(vote.vote_score)
                    # todo move to database files
                    # add all Ratings together, divide by user number and half for stars
                    vote_av_raw = (average_vote / len(ratings_list)) / 2
                    average_vote = round((vote_av_raw*2), 1) / 2
                    current_card.rating = average_vote
                    main_app.db.session.commit()

                    # update to next card
                    voterpage.change_card()

                voterpage.send_user_list()
                voterpage.send_ratings()
                infopage.send_previous_voted()
                sleep(self.delay)

    def run(self):
        self.monitor_function()


# set the monitor thread
monitor_thread = MonitorThread(main_app.app)


def monitor_thread_start():
    # Start the monitoring thread if it hasn't already
    if monitor_thread is not None and monitor_thread.is_alive() is False:
        print("Starting Monitor Thread")
        monitor_thread.start()

