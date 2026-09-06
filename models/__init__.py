from flask_sqlalchemy import SQLAlchemy
#You're importing SQLAlchemy from the Flask-SQLAlchemy library.
#SQLAlchemy is a Python library that allows us to work with databases using Python objects/classes instead of writing SQL for everything.

db = SQLAlchemy() #you're creating the database object that your entire application will use.

# Import models to ensure they are registered with metadata
from models.user import User
from models.resume import Resume
from models.extracted_skill import ExtractedSkill
from models.job_description import JobDescription
from models.ats_score import ATSScore
from models.recommendation import Recommendation
from models.interview_question import InterviewQuestion
