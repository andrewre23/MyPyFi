from . import db


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


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
