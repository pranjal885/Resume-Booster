from datetime import datetime
#You're importing datetime so you can record when a user account was created.
from werkzeug.security import generate_password_hash, check_password_hash
#These two functions are used for password security.
from models import db


#create python class called user that inherits from db.Model. This means that the User class is a model that SQLAlchemy will use to create a table in the database.
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resumes = db.relationship('Resume', backref='user', cascade='all, delete-orphan', lazy=True)
    #db.relationship('Resume') defines the relationship between User and Resume, allowing one user to have multiple resumes and allowing each resume to access its associated user.
    job_descriptions = db.relationship('JobDescription', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
    #__repr__() defines a readable representation of the User object.
    # In this case, it displays the username of the user.
