# Server Challenge <a id="sec-1" name="sec-1"></a>

by Isaac Tham


## Description<a id="sec-1-1" name="sec-1-1"></a>

This is a Flask app that scrapes data from Penn Clubs website and stores them in a database, allowing users to favourite clubs and post comments about them. There is also a built-in sentiment analysis function that uses VaderSentiment package to calculate a sentiment score for each comment, allowing the average sentiment of the club to be visualized.

A SQLite database was used to store and query the information. A login/logout system was attempted but I ran out of time to successfully implement it.

**Clubs**
1. /clubs (POST) - creates a club (Required parameters: name, description, tags)
2. /clubs (GET) - gets information of all clubs (Parameters: name, description, tags, sentiment)
3. /clubs/<id> (GET) - gets information of the club with the specified club_id (Parameters: name, description, tags, comments, sentiment)
4. /clubs (PUT) - update data for a club (Required parameters: name, description, tags)

**Users**
1. /user (GET) - gets all users (Parameters: name, year)
2. /user/<username> (GET) - gets information of the user with the specified username (Parameters: name, year, favourited clubs)
3. /user/ (POST) - create a user (Required parameters: username, password)
4. /favourite (POST) - favourite a club (Required parameters: username, club_favourited)

**Comments**
1. /comments (GET) - get all comments (Parameters: author, date_posted, club, content)
2. /comments (POST) - creates a comment (Required parameters: username, club, content)


## Project Structure<a id="sec-1-2" name="sec-1-2"></a>


    +-- run.py                          # Runs the application
    +-- README.md                       # README file
    +-- pennclubs                       # Package containing main files
    ¦   +-- __init__.py                 # Instantiates app and database
    ¦   +-- routes.py                   # Routes for the app
    ¦   +-- models.py                   # Stores models for User, Club, Tag, Comment
    ¦   +-- scraper.py                  # Functions to scrape the Penn Clubs website
    ¦   +-- sentiment.py                # Function to perform sentiment analysis
    ¦   +-- pennclubs.db                # SQLite database to store information
    


