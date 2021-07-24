import sqlite3
from flask import Flask, render_template, url_for, request, redirect
import random
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'


def setup_session():
    db = sqlite3.connect("reviews.db")
    return db


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


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
    if review_theme.lower() == "vaccine":
        review_table_name = "VACCINE"
    elif review_theme.lower() == "pharmacy":
        review_table_name = "PHARMACY"
    else:
        review_table_name = "HOSPITAL"
    review_entity_name = request.form['name']
    # Assuming here that while filling the form, user will be prompted to choose hospital/pharmacy/vaccine name
    # in a dropdown and the user cannot type the name himself. To support this, we will be adding data in the db
    query = "SELECT " + review_table_name + "_ID FROM " + review_table_name + " WHERE name =\"" + review_entity_name + "\""
    cur.execute(query)
    data = cur.fetchone()[0]
    review_vaccine_id = data if review_theme.lower() == "vaccine" else None
    review_pharmacy_id = data if review_theme.lower() == "pharmacy" else None
    review_hospital_id = data if review_theme.lower() == "hospital" else None
    file = request.files['picture']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    review_picture = convertToBinaryData(app.config['UPLOAD_FOLDER'] + '/' + filename)
    review_title = request.form['title']
    review_description = request.form['description']
    review_rating = request.form['rating']
    review_tags = request.form['tags']
    review_id = random.randint(0, 900)
    review_insert_query = "INSERT INTO REVIEWS(REVIEW_ID, USER_ID, TITLE, THEME, HOSPITAL_ID, PHARMACY_ID, \
    VACCINE_ID, RATING, PICTURE, DESCRIPTION, TAGS) VALUES(?,?,?,?,?,?,?,?,?,?,?);"
    data_tuple = (review_id, review_user_id, review_title, review_theme, review_hospital_id,
                  review_pharmacy_id,
                  review_vaccine_id, review_rating,
                  review_picture,
                  review_description,
                  review_tags)
    cur.execute(review_insert_query, data_tuple)
    result = cur.rowcount
    print(result)
    db.commit()
    db.close()
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)
