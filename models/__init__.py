from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to ensure they are registered with metadata
from models.user import User
from models.resume import Resume
from models.extracted_skill import ExtractedSkill
from models.job_description import JobDescription
from models.ats_score import ATSScore
from models.recommendation import Recommendation
from models.interview_question import InterviewQuestion
