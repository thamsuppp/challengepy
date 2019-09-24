#Main app with the routes
from flask import Flask, request, jsonify, make_response, abort
from pennclubs.scraper import * # Web Scraping utility functions for Online Clubs with Penn.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '324uhfij23j4hkjsy3274hjk'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pennclubs.db'
db = SQLAlchemy(app)

from pennclubs import routes
from pennclubs.models import Club, Tag, User, Comment


#### SCRAPING FROM WEBSITE

#Wrapper function that scrapes website and returns soup of clubs
def get_clubs_soup():
    html = get_clubs_html()
    soup = soupify(html)
    clubs_soup = get_clubs(soup)
    return clubs_soup

#Get clubs_soup
clubs_soup = get_clubs_soup()


##### CREATING CLUB OBJECTS

#Function to create Club object
def create_club_object(club_soup):
    name = get_club_name(club_soup)
    description = get_club_description(club_soup)
    tags = get_club_tags(club_soup)

    #Add club to db
    club_obj = Club(name = name, description = description)
    #If club is not in db, then add club to db
    if Club.query.filter_by(name = name).all() == []:
        db.session.add(club_obj)
        db.session.commit()

        
        for tag in tags:
            #If tag is not in db, then add tag to db, then create association between club and tag
            if Tag.query.filter_by(tag_name = tag).all() == []:
                tag_obj = Tag(tag_name = tag)
                db.session.add(tag_obj)  

                #Add the association between club and tag
                tag_obj.clubs.append(club_obj)
            
            else:
                tag_obj = Tag.query.filter_by(tag_name = tag).all()[0]

                #Add the association between club and tag
                tag_obj.clubs.append(club_obj)
        
    db.session.commit()
    print('Club added: {}'.format(club_obj))



#Create Club objects
for club_soup in clubs_soup:
    create_club_object(club_soup)
