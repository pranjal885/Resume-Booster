
import json
from flask import Blueprint, render_template, request, jsonify, session
from models import db, Resume, ExtractedSkill, Recommendation, ATSScore
from routes.dashboard import login_required
from ai_engine.skill_extractor import extract_skills
from ai_engine.ats_score import ACTION_VERBS

# NLP + Semantic Matching
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

# Load AI model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Blueprint
chat_bp = Blueprint('chat', __name__)

# =========================================================
# INTENT DATABASE
# =========================================================

INTENTS = {

    "summary": [
        "generate summary",
        "resume summary",
        "write professional summary",
        "profile summary",
        "generate profile",
        "summary for resume"
    ],

    "missing_skills": [
        "missing skills",
        "skills to improve",
        "skills to add",
        "what skills am i missing",
        "skill gaps",
        "missing tech stack"
    ],

    "certifications": [
        "should i add certifications",
        "certificates",
        "certification advice",
        "aws cert",
        "courses to do",
        "best certifications"
    ],

    "projects": [
        "improve projects",
        "projects section",
        "project ideas",
        "how are my projects",
        "improve project descriptions"
    ],

    "ats_score": [
        "ats score",
        "resume score",
        "check ats",
        "resume strength",
        "how good is my resume",
        "my score"
    ],

    "action_verbs": [
        "action verbs",
        "better wording",
        "improve wording",
        "replace worked on",
        "resume verbs",
        "strong action verbs"
    ]
}

# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intent(user_input):

    user_embedding = model.encode(user_input)

    best_intent = None
    best_score = 0

    for intent, samples in INTENTS.items():

        for sample in samples:

            # Semantic Similarity
            sample_embedding = model.encode(sample)

            semantic_score = util.cos_sim(
                user_embedding,
                sample_embedding
            ).item()

            # Fuzzy Matching
            fuzzy_score = fuzz.partial_ratio(
                user_input,
                sample
            ) / 100

            # Combined Score
            final_score = (semantic_score * 0.7) + (fuzzy_score * 0.3)

            if final_score > best_score:
                best_score = final_score
                best_intent = intent

    # Confidence Threshold
    if best_score < 0.45:
        return "unknown"

    return best_intent

# =========================================================
# CHAT PAGE
# =========================================================

@chat_bp.route('/chat')
@login_required
def index():
    return render_template('chat.html')

# =========================================================
# CHAT MESSAGE API
# =========================================================

@chat_bp.route('/chat/message', methods=['POST'])
@login_required
def message():

    user_id = session['user_id']

    user_msg = request.json.get('message', '').strip().lower()

    if not user_msg:
        return jsonify({
            'response': (
                "I didn't catch that. "
                "Please ask something related to your resume."
            )
        })

    # =====================================================
    # FETCH USER RESUME DATA
    # =====================================================

    latest_resume = Resume.query.filter_by(
        user_id=user_id
    ).order_by(
        Resume.created_at.desc()
    ).first()

    skills_list = []
    resume_name = "Job Seeker"
    score_val = 0
    strength = "N/A"

    ats = None

    if latest_resume:

        resume_name = latest_resume.name or "Job Seeker"

        skills = ExtractedSkill.query.filter_by(
            resume_id=latest_resume.id
        ).all()

        skills_list = [s.skill_name for s in skills]

        ats = ATSScore.query.filter_by(
            resume_id=latest_resume.id
        ).order_by(
            ATSScore.created_at.desc()
        ).first()

        if ats:
            score_val = ats.overall_score
            strength = ats.strength_meter

    # =====================================================
    # DETECT INTENT
    # =====================================================

    intent = detect_intent(user_msg)

    # =====================================================
    # SUMMARY GENERATION
    # =====================================================

    if intent == "summary":

        if not skills_list:

            response = (
                "I'd love to help generate a professional summary for you.<br><br>"
                "Please upload and analyze your resume first."
            )

        else:

            top_skills = skills_list[:4]

            response = (
                f"Here is a customized professional summary based on your profile:<br><br>"

                f"<i>\"Result-oriented and analytical professional skilled in "
                f"{', '.join(top_skills[:-1])} and {top_skills[-1]}. "
                f"Experienced in developing scalable solutions, solving technical problems, "
                f"and collaborating in fast-paced engineering environments.\"</i>"
            )

    # =====================================================
    # ACTION VERBS
    # =====================================================

    elif intent == "action_verbs":

        response = (
            "Using strong action verbs improves ATS score and recruiter impact.<br><br>"

            "Recommended action verbs:<br><br>"

            "• <b>Spearheaded</b> — Led an initiative<br>"
            "• <b>Optimized</b> — Improved performance<br>"
            "• <b>Engineered</b> — Built technical systems<br>"
            "• <b>Automated</b> — Reduced manual work<br>"
            "• <b>Implemented</b> — Successfully developed features<br><br>"

            "Example:<br>"
            "<i>'Engineered an AI-powered ATS optimization platform using Flask and NLP.'</i>"
        )

    # =====================================================
    # MISSING SKILLS
    # =====================================================

    elif intent == "missing_skills":

        if not latest_resume:

            response = (
                "Upload and analyze your resume first so I can detect missing skills."
            )

        else:

            recs = Recommendation.query.filter_by(
                resume_id=latest_resume.id
            ).order_by(
                Recommendation.match_percentage.desc()
            ).all()

            if recs:

                rec_feedback = (
                    "Based on your resume analysis, here are your strongest matching roles:<br><br>"
                )

                for r in recs[:3]:

                    gaps = (
                        r.skill_improvements
                        if r.skill_improvements
                        else "Excellent fit."
                    )

                    rec_feedback += (
                        f"• <b>{r.job_title}</b> "
                        f"({r.match_percentage}% Match)<br>"
                        f"&nbsp;&nbsp;<i>Skills to add:</i> {gaps}<br><br>"
                    )

                response = rec_feedback

            else:

                response = (
                    "I haven't analyzed your resume against job roles yet.<br><br>"
                    "Upload a job description in Analyze Resume to unlock recommendations."
                )

    # =====================================================
    # CERTIFICATIONS
    # =====================================================

    elif intent == "certifications":

        response = (
            "Yes — certifications can improve your ATS score and credibility, "
            "especially for technical roles.<br><br>"

            "Recommended certifications for AI/Data roles:<br><br>"

            "• AWS Cloud Practitioner<br>"
            "• Google Data Analytics<br>"
            "• TensorFlow Developer Certificate<br>"
            "• IBM Data Science Professional Certificate<br><br>"

            "However, practical projects and real-world skills matter more than certifications alone."
        )

    # =====================================================
    # PROJECTS
    # =====================================================

    elif intent == "projects":

        response = (
            "Your projects section is one of the MOST important parts of a technical resume.<br><br>"

            "Strong projects should include:<br>"
            "• Problem statement<br>"
            "• Technologies used<br>"
            "• Real impact/results<br>"
            "• Metrics or accuracy<br><br>"

            "Example:<br>"

            "<i>'Built an AI-powered Resume Booster platform using Flask, MySQL, NLP, "
            "and Sentence Transformers for semantic ATS optimization.'</i>"
        )

    # =====================================================
    # ATS SCORE
    # =====================================================

    elif intent == "ats_score":

        if latest_resume and ats:

            response = (
                f"Your latest analyzed resume is <b>{latest_resume.filename}</b>.<br><br>"

                f"Current ATS Score: <b>{score_val}%</b><br>"
                f"Resume Strength: <b>{strength}</b><br><br>"

                "Suggestions to improve score:<br>"
                "• Add more job-relevant keywords<br>"
                "• Improve project descriptions<br>"
                "• Add measurable achievements<br>"
                "• Add missing technical skills"
            )

        else:

            response = (
                "You haven't analyzed a resume yet.<br><br>"
                "Please upload a resume in Analyze Resume first."
            )

    # =====================================================
    # GREETINGS
    # =====================================================

    elif any(word in user_msg for word in ['hi', 'hello', 'hey']):

        response = (
            f"Hello {resume_name}! I am your AI Resume Coach.<br><br>"

            "You can ask me about:<br><br>"

            "• ATS score improvement<br>"
            "• Missing skills<br>"
            "• Resume summaries<br>"
            "• Certifications<br>"
            "• Projects<br>"
            "• Job recommendations<br>"
            "• Action verbs"
        )

    # =====================================================
    # UNKNOWN / IRRELEVANT QUESTIONS
    # =====================================================

    else:

        response = (
            "I specialize in resume optimization and career guidance.<br><br>"

            "Please ask resume-related questions such as:<br><br>"

            "• How can I improve my ATS score?<br>"
            "• What skills am I missing?<br>"
            "• Suggest certifications<br>"
            "• Improve my projects section<br>"
            "• Generate a professional summary<br>"
            "• Suggest better action verbs"
        )

    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return jsonify({
        'response': response
    })

