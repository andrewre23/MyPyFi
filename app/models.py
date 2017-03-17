from . import db
import datetime as dt

class Portfolio(db.Model):
    # model for base portfolio object
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), unique=True)    # name of portfolio
    cash = db.Column(db.Float)                      # cash holdings within portfolio
    market_value = db.Column(db.Float)              # market value of all holdings + cash
    total_profit = db.Column(db.Float)              # total profits of all holdings
    invested = db.Column(db.Float)                  # total amount invested into holdings - excludes cash holding
    profit_percent = db.Column(db.Float)            # percent return on current amount invested - excludes cash holding
    num_holdings = db.Column(db.Integer)            # total number of holdings in portfolio - excludes cash holding
    holdings = db.relationship('Holding', backref='portfolio', lazy='dynamic')

    def __init__(self, name, cash):
        self.name = name
        self.cash = cash
        self.market_value = cash
        self.num_holdings = 0
        self.update()

    def __repr__(self):
        return '<Name %r>' % self.name

    def update_last_price(self):
        # update last_price for all holdings in portfolio
        for holding in self.holdings:
            holding.update()

    def update_market_value(self):
        # update market_value and invested attributes of portfolio
        self.market_value = 0
        self.invested = 0
        self.market_value += self.cash
        for holding in self.holdings:
            self.market_value += (holding.shares * holding.last_price)
            self.invested += (holding.shares * holding.purch_price)
            holding.update_portfolio_percentage()
        db.session.add(self)

    def update_profit(self):
        # update profit attributes
        self.total_profit = self.market_value - self.invested - self.cash
        if self.invested:
            self.profit_percent = round(self.total_profit / self.invested, 4)
        else:
            self.profit_percent = 0
        db.session.add(self)

    def update_holding_count(self):
        # update number of holdings currently held
        self.num_holdings = Holding.query.filter_by(portfolio_id=self.id).count()
        db.session.add(self)

    def update(self):
        # update all holdings and overall portfolio
        for holding in self.holdings:
            holding.update()
        self.update_market_value()
        self.update_profit()
        self.update_holding_count()
        for holding in self.holdings:
            holding.update_portfolio_percentage()
            if holding.shares == 0:
                db.session.delete(holding)
        db.session.commit()

    def create_optimal_portfolio(self):
        old_port = Portfolio.query.filter_by(name=self.name+'_opt').first()
        if old_port:
            for holding in old_port.holdings:
                db.session.delete(holding)
            db.session.delete(old_port)
            db.session.commit()
        opt_port = Portfolio(name=self.name+'_opt',cash=self.cash)
        for holding in self.holdings:
            Holding(holding.symbol,holding.shares,holding.purch_date,holding.purch_price,opt_port.id)
        opt_port.update()
        db.session.add(opt_port)



class Holding(db.Model):
    # model for holdings associated with portfolios
    __tablename__ = 'holdings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(6))            # stock symbol
    shares = db.Column(db.Integer)              # number of shares held
    market_value = db.Column(db.Float)          # market value of holding
    purch_date = db.Column(db.Date)             # date holding was purchased
    purch_price = db.Column(db.Float)           # share price on purchase date
    last_price = db.Column(db.Float)            # most recent price from pandas_dataframe module
    total_profit = db.Column(db.Float)          # total profits of holding ($)
    profit_percent = db.Column(db.Float)        # percent profit based on initial amount invested
    portfolio_percent = db.Column(db.Float)     # percent holding makes up of overall portfolio
    last_updated = db.Column(db.String)         # date holding's last_price attribute was updated
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'))

    def __init__(self, symbol, shares, purch_date, purch_price, portfolio_id):
        self.symbol = symbol
        self.shares = shares
        self.purch_date = purch_date
        self.purch_price = purch_price
        self.portfolio_id = portfolio_id
        self.update()
        db.session.add(self)

    def __repr__(self):
        return '<Name %r>' % self.symbol

    def update_last_price(self):
        # update last_price from pandas_datareader module
        # only if last_updated doesn't match today
        import datetime as dt
        if not self.last_updated == str(dt.date.today()):
            from pandas_datareader import data as web
            self.last_price = round(web.DataReader(self.symbol, 'yahoo')['Adj Close'].iloc[-1], 2)
            self.last_updated = str(dt.date.today())
        db.session.add(self)

    def update_market_value(self):
        # update market_value attribute
        self.market_value = self.shares * self.last_price
        db.session.add(self)

    def update_profit(self):
        # update profit attributes
        self.total_profit = round(self.shares * (self.last_price - self.purch_price), 2)
        self.profit_percent = round(self.last_price / self.purch_price - 1, 4)
        db.session.add(self)

    def update_portfolio_percentage(self):
        # update percentage that this holding makes up of portfolio
        self.portfolio_percent = round(self.market_value / Portfolio.query.filter_by(id=self.portfolio_id).first().market_value,4)
        db.session.add(self)

    def update(self):
        self.update_last_price()
        self.update_market_value()
        self.update_portfolio_percentage()
        self.update_profit()
        db.session.commit()


class Ticker_Dataset(db.Model):
    # model definition for HDF5 ticker data storage
    __tablename__ = 'ticker_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(6))
    name = db.Column(db.String(32))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    freq = db.Column(db.String(4))
    vals = db.Column(db.Integer)
    location = db.Column(db.String(64))

    def __init__(self, symbol, name, start, end, freq, vals, location):
        self.symbol = symbol
        self.name = name
        self.start = start
        self.end = end
        self.freq = freq
        self.vals = vals
        self.location = location

    def __repr__(self):
        return '<Name %r>' % self.name
