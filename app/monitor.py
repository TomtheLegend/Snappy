__author__ = 'tomli'
from threading import Thread, Event
from app import socketio
from app.models import Card, User, Votes, Rulings
from app import app, db
from time import sleep
from flask_socketio import emit

thread = Thread()
thread_stop_event = Event()


class MonitorThread(Thread):
    def __init__(self):
        self.delay = 5
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
                print('user_voters_count: ' + str(user_voters_count))

                #get tracker count, ensure all votes collected
                votes_list = Votes.query.filter_by(card_id=current_card.id).all()
                print('votes_list count: ' + str(len(votes_list)))
                if len(votes_list) == user_voters_count and user_voters_count > 0:
                    # calculate score and update the Card  table
                    average_vote = 0
                    for vote in votes_list:
                        average_vote += int(vote.vote_score)

                    # add all votes together, divide by user number and half for stars
                    average_vote = (average_vote / len(votes_list)) / 2
                    current_card.rating = average_vote
                    db.session.commit()

                    # update to  next card
                    Card.next_card()
                    current_card = Card.query.filter_by(current_selected=True).first()

                    # get the data for current card and send to users

                    emit('card_data_message', self.get_card_info(),  namespace='/', broadcast=True)

                    # show the button for all users
                    self.send_update_vote_bar(False)

                #update the vote bar for voters, showing number of voters.
                self.send_update_vote_bar()

                sleep(self.delay)

    def run(self):
        self.monitor_function()


    def get_current_voters(self):
        user_voters_count = 0
        current_users = User.query.filter_by(voting=True).all()
        for user in current_users:
            user_voters_count += 1
        return user_voters_count


    def get_current_vote_count(self):
        current_card = Card.query.filter_by(current_selected=True).first()
        votes_list = Votes.query.filter_by(card_id=current_card.id).all()
        print(len(votes_list))
        return len(votes_list)

    def get_current_votes_string(self):
        return "{} / {} votes ".format(self.get_current_vote_count(), self.get_current_voters())

    def send_update_vote_bar(self, disable_all=''):
        votes = self.get_current_votes_string()
        print (disable_all)
        emit('vote_bar_message', {'button_disabled': disable_all, 'current_votes': votes, 'last_vote': ''},  namespace='/', broadcast=True)

    def get_card_info(self):
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


        return card_dict




