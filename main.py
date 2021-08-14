from flask import Flask, render_template, request, redirect, url_for, request
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import random, secrets
import pymongo
import urllib.parse
import re
import json
import base64
import os


# Bucket Google Cloud Storage
from io import BytesIO
from google.cloud import storage

app = Flask(__name__)
firebase_request_adapter = requests.Request()
datastore_client = datastore.Client()
app.config['UPLOAD_FOLDER'] = 'static/img/reviews'


def setup_mongodb_session():
    #Connecting to our DB everytime we need to push/pull
    username = urllib.parse.quote_plus('admin')
    password = urllib.parse.quote_plus('asdasd@123')
    client = pymongo.MongoClient(
        "mongodb+srv://" + username + ":" + password + "@cluster0.le7xd.mongodb.net/?retryWrites=true&w=majority")
    db = client['apadgroup8']
    return db


def store_time(email, dt):
    entity = datastore.Entity(key=datastore_client.key('User', email, 'visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)

def fetch_times(email, limit):
    ancestor = datastore_client.key('User', email)
    query = datastore_client.query(kind='visit', ancestor=ancestor)
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times

def is_user_authenticated():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    token_expired = 0

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)
            token_expired = 1
    if not token_expired and id_token:
        return claims
    else:
        return False

def update_user_theme(user_email, themes):
    #We run the function everytime we need to update user preferences
    db = setup_mongodb_session()
    data = db.users.find({"email": user_email})
    query = { "email": user_email }
    new_preferences = { "$set": { "themes": themes } }
    db.users.update_one(query, new_preferences)
    data = db.users.find({"email": user_email})

@app.route('/')
def root():
    #Root gives us the login page after checking user authentication. We are using DB to get basic user information once user is logged in.
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        user_id = claims['user_id']
        user_email = claims['email']
        db = setup_mongodb_session()

        # find if user_id is present in users table
        if db.users.find({"user_token": user_id }).count() == 0:
            # Push user_id and user_email to db
            db.users.insert({
                "user_token":  user_id,
                "email": user_email,
                "themes": []
            })

        curr = db.users.find({"user_token": user_id})
        data = [cur for cur in curr]
        return render_template('index.html', user_data=claims, error_message=None, user=data[0])
    else:
        return render_template('index.html', error_message=True)

@app.route('/preferences/set', methods=['GET', 'POST'])
def preferences_set():
    #Update user preferences page
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        current_user = db.users.find({"user_token": claims['user_id']})

        collections = db.list_collection_names()
        data = db.themes.find()

        email = claims['email']
        all_themes = []

        #All themes appeneded to a list for printing
        for theme in data:
            all_themes.append(theme['theme_name'])

        details = {'email':email, 'themes':current_user[0]['themes']}

        if request.method == 'POST':
            new_preferences = request.form.getlist("th_preferences")
            update_user_theme(details['email'], new_preferences)
            return preferences_show()

        return render_template("preferences_set.html", details=details, all_themes=all_themes)
    else:
        return root ()

@app.route('/preferences', methods=['GET', 'POST'])
def preferences_show():
    #Show current user preferences on the page
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        current_user = db.users.find({"user_token": claims['user_id']})
        collections = db.list_collection_names()
        data = db.users.find()
        user_id = claims['user_id']

        #find if user_id is present in users table
        if db.users.find({"user_token": user_id }).count() == 0:
            # Push user_id and user_email to db
            return redirect(url_for("preferences_set"))
        else:
            details = db.users.find({"user_token": user_id })[0]
            return render_template("preferences.html", details=details)
    else:
        return root ()

@app.route('/themes/create', methods=['GET', 'POST'])
def create_theme():
    #For creation of new themes
    if request.method == 'POST':
        #Post method gets all information from html file and posts to MongoDB
        theme_name = request.form['th_name']
        theme_description = request.form['th_description']
        theme_photo = request.files.get('photo', False)

        db = setup_mongodb_session()

        collections = db.list_collection_names()

        data = db.themes.find()

        #We store the picture as a 16-character random string (https://docs.python.org/3/library/secrets.html) to keep the files separate
        file_id = secrets.token_hex(16)
        file_name = file_id + ".jpg"

        #We connect to our storage bucket on GCloud and store all the images there with the random string name
        client = storage.Client.from_service_account_json("apad-storage.json", project="APAD-Vaccination")

        # client = storage.Client()
        bucket = client.get_bucket('apad-group8-bucket')
        filename = "img/themes/" + file_name
        blob = bucket.blob(filename)
        blob.upload_from_file(theme_photo.stream, content_type=theme_photo.content_type)

        new_theme = {'_id': file_id,
                    'theme_name': theme_name,
                    'picture': file_name,
                    'description': theme_description}

        db.themes.insert_one(new_theme)
        return view_themes()

    return render_template("themes_create.html")

@app.route('/themes/all', methods=['GET'])
def view_themes():
    #The function to view all themes
    source_header = request.headers.get('source')
    db = setup_mongodb_session()
    collections = db.list_collection_names()
    data = db.themes.find()
    if source_header:
        #We store all themes data inside a list to be sent to our mobile app through a JSON dump
        themes_list = []
        theme_name = []
        theme_description = []
        theme_picture = []
        for theme in data:
            theme_name.append(theme["theme_name"])
            theme_description.append(theme["description"])
            theme_picture.append(theme["picture"])
        themes_list.append(theme_name)
        themes_list.append(theme_description)
        themes_list.append(theme_picture)
        return json.dumps(themes_list)
    else:
        return render_template("themes_all.html", themes_data=data)


@app.route('/themes/<string:theme_name>', methods=['GET'])
def view_theme(theme_name):
    """
    This function/service is used to get a single theme from the db and all associated reviews
    :return: string containing the theme
    """
    source_header = request.headers.get('source')
    db = setup_mongodb_session()
    all_reviews = []

    data = db.themes.find({"theme_name": theme_name})
    data1 = db.reviews.find({"theme": theme_name})

    for i in data1:
        all_reviews.append(i)

    if source_header:
        return json.dumps(all_reviews,default=str)
    else:
        return render_template("theme.html", details=data[0], details1=all_reviews)

@app.route('/reviews/create', methods=['GET', 'POST'])
def create_review():
    """
    This function/service is used to post review of a theme item by a user
    :param user_id: unique user id who is posting the review
    :return: None
    """
    db = setup_mongodb_session()
    collections = db.list_collection_names()
    data = db.themes.find()
    claims = is_user_authenticated()
    if claims is not False:
        current_user = db.users.find({"user_token": claims['user_id']})
        themes = []

        # db.reviews.drop()

        for theme in data:
            themes.append(theme['theme_name'])

        if request.method == 'POST':
            db = setup_mongodb_session()
            review_theme = request.form["th_preferences"]
            review_photo = request.files['th_photo']

            file_id = secrets.token_hex(16)
            file_name = file_id + ".jpg"

            client = storage.Client.from_service_account_json("apad-storage.json", project="APAD-Vaccination")

            # client = storage.Client()
            bucket = client.get_bucket('apad-group8-bucket')
            filename = "img/reviews/" + file_name
            blob = bucket.blob(filename)
            blob.upload_from_file(review_photo.stream, content_type=review_photo.content_type)

            review_user_id = claims['user_id']

            # blob.make_public()
            # url = blob.public_url
            review_title = request.form['th_title']
            review_description = request.form['th_review']
            review_rating = request.form['star']
            review_tags = request.form['th_tags']

            #hardcoding min and max lat, lng for Austin area
            min_lat = 30.0
            max_lat = 31.0
            min_lng = -97.0
            max_lng = -98.0

            #selecting lat and lng randomly from the min/max defined above
            lat = random.uniform(min_lat, max_lat)
            lng = random.uniform(min_lng, max_lng)
            g = []
            g.append (lat)
            g.append (lng)
            
            db.reviews.insert({
                "user_token": review_user_id,
                "title": review_title,
                "theme": review_theme,
                "rating": review_rating,
                "picture": file_name,
                "description": review_description,
                "tags": review_tags,
                "geo_location": g
            })

            return redirect(url_for("view_reviews"))
        else:
            return render_template('review_create.html', themes=themes)
    else:
        return root()

@app.route('/reviews/create/android', methods=['GET', 'POST'])
def create_review_from_android():
    """
    This function/service is used to post review of a theme item by a user
    :param user_id: unique user id who is posting the review
    :return: None
    """
    db = setup_mongodb_session()
    collections = db.list_collection_names()
    data = db.themes.find()

    themes = []

    for theme in data:
        themes.append(theme['theme_name'])

    if request.method == 'POST':
        db = setup_mongodb_session()
        review_theme = request.form["th_preferences"]
        review_photo = request.form["th_photo"]

        ## Convert photo encoded back to streamed Image
        review_photo = base64.b64decode((review_photo))
        file_id = secrets.token_hex(16)+'.jpg'
        file_name = '/tmp/'+file_id
        decodeit = open(file_name, 'wb')
        decodeit.write(review_photo)
        decodeit.close

        client = storage.Client.from_service_account_json("apad-storage.json", project="APAD-Vaccination")

        # client = storage.Client()
        bucket = client.get_bucket('apad-group8-bucket')
        filename = "img/reviews/" + file_id
        blob = bucket.blob(filename)
        with open(file_name, 'rb') as f:
            blob.upload_from_file(f)
        os.remove(file_name)

        review_user_id = request.form["user_id"]

        # blob.make_public()
        # url = blob.public_url
        review_title = request.form['th_title']
        review_description = request.form['th_review']
        review_rating = request.form['star']
        review_tags = request.form['th_tags']
        
        #Getting the current lat and lng coordinates from the mobile app
        g = []
        lat = float(request.form['th_lat'])
        lng = float(request.form['th_lng'])
        g.append(lat)
        g.append(lng)

        db.reviews.insert({
            "user_token": review_user_id,
            "title": review_title,
            "theme": review_theme,
            "rating": review_rating,
            "description": review_description,
            "picture": file_id,
            "tags": review_tags,
            "geo_location": g
        })
        return "Posted in MongoDB !!!"
    else:
        return "Not a post"
                        
@app.route('/reviews/all', methods=['GET', 'POST'])
def view_reviews():
    #The main feed where we show all posts under the user's selected themes
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        if request.method == 'POST':
            #POST method takes us to the search page where we can see reviews filtered by search tags.
            tag_name = request.form["search"]
            all_reviews = []
            curr_user = db.users.find({"user_token": claims["user_id"]})
            sub_themes = curr_user[0]["themes"]
            for tag in tag_name.split(','):
                rgx = re.compile('.*'+tag+'.*', re.IGNORECASE)  # compile the regex

            #We make a search request by using the input from user and searching it within post tags
            search_request = {
                '$and': [
                    {'tags': {'$regex': rgx}},
                    {'theme': {'$in' : sub_themes}}
                ]
            }
            for review in db.reviews.find(search_request):
                if review not in all_reviews:
                    all_reviews.append(review)
            return render_template("feed_reviews_tags.html", reviews=all_reviews)
        else:
            #Main feed
            current_user = db.users.find({"user_token": claims['user_id']})
            all_reviews = []
            temp = True

            if current_user[0]["themes"] == []:
                temp = False

            for theme in current_user[0]["themes"]:
                for review in db.reviews.find({"theme": theme}):
                    all_reviews.append(review)

            return render_template("feed_reviews.html", themes=current_user[0]["themes"], reviews=all_reviews, temp=temp)
    else:
        return root()

@app.route('/geoview', methods=['GET'])
def get_geoview_page():
    #Checks current user's subscribed themes, fetches all reviews from those themes and generates the maps page using Google Maps API
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        current_user = db.users.find({"user_token": claims['user_id']})
        all_reviews = []
        temp = True

        if current_user[0]["themes"] == []:
            temp = False

        for theme in current_user[0]["themes"]:
            for review in db.reviews.find({"theme": theme}):
                all_reviews.append(review)

        return render_template("geo_view.html", reviews=all_reviews, temp=temp)
    else:
        return root()


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
