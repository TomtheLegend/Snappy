from . import main
from.forms import LoginForm
from flask import render_template, url_for, redirect, request
from flask_login import login_required, current_user
from cardinformation.infopage import get_averages, get_supertypes
from cardinformation.colourpage import get_card_colour_page_info
from database.searchcards import current_card
from database.searchusers import get_user
from database import update
###############
##  Routes  ###
###############

@main.route('/')
@main.route('/index')
@login_required
def index():
    # thread_check()
    return render_template('index.html')


@main.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    card_im = current_card().card_image
    # Card.next_card()
    return render_template('vote.html', card_image=card_im)


@main.route('/info', methods=['GET', 'POST'])
def info():
    metric_data = dict()
    metric_data['supertypes'] = get_supertypes()
    metric_data['powerav'] = get_averages('Power_Averages')
    metric_data['toughnessav'] = get_averages('Toughness_Averages')
    # print(metric_data['powerav'])
    return render_template('infonew.html', **metric_data)


@main.route('/colourinfo/<colour>')
def colour_info(colour):
    card_data = get_card_colour_page_info(colour)
    return render_template('info_colour.html', **card_data)


@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.admin:
        return render_template('admin.html')
    else:
        return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.username.data)
        if user is not None:
            if user.logged_in is False:
                update.login_user(user)
                return redirect(request.args.get('next') or url_for('index'))
            return render_template('login.html', form=form)
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)
