import sqlite3
from flask import Flask, render_template, url_for, request, redirect
import secrets
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/img/reviews'


def setup_session():
    db = sqlite3.connect("reviews.db")
    return db


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
    review_picture = filename
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
def view_all_themes():
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


if __name__ == '__main__':
    app.run(debug=True)
