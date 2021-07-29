import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import random, secrets
import pymongo
import urllib.parse
from werkzeug.utils import secure_filename
import os
from PIL import Image
import base64

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


def update_user_theme(user_email, themes):
    db = setup_mongodb_session()
    #print(user_email)
    #print("asdasd123@gmail.com")
    #data = db.users.find()

    data = db.users.find({"email": user_email})
    #print(data[0]['themes'])

    #themes = ['blabla1', 'blabla2']

    query = { "email": user_email }
    new_preferences = { "$set": { "themes": themes } }

    db.users.update_one(query, new_preferences)

    data = db.users.find({"email": user_email})
    #print(data[0]['themes'])
    #{'_id': ObjectId('6102d061f9a93c37284f6f5e'), 'user_token': 'abc123', 'email': 'asdasd123@gmail.com', 'themes': ['vaccine', 'pharmacy']}


@app.route('/')
def root():
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
        print(data[0])
        return render_template('index.html', user_data=claims, error_message=error_message, user=data[0])
    else:
        return render_template('index.html')

@app.route('/preferences/set', methods=['GET', 'POST'])
def preferences_set():
    db = setup_mongodb_session()
    collections = db.list_collection_names()
    data = db.themes.find()

    user_id = "abc123"
    all_themes = []

    for theme in data:
        all_themes.append(theme['theme_name'])

    details = {'email':"asdasd123@gmail.com", 'themes':["asdasd", "dsadsa"]}

    if request.method == 'POST':
        new_preferences = request.form.getlist("th_preferences")
        update_user_theme(details['email'], new_preferences)

    return render_template("preferences_set.html", details=details, all_themes=all_themes)

@app.route('/preferences', methods=['GET', 'POST'])
def preferences_show():
    db = setup_mongodb_session()

    collections = db.list_collection_names()
    data = db.users.find()

    user_id = "abc123"

    #find if user_id is present in users table
    if db.users.find({"user_token": user_id }).count() == 0:
        # Push user_id and user_email to db
        return redirect(url_for("preferences_set"))
    else:
        details = db.users.find({"user_token": user_id })[0]
        return render_template("preferences.html", details=details)

@app.route('/themes/create', methods=['GET', 'POST'])
def create_theme():
    if request.method == 'POST':
        theme_name = request.form['th_name']
        theme_description = request.form['th_description']
        theme_photo = request.files['photo']

        #'_id': ObjectId('6102cf1af9a93c37284f6f5c'), 'theme_name': 'vaccine', 'picture': b'NA', 'description': 'take it and enjoy'}
        db = setup_mongodb_session()

        collections = db.list_collection_names()
        data = db.themes.find()

        file_id = secrets.token_hex(16)
        file_name = file_id + ".jpg"

        if theme_photo.filename != '':
            theme_photo.save("static/img/themes/" + file_name)

        new_theme = {'_id': file_id,
                    'theme_name': theme_name,
                    'picture': file_name,
                    'description': theme_description}

        db.themes.insert_one(new_theme)

    return render_template("themes_create.html")

@app.route('/themes/all', methods=['GET'])
def view_themes():
    if request.method == 'GET':
        #'_id': ObjectId('6102cf1af9a93c37284f6f5c'), 'theme_name': 'vaccine', 'picture': b'NA', 'description': 'take it and enjoy'}
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

    print(theme_name)

    data = db.themes.find({"theme_name": theme_name})
    data1 = db.reviews.find({"theme": theme_name})

    for i in data1:
        all_reviews.append(i)


    return render_template("theme.html", details=data[0], details1=all_reviews)


@app.route('/review', methods=['GET'])
def post_review():
    """
    This function/service is used to post review of a theme item by a user
    :param user_id: unique user id who is posting the review
    :return: None
    """
    db = setup_mongodb_session()
    themes = db.themes.find()
    data = [theme for theme in themes]
    print(data)
    return render_template("create_review.html", th_themes=data)


@app.route('/post/review', methods=['GET', 'POST'])
def post_review_to_db():
    """
    This function/service is used to post review of a theme item by a user
    :param user_id: unique user id who is posting the review
    :return: None
    """

    if request.method == 'POST':
        db = setup_mongodb_session()
        id_token = request.cookies.get("token")
        error_message = None
        claims = None
        times = None

        if id_token:
            try:
                claims = google.oauth2.id_token.verify_firebase_token(
                    id_token, firebase_request_adapter)

            except ValueError as exc:
                error_message = str(exc)

        review_user_id = id_token
        review_theme = request.form['th_themes']
        review_photo = request.files['th_photo']
        filename = secrets.token_hex(16)
        local_path = os.path.join('/tmp', filename)
        review_photo.save(local_path)
        with open(local_path, "rb") as imageFile:
            image_string = base64.b64encode(imageFile.read())

        review_title = request.form['th_title']
        review_description = request.form['th_review']
        review_rating = request.form['star']
        review_tags = request.form['th_tags']
        db.reviews.insert({
            "user_token": review_user_id,
            "title": review_title,
            "theme": review_theme,
            "rating": review_rating,
            "picture": image_string,
            "description": review_description,
            "tags": list(review_tags)
        })
        return render_template('feed.html')
    else:
        return render_template('create_review.html')

@app.route('/reports', methods=['GET'])
def get_reports_from_tags():
    """
    This function/service is used to get all reports with matching tags
    Here, assumption is that tags will be either a single tag or a string of comma separated multiple tags
    e.g. valid tags i) 'austin' ii) 'cvs,austin,pfizer'
    :return: string containing all themes
    """
    db = setup_session()
    cur = db.cursor()
    tags_filter = request.args.get('tags').split(',')
    query = "SELECT * from REVIEWS WHERE "
    for tag_item in tags_filter[:-1]:
        query = query + "TAGS LIKE \'%" + tag_item + "%\' OR "
    else:
        query = query + "TAGS LIKE \'%" + tags_filter[-1] + "%\'"
    try:
        cur.execute(query)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
    data = cur.fetchall()
    return str(data)

@app.route('/user/page/set', methods=['GET', 'POST'])
def set_preferences():
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
    if request.method == 'POST':
        preferences = request.form.getlist("th_preferences")
        user_id = claims['user_id']
        user_email = claims['email']
        file_path = "db/reviews.db"
        local_path = "/tmp/reviews.db"
        storage = setup_firebase()
        db = setup_session(storage)
        sql = "UPDATE USER SET THEMES=\"" + ",".join(preferences) + "\" WHERE USER_ID=" + user_id
        task = (",".join(preferences),user_id)

        print(user_id)
        print(task)
        print(",".join(preferences))
        print(sql)

        try:
            cur = db.cursor()
            cur.execute(sql, task)
            db.commit()
            #push_db(storage, file_path, local_path)
            push_db(storage, "db/reviews.db", "/tmp/reviews.db")
            #return view_themes()
        except:
            return 'There was an issue upating your task'
            ### BUG : Fix the insert UPDATE section above

    if not token_expired and id_token:
        user_id = claims['user_id']
        user_email = claims['email']

        file_path = "db/reviews.db"
        local_path = "/tmp/reviews.db"
        storage = setup_firebase()
        db = setup_session(storage)
        cur = db.cursor()
        query = "SELECT * from USER WHERE USER_ID=\"" + claims['user_id'] + "\""

        try:
            cur.execute(query)
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
        data = cur.fetchall()

        storage = setup_firebase()
        db = setup_session(storage)
        cur = db.cursor()
        query = "SELECT * from THEMES"
        try:
            cur.execute(query)
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
        themes = cur.fetchall()

        return render_template('preferences.html', details=claims, error_message=error_message, user=data, themes=themes)

    else:
        return render_template('index.html')


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
