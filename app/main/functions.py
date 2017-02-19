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