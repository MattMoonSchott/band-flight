from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
import urllib

#initialize sqlalchemy instance and Bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()

# define user including last search information
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, index=True)
    hash = db.Column(db.String(255))
    cplace = db.Column(db.String(100))
    cend = db.Column(db.String(10))
    cstart = db.Column(db.String(10))
    cpid = db.Column(db.Integer)
    cpage = db.Column(db.Integer)
    events = db.relationship('Events', backref='user', cascade="all, delete-orphan")

    def __init__(self , username , password):
        self.username = username
        self.hash = bcrypt.generate_password_hash(password)

    def is_active(self):
        """All users are active but this is a Flask-Login requirement"""
        return True

    def get_id(self):
        """Return the ID to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """No users are anonymous but this is a Flask-Login requirement."""
        return False

    def __repr__(self):
        return '<User %r>' % self.username

#define a saved event
class Events(db.Model):
    __tablename__ = 'saved'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'))
    artist = db.Column(db.String(255))
    venue = db.Column(db.String(100))
    addr = db.Column(db.String(255))
    date = db.Column(db.String(30))
    time = db.Column(db.String(40))
    link = db.Column(db.String(255))

    def init(self, uid, artist, venue, addr, date, time, link):
        self.uid = uid
        self.artist = artist
        self.venue = venue
        self.addr = addr
        self.date = date
        self.time = time
        self.link = link
        

# define a class for search links, not a database class but used in bandflight.py for get requests
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
