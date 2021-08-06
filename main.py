from flask import Flask, render_template, request, redirect, url_for
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import random, secrets
import pymongo
import urllib.parse
import re

# Bucket Google Cloud Storage
from io import BytesIO
from google.cloud import storage

app = Flask(__name__)
firebase_request_adapter = requests.Request()
datastore_client = datastore.Client()
app.config['UPLOAD_FOLDER'] = 'static/img/reviews'


def setup_mongodb_session():
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
    db = setup_mongodb_session()
    data = db.users.find({"email": user_email})
    query = { "email": user_email }
    new_preferences = { "$set": { "themes": themes } }
    db.users.update_one(query, new_preferences)
    data = db.users.find({"email": user_email})

@app.route('/')
def root():
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
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        current_user = db.users.find({"user_token": claims['user_id']})

        collections = db.list_collection_names()
        data = db.themes.find()

        email = claims['email']
        all_themes = []

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
    if request.method == 'POST':
        theme_name = request.form['th_name']
        theme_description = request.form['th_description']
        theme_photo = request.files.get('photo', False)

        db = setup_mongodb_session()

        collections = db.list_collection_names()

        data = db.themes.find()

        file_id = secrets.token_hex(16)
        file_name = file_id + ".jpg"

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
    db = setup_mongodb_session()
    collections = db.list_collection_names()
    data = db.themes.find()

    return render_template("themes_all.html", themes_data=data)

@app.route('/themes/<string:theme_name>', methods=['GET'])
def view_theme(theme_name):
    """
    This function/service is used to get a single theme from the db and all associated reviews
    :return: string containing the theme
    """
    db = setup_mongodb_session()

    all_reviews = []

    data = db.themes.find({"theme_name": theme_name})
    data1 = db.reviews.find({"theme": theme_name})

    for i in data1:
        all_reviews.append(i)


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

@app.route('/reviews/all', methods=['GET', 'POST'])
def view_reviews():
    db = setup_mongodb_session()
    claims = is_user_authenticated()
    if claims is not False:
        if request.method == 'POST':
            tag_name = request.form["search"]
            all_reviews = []
            curr_user = db.users.find({"user_token": claims["user_id"]})
            sub_themes = curr_user[0]["themes"]
            for tag in tag_name.split(','):
                rgx = re.compile('.*'+tag+'.*', re.IGNORECASE)  # compile the regex

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
