
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pennclubs import app, db
from pennclubs.scraper import *

##### CLASSES

#Association Table to model club-tag many-to-many relationship
club_tags = db.Table('club_tags', 
    db.Column('club_id', db.Integer, db.ForeignKey('club.club_id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.tag_id')))

#Association Table to model user-favourited clubs many-to-many relationship
user_favourited_clubs = db.Table('user_favourited_clubs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
    db.Column('club_id', db.Integer, db.ForeignKey('club.club_id')))


#Club class
class Club(db.Model):
    
    club_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(500), unique = True, nullable = False)
    description = db.Column(db.String(2000), unique = True, nullable = False)

    #many-to-many - need a secondary relationship
    tags = db.relationship('Tag', secondary = club_tags, backref = db.backref('clubs', lazy = 'dynamic'))

    comments = db.relationship('Comment', backref='club', lazy=True)

    #Constructor
    def __init__(self, name, description, tags = []):
        self.name = name
        self.description = description
        self.tags = tags
    
    #To string function
    def __repr__(self):
        return 'Club({}, {})'.format(self.name, self.description)


#Tag class - many-to-many relationship with clubs
class Tag(db.Model):
    tag_id = db.Column(db.Integer, primary_key = True)
    tag_name = db.Column(db.String(100), unique = True, nullable = False)

    #To string function
    def __repr__(self):
        return 'Tag({})'.format(self.tag_name)


#User classs
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), unique = True, nullable = False)
    # Freshmen, sophomore, junior or senior year
    year = db.Column(db.String(10), unique = False, nullable = False)
    favourited_clubs = db.relationship('Club', secondary = user_favourited_clubs, backref = db.backref('users_favourited', lazy = 'dynamic'))

    comments = db.relationship('Comment', backref='author', lazy=True)

    #Constructor
    def __init__(self, username, year):
        self.username = username
        self.year = year

    #To string function
    def __repr__(self):
        return 'User({}, {})'.format(self.username, self.year)

#Comment class
class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, unique = False, nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'), nullable = False)

    #Constructor
    def __init__(self, author, club, content):
        self.author = author
        self.club = club
        self.content = content

