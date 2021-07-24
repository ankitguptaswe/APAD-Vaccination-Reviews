from app import db


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    themes = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary)


class Hospital(db.Model):
    hospital_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary)


class Pharmacy(db.Model):
    pharmacy_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary)


class Vaccine(db.Model):
    vaccine_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary)


class Reviews(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    theme = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer)
    pharmacy_id = db.Column(db.Integer)
    vaccine_id = db.Column(db.Integer)
    rating = db.Column(db.Integer, nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(100), nullable=False)


if __name__ == "__main__":
    # Run this file directly to create the database tables.
    print("Creating database tables...")
    db.create_all()
    print("Done!")