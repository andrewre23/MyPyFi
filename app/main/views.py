from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from . import main
from .forms import NameForm, TickerForm

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
