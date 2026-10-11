from datetime import datetime
from models import db
#Imports the SQLAlchemy db object that we created in models/__init__.py.

class InterviewQuestion(db.Model):
    __tablename__ = 'interview_questions'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    #Connect question to a resume
    skill = db.Column(db.String(100), nullable=False)
    #Stores the skill that the question is related to.
    question = db.Column(db.Text, nullable=False)
    answer_guideline = db.Column(db.Text, nullable=True)  # Contextual hints or answer tips
    #Stores hints or guidelines for answering the question.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InterviewQuestion for {self.skill} (Resume: {self.resume_id})>"
