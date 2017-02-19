from . import db


class Portfolio(db.Model):
    # model for base portfolio object
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), unique=True)
    cash = db.Column(db.Float)
    market_value = db.Column(db.Float)
    holdings = db.relationship('Holding', backref='portfolio', lazy='dynamic')

    def __init__(self, name, cash):
        self.name = name
        self.cash = cash
        self.market_value = cash

    def __repr__(self):
        return '<Name %r>' % self.name


class Holding(db.Model):
    # model for holdings associated with portfolios
    __tablename__ = 'holdings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(6))
    shares = db.Column(db.Integer)
    purch_date = db.Column(db.Date)
    purch_price = db.Column(db.Float)
    last_price = db.Column(db.Float)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'))

    def __init__(self, symbol, shares, purch_date, purch_price,last_price):
        self.symbol = symbol
        self.shares = shares
        self.purch_date = purch_date
        self.purch_price = purch_price
        self.last_price = last_price

    def __repr__(self):
        return '<Name %r>' % self.symbol


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
