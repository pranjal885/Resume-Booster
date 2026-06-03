from datetime import datetime
from models import db

class InterviewQuestion(db.Model):
    __tablename__ = 'interview_questions'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    skill = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer_guideline = db.Column(db.Text, nullable=True)  # Contextual hints or answer tips
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InterviewQuestion for {self.skill} (Resume: {self.resume_id})>"
