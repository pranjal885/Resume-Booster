from datetime import datetime
from models import db

class ATSScore(db.Model):
#Creates a database model called ATSScore.Because it inherits from:db.Model
#SQLAlchemy knows that this class represents a database table.
    __tablename__ = 'ats_scores'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id', ondelete='CASCADE'), nullable=False)
    
    # Core scoring details
    overall_score = db.Column(db.Float, nullable=False)
    skills_score = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, nullable=False)
    education_score = db.Column(db.Float, nullable=False)
    projects_score = db.Column(db.Float, nullable=False)
    certifications_score = db.Column(db.Float, nullable=False)
    
    strength_meter = db.Column(db.String(50), nullable=False)  # e.g., 'Weak', 'Good', 'Excellent'
    feedback_json = db.Column(db.Text, nullable=True)  # JSON-formatted detailed feedback on improvements
    #Why nullable=True? Because feedback is optional.An ATS score can exist even if detailed feedback isn't available.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #Stores when this ATS score was created.

    def __repr__(self):
    #Defines how an ATSScore object should appear when printed/debugged.
        return f"<ATSScore {self.overall_score} (Resume: {self.resume_id})>"


#One ATSScore represents the result of analyzing one resume against one job description.