from pandas_datareader import data as web
from .. import db
from ..models import Portfolio, Holding

def last_price(symbol):
    data = web.DataReader(symbol,'yahoo')['Adj Close']
    return data.iloc[-1]

def update_last_price(holding_id):
    holding = Holding.query.filter_by(id=holding_id).first()
    holding.last_price = round(last_price(holding.symbol),2)
    db.session.add(holding)
    db.session.commit()

def update_mkt_val(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id).first()
    portfolio.market_value = portfolio.cash
    for hold in Holding.query.filter_by(portfolio_id=portfolio.id).all():
        portfolio.market_value += hold.shares * hold.last_price
    db.session.add(portfolio)
    db.session.commit()

def update_all_market_vals():
    for port in Portfolio.query.all() or []:
        for hold in Holding.query.filter_by(portfolio_id=port.id).all() or []:
            update_last_price(hold.id)
        update_mkt_val(port.id)

def add_hold_to_port(holding, port_name):
    holding.portfolio_id = Portfolio.query.filter_by(name=port_name).first().id
    db.session.add(holding)
    db.session.commit()
    update_mkt_val(holding.portfolio_id)



def edit_portfolio():
    pass