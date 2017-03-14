import datetime as dt
from pandas_datareader import data as web
from flask_wtf import Form
from wtforms import StringField, FloatField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Optional


# define PortfolioForm to add new portfolios
class PortfolioForm(Form):
    name = StringField('Enter portfolio name:', validators=[DataRequired()])
    cash = FloatField('Enter cash position (USD $):',
                      validators=[NumberRange(min=0, max=None, message='Cannot have negative cash holdings'),
                                  DataRequired()])
    submit = SubmitField('Add Portfolio')


# define PortfolioForm to add new portfolios
class PortfolioEditForm(Form):
    newname = StringField('Enter new portfolio name:', validators=[Optional()])
    newcash = FloatField('Enter new cash position (USD $):',
                         validators=[NumberRange(min=0, max=None, message='Cannot have negative cash holdings'),
                                     Optional()])
    submit = SubmitField('Update Data')


# define HoldingForm to add new portfolios
class HoldingForm(Form):
    symbol = StringField('Enter ticker symbol:', validators=[DataRequired()])
    shares = IntegerField('Enter number of shares to be held:', validators=[NumberRange(min=0, max=None,
                                                                                        message='Not a valid position'),
                                                                            DataRequired()])
    purch_price = FloatField('Enter purchase price:',
                             validators=[NumberRange(min=0, max=None, message='Cannot enter negative prices'),
                                         DataRequired()])
    purch_date = DateField('Enter date purchased: (YYYY-DD-MM)', default=dt.date.today())
    submit = SubmitField('Add Holding')

    # ensure symbol entered is one that yahoo finance has data for
    def validate_symbol(form, field):
        try:
            test = web.DataReader(str(field.data).capitalize(), 'yahoo')
        except:
            raise ValidationError('No symbol under that name found')


# define HoldingForm to add new portfolios
class HoldingEditForm(Form):
    new_shares = IntegerField('Enter new number of shares to be held:', validators=[NumberRange(min=0, max=None,
                                                                                                message='Not a valid position'),
                                                                                    Optional()])
    new_purch_price = FloatField('Enter new purchase price:',
                                 validators=[NumberRange(min=0, max=None, message='Cannot enter negative prices'),
                                             Optional()])
    new_purch_date = DateField('Enter new date purchased', validators=[Optional()])
    submit = SubmitField('Edit Holding')

    # ensure symbol entered is one that yahoo finance has data for
    def validate_symbol(form, field):
        try:
            test = web.DataReader(str(field.data).capitalize(), 'yahoo')
        except:
            raise ValidationError('No symbol under that name found')


class OptimizationForm(Form):
    # form to enter time-span of returns used for portfolio optimization
    start_date = DateField('Enter start date for historical returns for optimization: (YYYY-DD-MM)',
                           validators=[DataRequired()])
    risk_free = FloatField('Enter risk-free interest rate:', default=0.01,
                           validators=[NumberRange(min=0, max=None, message='No negative interest rates')])
    submit = SubmitField('Generate Optimal Portfolio')


class SimulationForm(Form):
    # form to enter time-span of returns used for portfolio optimization
    start_date = DateField('Enter start date for historical returns for optimization: (YYYY-DD-MM)',
                           validators=[DataRequired()])
    risk_free = FloatField('Enter risk-free interest rate:', default=0.01,
                           validators=[NumberRange(min=0, max=None, message='No negative interest rates')])
    submit = SubmitField('Generate Optimal Portfolio')



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
