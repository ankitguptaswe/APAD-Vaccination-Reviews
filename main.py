import datetime
import sqlite3
from flask import Flask, render_template, url_for, request, redirect
from google.auth.transport import requests
from google.cloud import datastore
import google.oauth2.id_token
import random
from werkzeug.utils import secure_filename
import os

datastore_client = datastore.Client()

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

def setup_session():
    db = sqlite3.connect("reviews.db")
    return db

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/img/reviews'
firebase_request_adapter = requests.Request()

@app.route('/')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            store_time(claims['email'], datetime.datetime.now())
            times = fetch_times(claims['email'], 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)

    return render_template(
        'index.html',
        user_data=claims, error_message=error_message, times=times)

@app.route('/<int:user_id>/post', methods=['POST'])
def reviews(user_id):
    """
    This function/service is used to post review of a theme item by a user
    :param user_id: unique user id who is posting the review
    :return: None
    """
    db = setup_session()
    cur = db.cursor()
    review_user_id = user_id
    review_theme = request.form['theme']
    file = request.files['picture']
    if file:
        filename = secrets.token_hex(16)
        file_extension = os.path.splitext(file.filename)[1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + file_extension))
    review_picture = filename + file_extension
    review_title = request.form['title']
    review_description = request.form['description']
    review_rating = request.form['rating']
    review_tags = request.form['tags']
    review_insert_query = "INSERT INTO REVIEWS(USER_ID, TITLE, THEME, RATING, PICTURE, DESCRIPTION, TAGS) " \
                          "VALUES(?,?,?,?,?,?,?);"
    data_tuple = (review_user_id, review_title, review_theme, review_rating, review_picture,
                  review_description, review_tags)
    try:
        cur.execute(review_insert_query, data_tuple)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
    result = cur.rowcount
    if result == 1:
        db.commit()
        db.close()
        return 'OK'
    else:
        return 'Failed to insert data in db'

@app.route('/themes/all', methods=['GET'])
def view_themes():

    """
    This function/service is used to get all themes from the db
    :return: string containing all themes
    """
    db = setup_session()
    cur = db.cursor()
    query = "SELECT * from THEMES"
    try:
        cur.execute(query)
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
    data = cur.fetchall()
    return render_template("themes.html", details=data)

@app.route('/themes/create', methods=['GET', 'POST'])
def create_theme():
    if request.method == 'POST':
        th_name = request.form['th_name']
        th_description = request.form['th_description']
        th_photo = request.files['photo']
        
        uploads_dir = 'static/img/themes'
        th_photo.save(os.path.join(uploads_dir, secure_filename(th_photo.filename)))
        
        db = setup_session()
        sql = ''' INSERT INTO THEMES(THEME_NAME,PICTURE,DESCRIPTION)
                  VALUES(?,?,?) '''
        task = (th_name,th_photo.filename,th_description)
        try:
            cur = db.cursor()
            cur.execute(sql, task)
            db.commit()
            return view_themes()
        except:
            return 'There was an issue adding your task'
    else:
        return render_template('create_theme.html')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)