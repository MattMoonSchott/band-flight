from flask_wtf import Form
from wtforms import StringField, DateField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

"""
Form for handling
SongKick queries.
"""


class SKForm(Form):
    locale = StringField('Locale', validators=[DataRequired()])
    place = StringField('Location', validators=[DataRequired(message="Location Required")])
    start = DateField('Start Date', validators=[DataRequired(message="Start Date Required")])
    end = DateField('End Date', validators=[DataRequired(message="End Date Required")])


"""
Registration Form
"""


class Registration(Form):
    username = StringField('Username', [Length(min=4, max=25)])

    # Password must be between 6 and 12 characters and equal the confirmation
    password = PasswordField('New Password', [Length(min=6, max=12),
                                              EqualTo('confirm', message='Passwords must match')])

    # confirmation
    confirm = PasswordField('Repeat Password', [Length(min=6, max=12)])


"""
Login Form
"""
class LoginForm(Form):
    username = StringField('Username', [DataRequired(message="username required")])
    password = PasswordField('Password', [Length(min=6, max=12)])