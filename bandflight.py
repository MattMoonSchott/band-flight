from flask import Flask, render_template, request, Response, redirect, flash, url_for, abort
from flask_bootstrap import Bootstrap
from flask.ext.login import LoginManager, login_required, login_user, current_user, logout_user
from models import *
from SKapi import SKEvent, gig_find, place_find
import Spotify
from Validators import *
import json, urllib
from datetime import datetime
from Forms import SKForm, Registration, LoginForm
from functools import wraps
from config import client_id, client_secret
import spotipy.util as util

# app instance
app = Flask(__name__)

# configure app
app.config.from_object('config')

# initialise the login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = "login"

# initialise mySQL database and  bcrypt with app instance
db.init_app(app)
bcrypt.init_app(app)

# bootstrap instance
bootstrap = Bootstrap(app)

token = util.oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
cache_token = token.get_access_token()
print(cache_token
    
class SearchLink:
    def __init__(self):
        self.area = ""
        self.place = ""
        self.start = ""
        self.end = ""

    def set_area(self, area):
        self.area = str(area)

    def set_place(self, pid):
        self.place = str(pid)

    def set_start(self, start):
        self.start = str(start)

    def set_end(self, end):
        self.end = str(end)

    def get_link(self):
        area = "?area=" + urllib.parse.quote(self.area)
        place = "&id=" + urllib.parse.quote(self.place)
        start = "&start=" + urllib.parse.quote(self.start)
        end = "&end=" + urllib.parse.quote(self.end)
        return '/results' + area + place + start + end

"""
@app.before_request
def before_request():
    return render_template('construct.html')
"""


@lm.user_loader
def load_user(user_id):
    """
    Provides flask-login with necessary
    way to obtain user from id.
    """
    return User.query.filter_by(id=user_id).first()


def require_s_or_l(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if current_user.name == 'Lauren' or current_user.name == 'Sunny':
            return view_function(*args, **kwargs)
        else:
            abort(401,{'key_error': 'Unauthorized Access. Not Lauren or Sunny'})
    return decorated_function


@app.route('/')
@login_required
def home():
    """
    Index page.
    """
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    """
    Registration Page
    """

    # initialise form
    form = Registration()
    if request.method == 'POST':

        # Use in-built validation from flask-wtforms
        if form.validate_on_submit():

            # check if user already exists
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                flash('Username already taken. Try a different one!', 'user')
                return render_template('register.html', form=form)
            user = User(request.form['username'].upper() , request.form['password'])
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login Page
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.upper()).first()
        if user:
            # use bcrypt to check the password
            if bcrypt.check_password_hash(user.hash, form.password.data):
                login_user(user, remember=True)
                return redirect(url_for('home'))
        flash("Either Password or Username Incorrect")
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    return redirect(url_for("home"))


@app.route("/saved")
@login_required
def saved():
    """
    Saved Event Page
    """
    uid = current_user.id
    results = Events.query.filter_by(uid=uid,).all()
    events = []
    for item in results:
        # find all the saved event
        event = SKEvent(item.artist, item.date, item.time, 'N/A', item.venue, item.link, item.addr)
        events.append(event)
    # get all tracks related to it
    Spotify.getTracks(events)
    return render_template('saved.html', saved=events)


@app.route('/terms')
def terms():
    """
    Terms and conditions
    """
    return render_template('Terms.html', current_user=current_user)


"""
AJAX servers
"""


@app.route('/_autocomplete',methods=['GET'])
def autocomplete():
    """
    AJAX for the places autocomplete.
    """
    term = request.args.get('term')
    # find the places
    search = place_find(term)
    return Response(json.dumps(search),  mimetype='application/json')


@app.route('/_addevent', methods=['GET'])
def addevent():
    """
    AJAX to add event to users saved event.
    """
    uid = current_user.id
    artist = request.args.get('Artist')
    venue = request.args.get('Venue')
    addr = request.args.get('Addr')
    date = request.args.get('Date')
    time = request.args.get('Time')
    link = request.args.get('Link')
    if Events.query.filter_by(uid=uid).filter_by(link=link).first():
        return json.dumps({'success': False}), 400, {'ContentType': 'application/json'}
    event = Events(uid=uid, artist=artist, venue=venue, addr=addr, date=date, time=time, link=link)
    db.session.add(event)
    db.session.commit()
    return "OK"


@app.route('/_remove', methods=['GET'])
def remove_event():
    """
    AJAX to remove the saved event from user's list of events
    """
    uid = current_user.id
    link = request.args.get('Link')
    events = Events.query.filter_by(uid=uid).filter_by(link=link).all()
    for event in events:
        db.session.delete(event)
    db.session.commit()
    return "OK"


@app.route('/results', methods=['POST', 'GET'])
@login_required
def newpage(page=1):
    """
    Renders search page
    """
    form = SKForm()
    user = current_user
    if request.method == 'POST':
        if form.validate_on_submit():
            link = SearchLink()
            link.set_place(form.place.data)
            link.set_area(form.locale.data)
            link.set_start(form.start.data)
            link.set_end(form.end.data)
            if not user.is_anonymous:
                user.cpid = form.place.data
                user.cplace = form.locale.data
                user.cstart = form.start.data
                user.cend = form.end.data
                db.session.commit()
            form.place.data = ''
            form.locale.data = ''
            form.start.data = ''
            form.end.data = ''
            return redirect(link.get_link() + "&page=1")
        else:
            events = []
            return render_template('results.html', form=form, events=events)

    elif request.method == 'GET':

        link = SearchLink()

        flag = False

        # find page number
        if 'page' in request.args:
            if not page_valid(request.values.get('page','')):
                abort(404)
            page = int(request.values.get('page', ''))
            user.cpage = int(request.values.get('page',''))
        elif user.cpage:
            page = user.cpage

        # find area
        if 'area' in request.args:
            area = request.values.get('area')
            link.set_area(area)
            user.cplace = area
        elif user.cplace:
            area = user.cplace
            link.set_area(area)
        else:
            flag = True

        # find the venue id
        if 'id' in request.args:
            if not id_valid(request.values.get('id')):
                abort(404)
            place = request.values.get('id')
            link.set_place(place)
            user.cpid = place
        elif user.cpid:
            place = user.cpid
            link.set_place(place)
        else:
            flag = True

        # get the start date for the search
        if 'start' in request.args:
            if not date_valid(request.values.get('start')):
                abort(404)
            start = request.values.get('start')
            link.set_start(start)
            user.cstart = start
        elif user.cstart:
            start = user.cstart
            link.set_start(start)
        else:
            flag = True

        # set the end date for the search
        if 'end' in request.args:
            if not date_valid(request.values.get('end')):
                abort(404)
            end = request.values.get('end')
            link.set_end(end)
            user.cend = end
        elif user.cend:
            end = user.cend
            link.set_end(end)
        else:
            flag = True

        # if there is a previous page, set the button
        if page > 1:
            prev = link.get_link() + "&page=" + str(page - 1)
        else:
            prev = ""

        if flag:
            return render_template('results.html', form=form)

        # use gig_find to get first page of results as list of events
        events = gig_find(page=page, location=place, start=start, end=end)

        # pop off the total number of events in search term
        total = events.pop()

        # If there are no results to show, flash a message as such
        if total == 0:
            flash('No results shown', 'results')
            return render_template('results.html', form=form)

        # Find out how many remaining results
        next_total = total - (page * 10)

        # if there are further results, set the next page button
        if next_total > 1:
            next_page = link.get_link() + "&page=" + str(page + 1)
        else:
            next_page = ""

        # find the tracks and add them to the event objects
        Spotify.getTracks(events)

        # commit the database session
        db.session.commit()

        start = datetime.strptime(start, "%Y-%m-%d").strftime("%m-%d-%Y")
        end = datetime.strptime(end, "%Y-%m-%d").strftime("%m-%d-%Y")
    return render_template('results.html', form=form, events=events, place = area, page=page, start=start, end=end, next=next_page, prev=prev)


@app.route('/finance/add', methods=['POST', 'GET'])
@login_required
@require_s_or_l
def finance_add():
    form = Registration()
    if request.method == 'POST':
        # Use in-built validation from flask-wtforms
        if form.validate_on_submit():
            # check if user already exists
            transaction = Transactions(request.form['username'].upper(), request.form['password'])
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.errorhandler(404)
def not_found(error):
    """
    Custom 404
    """
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
