from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from ..models import Portfolio, Holding, User
from . import main
from .forms import NameForm, TickerForm, PortfolioForm

import datetime as dt


# route for main index homepage
@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           name=session.get('name'),
                           known=session.get('known', False))


# route for portfolio homepage
@main.route('/portfolio', methods=['GET', 'POST'])
def portfolio_main():
    portfolio_data = Portfolio.query.all()
    return render_template('portfolio_main.html', portfolio_data=portfolio_data)


# route for adding new portfolios
@main.route('/portfolio_add', methods=['GET', 'POST'])
def portfolio_add():
    form = PortfolioForm()
    if form.validate_on_submit():
        portfolio = Portfolio.query.filter_by(name=form.name.data).first()
        if portfolio is None:
            portfolio = Portfolio(name=form.name.data, cash=round(form.cash.data, 2))
            db.session.add(portfolio)
            session['portfolio'] = portfolio.name
            flash('Portfolio successfully added!')
            return redirect(url_for('.portfolio_main'))
        else:
            flash('That portfolio name is already taken')
    return render_template('portfolio_add.html', form=form)


# route for ticker data management page
@main.route('/ticker_data', methods=['GET', 'POST'])
def ticker_data():
    test1 = {'symbol': 'NVDA', 'name': 'Nvidia', 'start': dt.datetime(2013, 1, 1).date(),
             'end': dt.datetime(2016, 12, 31).date(), 'freq': 'M', 'vals': 100,
             'location': 'C:/Users/Admin/PythonData/MyPyFi/'}
    test2 = {'symbol': 'AAPL', 'name': 'Apple', 'start': dt.datetime(2013, 1, 1).date(),
             'end': dt.datetime(2016, 12, 31).date(), 'freq': 'M', 'vals': 100,
             'location': 'C:/Users/Admin/PythonData/MyPyFi/'}
    dataset = [test1, test2]
    return render_template('ticker_data.html', dataset=dataset)


# route for page to add ticker data
@main.route('/ticker_add', methods=['GET', 'POST'])
def ticker_add():
    form = TickerForm()
    if form.validate_on_submit():
        pass

    return render_template('ticker_add.html', form=form)


# route for user-specific pages
@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)
