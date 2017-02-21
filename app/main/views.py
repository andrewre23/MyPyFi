from flask import render_template, session, redirect, url_for, flash, abort
from .. import db
from ..models import Portfolio, Holding
from . import main
from .forms import TickerForm, PortfolioForm, PortfolioEditForm, HoldingForm, HoldingEditForm

import datetime as dt


# route for main index homepage
@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


#######################
# portfolio routes
#######################


# route for portfolio homepage
@main.route('/portfolio_main', methods=['GET', 'POST'])
def portfolio_main():
    if not session.get('last_update', None) == str(dt.date.today()):
        portfolio_data = Portfolio.query.order_by(Portfolio.name).all()
        for port in portfolio_data: port.update()
        session['last_update'] = str(dt.date.today())
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
    holding_data = portfolio.holdings.order_by(Holding.portfolio_percent.desc()).all()
    return render_template('portfolio.html', name=name, holding_data=holding_data)


# route for adding new portfolios
@main.route('/portfolio/<name>/edit', methods=['GET', 'POST'])
def portfolio_edit(name):
    form = PortfolioEditForm()
    if form.validate_on_submit():
        portfolio = Portfolio.query.filter_by(name=session['portfolio']).first()
        if portfolio is not None:
            if form.newname.data:
                portfolio.name = form.newname.data
            if form.newcash.data or form.newcash.data == 0:
                portfolio.cash = form.newcash.data
            db.session.add(portfolio)
            portfolio.update()
            session['portfolio'] = portfolio.name
            flash('Portfolio data successfully updated!')
            return redirect(url_for('.portfolio_main'))
        else:
            flash('Error updating portfolio data')
    return render_template('portfolio_edit.html', name=name, form=form)


# route for confirming deletion of portfolios
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
    holdinglist = Holding.query.filter_by(portfolio_id=portfolio.id).all()
    db.session.delete(portfolio)
    for holding in holdinglist:
        db.session.delete(holding)
    db.session.commit()
    flash(session['portfolio'] + ' successfully deleted!')
    session['portfolio'] = None
    return redirect(url_for('.portfolio_main'))


#######################
# holding routes
#######################


# route for adding new holdings
@main.route('/portfolio/<name>/holding_add', methods=['GET', 'POST'])
def holding_add(name):
    form = HoldingForm()
    if form.validate_on_submit():
        Holding(symbol=str(form.symbol.data).upper(), shares=form.shares.data,
                purch_date=form.purch_date.data,
                purch_price=round(form.purch_price.data, 2),
                portfolio_id=Portfolio.query.filter_by(name=session['portfolio']).first().id)
        flash('Holding successfully added!')
        Portfolio.query.filter_by(name=session['portfolio']).first().update()
        return redirect(url_for('.holding_add', name=name))
    return render_template('holding_add.html', form=form, name=name)


# route for editing holdings
@main.route('/portfolio/<name>/<symbol>/holding_edit/<holding_id>', methods=['GET', 'POST'])
def holding_edit(name, symbol, holding_id):
    form = HoldingEditForm()
    if form.validate_on_submit():
        holding = Holding.query.filter_by(id=holding_id).first()
        if form.new_shares.data or form.new_shares.data == 0:
            holding.shares = form.new_shares.data
        if form.new_purch_price.data or form.new_purch_price.data == 0:
            holding.purch_price = round(form.new_purch_price.data, 2)
        if form.new_purch_date.data:
            holding.purch_date = form.new_purch_date.data
        db.session.add(holding)
        db.session.commit()
        Portfolio.query.filter_by(id=holding.portfolio_id).first().update()
        flash('Holding successfully edited!')
        return redirect(url_for('.portfolio', name=session['portfolio']))
    return render_template('holding_edit.html', form=form, symbol=symbol)


# route for confirming deletion of holdings
@main.route('/portfolio/<name>/<symbol>/delete/<holding_id>')
def holding_delete_ask(name, symbol, holding_id):
    holding = Holding.query.filter_by(id=holding_id).first()
    if holding is None:
        abort(404)
    return render_template('holding_delete.html', name=session['portfolio'], symbol=holding.symbol,
                           holding_id=holding.id)


# route for deleting holdings
@main.route('/holding/<holding_id>/delete')
def holding_delete(holding_id):
    holding = Holding.query.filter_by(id=holding_id).first()
    portfolio_id = holding.portfolio_id
    db.session.delete(holding)
    db.session.commit()
    Portfolio.query.filter_by(id=portfolio_id).first().update()
    flash(str(holding.symbol).upper() + ' successfully deleted!')
    return redirect(url_for('.portfolio', name=session['portfolio']))


#######################
# analytical routes
#######################

# route for portfolio optimization path





# #######################
# # ticker routes
# #######################

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
