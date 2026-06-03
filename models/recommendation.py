from datetime import datetime
from models import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    match_percentage = db.Column(db.Float, nullable=False)
    skill_improvements = db.Column(db.Text, nullable=True)  # Comma-separated or newline-separated suggested skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Recommendation {self.job_title} ({self.match_percentage}%)>"
