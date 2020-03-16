__author__ = 'tomli'

from flask_wtf import Form
from wtforms.fields import StringField,SubmitField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField('Your Username:', validators=[DataRequired()])
    submit = SubmitField('Log In')