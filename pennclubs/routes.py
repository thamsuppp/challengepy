from flask import Flask, request, jsonify, make_response, abort
from pennclubs import app, db
from pennclubs.scraper import * # Web Scraping utility functions for Online Clubs with Penn.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np
from pennclubs.models import Club, User, Comment, Tag
from pennclubs.sentiment import analyze_comment_sentiment


### Routes
@app.route('/')
def main():
    return "Welcome to the Penn Club Review!"

@app.route('/api')
def api():
    return "Welcome to the Penn Club Review API!."



### API ROUTES

### CLUBS

#Gets all clubs
@app.route('/api/clubs', methods = ['GET'])
def clubs_api():
    all_clubs = Club.query.all()

    def get_club_sentiment_score(comments):
        comments = analyze_comment_sentiment([{'content': comment.content} for comment in comments])
        sentiment = round(np.mean([comment['sentiment_score'] for comment in comments]), 3)

        return sentiment


    clubs_dict = [{'name': club.name, 'description': club.description, 'favourites': len(club.users_favourited.all()),
    'sentiment': get_club_sentiment_score(club.comments)} for club in all_clubs]


    return jsonify(clubs_dict)

#Gets one club's information by ID
@app.route('/api/clubs/<id>', methods = ['GET'])
def get_club_by_id_api(id):
    club = Club.query.get(id)

    tags = [tag.tag_name for tag in club.tags]

    comments = [{'content': comment.content, 'author': comment.author.username, 'date_posted': comment.date_posted} for comment in club.comments]
    comments = analyze_comment_sentiment(comments)

    sentiment = round(np.mean([comment['sentiment_score'] for comment in comments]), 3)

    n_users_favourited = len(club.users_favourited.all())

    club_dict = {'name': club.name, 'description': club.description, 'favourites': n_users_favourited, 'tags': tags, 'sentiment': sentiment, 'comments': comments}

    return jsonify(club_dict)

#Creates a new club
@app.route('/api/clubs', methods = ['POST'])
def create_club():

    # If name or description parameter is missing, return an error
    if (not 'name' in request.json) or (not 'description' in request.json) or (not 'tags' in request.json):
        return make_response(jsonify({'error': 'Missing field(s)'}), 400)

    name = request.json['name']
    description = request.json['description']
    tags = request.json['tags']

    new_club = Club(name, description)

    #If club is already in db, then return an error
    if Club.query.filter_by(name = name).all() != []:
        return make_response(jsonify({'error': 'Club with this name already exists'}), 400)
        
    db.session.add(new_club)

    #Add tags
    for tag in tags:
        #If tag is not in db, then add tag to db, then create association between club and tag
        if Tag.query.filter_by(tag_name = tag).all() == []:
            tag_obj = Tag(tag_name = tag)
            db.session.add(tag_obj)  

            #Add the association between club and tag
            tag_obj.clubs.append(new_club)
        
        else:
            tag_obj = Tag.query.filter_by(tag_name = tag).all()[0]

            #Add the association between club and tag
            tag_obj.clubs.append(new_club)
    
    db.session.commit()
    
    output = {'name': new_club.name, 'description': new_club.description, 'tags': [tag.tag_name for tag in new_club.tags]}

    return jsonify(output), 201

#Updates an existing club's description
@app.route('/api/clubs', methods = ['PUT'])
def update_club():

    # If name or description parameter is missing, return an error
    if (not 'name' in request.json) or (not 'description' in request.json):
        return make_response(jsonify({'error': 'Missing field(s)'}), 400)

    name = request.json['name']
    description = request.json['description']

    #If no such club exists, return an error
    if Club.query.filter_by(name = name).all() == []:
        return make_response(jsonify({'error': 'Club not found'}), 400)
    
    #If club exists, save it as club object, and change its description
    club = Club.query.filter_by(name = name)[0]
    club.description = description
    db.session.commit()

    output = {'name': club.name, 'description': club.description}

    return jsonify(output), 202


### USERS

#Gets all users
@app.route('/api/user', methods = ['GET'])
def get_all_users():
    all_users = User.query.all()

    users_dict = [{'username': user.username, 'year': user.year} for user in all_users]

    return jsonify(users_dict)

#Gets information for a specific user
@app.route('/api/user/<username>', methods = ['GET'])
def get_user_info(username):

    #If no such user exists, return an error
    if User.query.filter_by(username = username).all() == []:
        return make_response(jsonify({'error': 'User with this username not found'}), 400)

    user = User.query.filter_by(username = username)[0]

    favourited_clubs = [club.name for club in user.favourited_clubs]

    user_dict = {'username': user.username, 'year': user.year, 'favourited_clubs': favourited_clubs}

    return jsonify(user_dict)

#Creates a user
@app.route('/api/user', methods = ['POST'])
def create_user():

    # If username or year parameter is missing, return an error
    if (not 'username' in request.json) or (not 'password' in request.json) or (not 'year' in request.json):
        return make_response(jsonify({'error': 'Missing field(s)'}), 400)

    username = request.json['username']
    year = request.json['year']

    new_user = User(username, year)
    #If username is already in db, then return an error
    if User.query.filter_by(username = username).all() != []:
        return make_response(jsonify({'error': 'User with this username already exists'}), 400)

    db.session.add(new_user)
    db.session.commit()

    output = {'username': new_user.username, 'year': new_user.year}

    return jsonify(output), 201

# User favourites a club
@app.route('/api/favourite', methods = ['POST'])
def user_favourite_club():

    # If username or club_favourited is missing, return an error
    if (not 'username' in request.json) or (not 'club_favourited' in request.json):
        return make_response(jsonify({'error': 'Missing field(s)'}), 400)

    username = request.json['username']
    club_favourited = request.json['club_favourited']

    #If no such user exists, return an error
    if User.query.filter_by(username = username).all() == []:
        return make_response(jsonify({'error': 'User with this username not found'}), 400)

    #Get user object
    user = User.query.filter_by(username = username)[0]

    #If no such club exists, return an error
    if Club.query.filter_by(name = club_favourited).all() == []:
        return make_response(jsonify({'error': 'Club not found'}), 400)

    #Get club object
    club = Club.query.filter_by(name = club_favourited)[0]

    #Add the association between user and club - favourited
    club.users_favourited.append(user)
    db.session.commit()

    output = {'username': user.username, 'club_favourited': club.name}

    return jsonify(output), 201

### COMMENTS

#Gets all users
@app.route('/api/comments', methods = ['GET'])
def get_all_comments():
    all_comments = Comment.query.all()

    comment_dict = [{'content': comment.content, 'date_posted': comment.date_posted, 'author': comment.author.username, 'club': comment.club.name} for comment in all_comments]

    comment_dict = analyze_comment_sentiment(comment_dict)

    return jsonify(comment_dict)

#Creates a comment
@app.route('/api/comments', methods = ['POST'])
def create_new_comment():
    
    # If username or club or content is missing, return an error
    if (not 'username' in request.json) or (not 'club' in request.json) or (not 'content' in request.json):
        return make_response(jsonify({'error': 'Missing field(s)'}), 400)

    username = request.json['username']
    club = request.json['club']
    content = request.json['content']

    #If no such username exists, return an error
    if User.query.filter_by(username = username).all() == []:
        return make_response(jsonify({'error': 'User not found'}), 400)
    author = User.query.filter_by(username = username)[0]

    #If no such club exists, return an error
    if Club.query.filter_by(name = club).all() == []:
        return make_response(jsonify({'error': 'Club not found'}), 400)
    club = Club.query.filter_by(name = club)[0]

    #Creates a comment
    new_comment = Comment(author = author, club = club, content = content)

    db.session.add(new_comment)
    db.session.commit()

    output = {'author': new_comment.author.username, 'club': new_comment.club.name, 'content': new_comment.content}


    return jsonify(output)


# ### USER LOGIN

# @app.route('/login', methods = ['POST'])
# def user_login():
    
#     # If name or password parameter is missing, return an error
#     if (not 'username' in request.json) or (not 'password' in request.json):
#         return make_response(jsonify({'error': 'Missing field(s)'}), 400)

#     username = request.json['username']
#     password = request.json['password']

#     user = User.query.filter_by(username = username).first()
#     if not user:
#         return make_response(jsonify({'error': 'User does not exist'}), 400)

#     #Check if user exists and password is correct
#     if bcrypt.check_password_hash(user.password, password):
#         #Log in
#         login_user(user)
#         return make_response(jsonify({'response': 'Successful login', 'user': user.username}), 202)
#     else:
#         return make_response(jsonify({'error': 'Login unsuccessful. Check password.'}), 400)


# @app.route('/logout', methods = ['POST'])
# def user_logout():
#     logout_user()
#     return make_response(jsonify({'response': 'Successful logout'}), 202)