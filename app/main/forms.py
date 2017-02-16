from flask_wtf import Form
from wtforms import StringField, FloatField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange


# define PortfolioForm to add new portfolios
class PortfolioForm(Form):
    name = StringField('Enter portfolio name:',validators=[DataRequired()])
    cash = FloatField('Enter cash position (USD $):',validators=[DataRequired(),NumberRange(min=0,max=None,message='Cannot have negative cash holdings')])
    submit = SubmitField('Submit')

# define NameForm class from inherited Form class
class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# define TickerForm class for adding new HDF5 ticker data
class TickerForm(Form):
    symbol = StringField('Stock symbol:', validators=[DataRequired()])
    name = StringField('Company name:')
    start = DateField('Enter START of desired daterange (Year, Month, Day)', validators=[DataRequired()])
    end = DateField('Enter END of desired daterange (Year, Month, Day)', validators=[DataRequired()])
    freq = SelectField('Enter frequency of data desired (Pandas notation)', choices=[
        ('B', 'Business Day'), ('D', 'Calendar Day'), ('W', 'Weekly'), ('M', 'Month End'),
        ('SM', 'Semi-Month to End'), ('BM', 'Business-Month to End'), ('MS', 'Month Start'),
        ('SMS', 'Semi-Month to Start'), ('BMS', 'Business Month Start'), ('Q', 'Quarter End'),
        ('BQ', 'Business Quarter End'), ('QS', 'Quarter Start'), ('BQS', 'Business Quarter Start'),
        ('A', 'Year End'), ('BA', 'Business Year End'), ('AS', 'Year Start'), ('BAS', 'Business Year Start'),
        ('BH', 'Business Year Start'), ('H', 'Hourly'), ('T', 'Minutely'), ('S', 'Secondly'),
        ('L', 'Milliseconds'), ('U', 'Microseconds'), ('N', 'Nanoseconds')
    ])
    submit = SubmitField('Add Ticker Data')
