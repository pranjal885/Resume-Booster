import json
from flask import Blueprint, render_template, request, jsonify, session
from rapidfuzz import fuzz

from models import (
    db,
    Resume,
    ExtractedSkill,
    Recommendation,
    ATSScore
)

from routes.dashboard import login_required

from ai_engine.skill_extractor import extract_skills
from ai_engine.ats_score import ACTION_VERBS


chat_bp = Blueprint('chat', __name__)


# =========================================================
# INTENT DATABASE
# =========================================================

INTENTS = {

    "summary": [
        "generate summary",
        "resume summary",
        "profile summary",
        "professional summary"
    ],

    "missing_skills": [
        "missing skills",
        "skills to improve",
        "skills to add",
        "skill gaps"
    ],

    "certifications": [
        "certifications",
        "courses",
        "aws cert",
        "best certifications"
    ],

    "projects": [
        "projects section",
        "improve projects",
        "project ideas"
    ],

    "ats_score": [
        "ats score",
        "resume score",
        "resume strength"
    ],

    "action_verbs": [
        "action verbs",
        "better wording",
        "resume verbs"
    ]
}


# =========================================================
# LIGHTWEIGHT INTENT DETECTION
# =========================================================

def detect_intent(user_input):

    user_input = user_input.lower()

    best_intent = None
    best_score = 0

    for intent, samples in INTENTS.items():

        for sample in samples:

            score = fuzz.partial_ratio(
                user_input,
                sample
            )

            if score > best_score:

                best_score = score
                best_intent = intent

    # Confidence threshold
    if best_score < 55:
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

    user_msg = request.json.get(
        'message',
        ''
    ).strip().lower()

    if not user_msg:

        return jsonify({
            'response':
                "Please ask a resume-related question."
        })

    # =====================================================
    # LOAD USER DATA
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

        skills_list = [
            s.skill_name
            for s in skills
        ]

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
    # SUMMARY
    # =====================================================

    if intent == "summary":

        if not skills_list:

            response = (
                "Upload and analyze your resume first "
                "so I can generate a professional summary."
            )

        else:

            top_skills = skills_list[:4]

            response = (
                f"Professional Summary:<br><br>"

                f"<i>Result-oriented developer skilled in "
                f"{', '.join(top_skills)}. "
                f"Experienced in building scalable applications, "
                f"solving technical problems, and working on "
                f"real-world software projects.</i>"
            )

    # =====================================================
    # ACTION VERBS
    # =====================================================

    elif intent == "action_verbs":

        response = (
            "Strong resume action verbs:<br><br>"

            "• Engineered<br>"
            "• Developed<br>"
            "• Optimized<br>"
            "• Automated<br>"
            "• Implemented<br>"
            "• Spearheaded"
        )

    # =====================================================
    # MISSING SKILLS
    # =====================================================

    elif intent == "missing_skills":

        if not latest_resume:

            response = (
                "Upload and analyze your resume first."
            )

        else:

            recs = Recommendation.query.filter_by(
                resume_id=latest_resume.id
            ).order_by(
                Recommendation.match_percentage.desc()
            ).all()

            if recs:

                response = (
                    "Recommended improvements:<br><br>"
                )

                for r in recs[:3]:

                    gaps = (
                        r.skill_improvements
                        if r.skill_improvements
                        else "Strong match."
                    )

                    response += (
                        f"• <b>{r.job_title}</b> "
                        f"({r.match_percentage}% Match)<br>"
                        f"Skills to add: {gaps}<br><br>"
                    )

            else:

                response = (
                    "No recommendation data available yet."
                )

    # =====================================================
    # CERTIFICATIONS
    # =====================================================

    elif intent == "certifications":

        response = (
            "Useful certifications for software roles:<br><br>"

            "• AWS Cloud Practitioner<br>"
            "• Google Data Analytics<br>"
            "• IBM Data Science Certificate<br>"
            "• Microsoft Azure Fundamentals"
        )

    # =====================================================
    # PROJECTS
    # =====================================================

    elif intent == "projects":

        response = (
            "Strong technical projects should include:<br><br>"

            "• Problem statement<br>"
            "• Technologies used<br>"
            "• Features implemented<br>"
            "• Real-world impact<br>"
            "• Metrics/results"
        )

    # =====================================================
    # ATS SCORE
    # =====================================================

    elif intent == "ats_score":

        if latest_resume and ats:

            response = (
                f"Current ATS Score: "
                f"<b>{score_val}%</b><br><br>"

                f"Resume Strength: "
                f"<b>{strength}</b><br><br>"

                "Suggestions:<br>"
                "• Add more technical keywords<br>"
                "• Improve project descriptions<br>"
                "• Add measurable achievements"
            )

        else:

            response = (
                "Please analyze your resume first."
            )

    # =====================================================
    # GREETINGS
    # =====================================================

    elif any(
        word in user_msg
        for word in ['hi', 'hello', 'hey']
    ):

        response = (
            f"Hello {resume_name}!<br><br>"

            "I can help with:<br><br>"

            "• ATS score improvement<br>"
            "• Missing skills<br>"
            "• Resume summaries<br>"
            "• Certifications<br>"
            "• Project improvements<br>"
            "• Resume wording"
        )

    # =====================================================
    # UNKNOWN QUESTIONS
    # =====================================================

    else:

        response = (
            "Please ask questions related to resumes, "
            "ATS optimization, skills, projects, "
            "or career guidance."
        )

    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return jsonify({
        'response': response
    })

