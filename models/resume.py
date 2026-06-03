from datetime import datetime
from models import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    parsed_text = db.Column(db.Text, nullable=True)
    
    # Extracted contact details
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    
    # Extracted sections
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    projects = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    extracted_skills = db.relationship('ExtractedSkill', backref='resume', cascade='all, delete-orphan', lazy=True)
    ats_scores = db.relationship('ATSScore', backref='resume', cascade='all, delete-orphan', lazy=True)
    recommendations = db.relationship('Recommendation', backref='resume', cascade='all, delete-orphan', lazy=True)
    interview_questions = db.relationship('InterviewQuestion', backref='resume', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<Resume {self.filename}>"
