# MyPyFi
#
# Financial hub for financial analysis with Python
#
# Local data management, portfolio management,
# and quick visualizations

import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# define NameForm class from inherited Form class
class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# base directory location
basedir = os.path.abspath(os.path.dirname(__file__))

# initialize app dictionary
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# create proper instances of ext's
manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


#
# app routes
#

# route for main index homepage
@app.route('/', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))


# error handler for 404 error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# error handler for 500 error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# route for user-specific pages
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


#
# functions and initialization
#

# initialize variables for shell context
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))


#
# class definitions
#

# define NameForm class from inherited Form class
class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# define Role model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role {!r}>'.format(self.name)


# define User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {!r}>'.format(self.username)


# run main application
if __name__ == '__main__':
    manager.run()
