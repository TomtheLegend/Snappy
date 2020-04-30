import csv
from app import db
from database.models import User, Card


def make_csv():
    # output cards data to local CSV
    outfile = open('total_Ratings.csv', 'w', newline='')
    out_csv = csv.writer(outfile)

    sql_all_cards = 'SELECT * FROM Card'
    all_cards = db.session.execute(sql_all_cards)
    # print (all_cards.keys())
    out_csv.writerow(all_cards.keys())
    # dump rows
    out_csv.writerows(all_cards.fetchall())

    outfile.close()

    all_users = User.query.all()
    # loop through all users
    for user in all_users:
        # generate  csv for each user
        user_csv(user)

    # set to card waiting forever
    wait_card_selected = Card.query.filter_by(name="Wait Card").first()
    wait_card_selected.current_selected = True
    db.session.commit()
    # wait_card = True


def user_csv(user):
    """
    User: string value for the users name
    """
    outfile = open('app/static/csvs/' + user.username + '.csv', 'w', newline='')
    outcsv = csv.writer(outfile)

    sql_all_cards = 'SELECT Card.*, Ratings.vote_score FROM Card ' \
                    'INNER JOIN Ratings ON Card.id=Ratings.card_id WHERE Ratings.user_id = \'{}\''.format(user.id)
    all_cards = db.session.execute(sql_all_cards)
    # print(all_cards.keys())
    outcsv.writerow(all_cards.keys())
    # dump rows
    outcsv.writerows(all_cards.fetchall())

    outfile.close()