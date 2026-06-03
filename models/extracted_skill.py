from models import db

class ExtractedSkill(db.Model):
    __tablename__ = 'extracted_skills'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    skill_type = db.Column(db.String(50), nullable=False)  # e.g., 'language', 'framework', 'database', 'tool', 'soft_skill'

    def __repr__(self):
        return f"<ExtractedSkill {self.skill_name} ({self.skill_type})>"
