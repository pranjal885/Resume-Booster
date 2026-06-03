import functools
from flask import Blueprint, render_template, redirect, url_for, session
from models import db, Resume, ATSScore, ExtractedSkill, Recommendation

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(view):
    """
    Decorator to protect routes from unauthenticated users.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@dashboard_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    
    # Query all resumes uploaded by user
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
    total_resumes = len(resumes)
    
    avg_ats_score = 0.0
    max_ats_score = 0.0
    latest_score = None
    latest_resume = None
    
    # Fetch all ATS scores for this user's resumes
    user_ats_scores = ATSScore.query.join(Resume).filter(Resume.user_id == user_id).all()
    
    if user_ats_scores:
        scores = [item.overall_score for item in user_ats_scores]
        avg_ats_score = round(sum(scores) / len(scores), 2)
        max_ats_score = round(max(scores), 2)
        
    latest_resume = resumes[0] if resumes else None
    
    # Details from latest analysis
    skills_by_category = {
        'programming_language': 0,
        'framework': 0,
        'database': 0,
        'tool': 0,
        'technology': 0,
        'soft_skill': 0
    }
    
    skills_list = []
    latest_ats = None
    latest_recommendations = []
    
    if latest_resume:
        # Get latest ATS score
        latest_ats = ATSScore.query.filter_by(resume_id=latest_resume.id).order_by(ATSScore.created_at.desc()).first()
        
        # Get skills list and distributions
        skills = ExtractedSkill.query.filter_by(resume_id=latest_resume.id).all()
        skills_list = [s.skill_name for s in skills]
        
        for s in skills:
            if s.skill_type in skills_by_category:
                skills_by_category[s.skill_type] += 1
                
        # Get latest recommendations
        latest_recommendations = Recommendation.query.filter_by(resume_id=latest_resume.id).order_by(Recommendation.match_percentage.desc()).limit(3).all()
        
    return render_template(
        'dashboard.html',
        resumes=resumes[:5],  # Display top 5 recently analyzed
        total_resumes=total_resumes,
        avg_ats_score=avg_ats_score,
        max_ats_score=max_ats_score,
        latest_resume=latest_resume,
        latest_ats=latest_ats,
        latest_recommendations=latest_recommendations,
        skills_count=len(skills_list),
        skills_by_category=skills_by_category,
        skills_preview=", ".join(skills_list[:8]) + ("..." if len(skills_list) > 8 else "")
    )
