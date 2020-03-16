from . import main
from.forms import LoginForm
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_required, login_user, current_user

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
    card_im = Card.query.filter_by(current_selected=True).first().card_image
    # Card.next_card()
    return render_template('vote.html', card_image=card_im)


@main.route('/info', methods=['GET', 'POST'])
def info():
    # Card.next_card()
    metric_data = dict()
    metric_data['supertypes'] = get_supertypes()
    metric_data['powerav'] = get_averages('Power_Averages')
    metric_data['toughnessav'] = get_averages('Toughness_Averages')
    print(metric_data['powerav'])
    return render_template('infonew.html', **metric_data)


@main.route('/colourinfo/<colour>')
def colour_info(colour):
    # all cards
    card_data = card_info.get_card_colour_page_info(colour)

    return render_template('info_colour.html', **card_data)


@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    print(current_user.is_authenticated)
    print(current_user.admin)
    if current_user.admin:
    # Card.next_card()
        return render_template('admin.html')
    else:
        return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
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