from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, Form
from wtforms.validators import DataRequired, Length

class GameSearchForm(Form):
    choices = [('QueryName', 'Title'), ('AboutText', 'Description')]
    select = SelectField('Search for:', choices=choices)
    search = StringField('')
