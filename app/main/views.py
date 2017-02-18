from flask import render_template, session, redirect, url_for, flash, abort
from .. import db
from ..models import Portfolio, Holding
from . import main
from .forms import TickerForm, PortfolioForm, HoldingForm

import datetime as dt


# route for main index homepage
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#############
# portfolio routes
#############


# route for portfolio homepage
@main.route('/portfolio_main', methods=['GET', 'POST'])
def portfolio_main():
    portfolio_data = Portfolio.query.order_by(Portfolio.name).all()
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


# route for portfolio-specific pages
@main.route('/portfolio/<name>')
def portfolio(name):
    portfolio = Portfolio.query.filter_by(name=name).first()
    if portfolio is None:
        abort(404)
    else:
        session['portfolio'] = str(portfolio.name)
    holding_data = portfolio.holdings.order_by(Holding.symbol).all()
    return render_template('portfolio.html', name=name, holding_data=holding_data)

# route for deleting portfolios
@main.route('/portfolio/<name>/delete')
def portfolio_delete_ask(name):
    portfolio = Portfolio.query.filter_by(name=name).first()
    if portfolio is None:
        abort(404)
    else:
        session['portfolio'] = str(portfolio.name)
    return render_template('portfolio_delete.html', name=name)

# route for deleting portfolios
@main.route('/portfolio/delete')
def portfolio_delete():
    portfolio = Portfolio.query.filter_by(name=session['portfolio']).first()
    db.session.delete(portfolio)
    db.session.commit()
    flash('Portfolio deleted!')
    flash(session['portfolio'])
    session['portfolio'] = None
    return redirect(url_for('.portfolio_main'))

# route for adding new holdings
@main.route('/holding_add', methods=['GET', 'POST'])
def holding_add():
    form = HoldingForm()
    if form.validate_on_submit():
        holding = Holding(symbol=str(form.symbol.data).capitalize(), shares=form.shares.data, purch_date=form.purch_date.data,
                          purch_price=round(form.purch_price.data, 2))
        portfolio_name=session['portfolio']
        holding.portfolio_id=Portfolio.query.filter_by(name=portfolio_name).first().id
        db.session.add(holding)
        flash('Holding successfully added!')
        return redirect(url_for('.holding_add'))
    return render_template('holding_add.html', form=form)

#############
# ticker routes
#############

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
