from datetime import datetime
from models import db

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ats_scores = db.relationship('ATSScore', backref='job_description', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<JobDescription {self.title}>"
