import json
import re
import html
from flask import Blueprint, render_template, request, jsonify, session
from rapidfuzz import fuzz

from models import (
    db,
    Resume,
    JobDescription,
    ExtractedSkill,
    Recommendation,
    ATSScore
)
from routes.dashboard import login_required
from ai_engine.llm_client import call_llm, is_ai_available

chat_bp = Blueprint('chat', __name__)

def format_markdown_to_html(text):
    """
    Converts Gemini Markdown text (bold, bullet points, headers, line breaks)
    into safe HTML for clean display in the chat UI.
    """
    if not text:
        return ""
    # Safely escape HTML characters first to prevent XSS
    escaped = html.escape(text)
    
    # Convert bold: **text** or __text__ -> <b>text</b>
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escaped)
    formatted = re.sub(r'__(.*?)__', r'<b>\1</b>', formatted)
    
    # Convert italic: *text* or _text_ -> <i>text</i>
    formatted = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', formatted)
    
    # Convert headings: ### Heading -> <b>Heading</b>
    formatted = re.sub(r'^#{1,6}\s*(.*?)$', r'<b>\1</b>', formatted, flags=re.MULTILINE)
    
    # Convert bullet points: line starting with * or - -> •
    formatted = re.sub(r'^\s*[\*\-]\s+', r'• ', formatted, flags=re.MULTILINE)
    
    # Convert linebreaks to <br>
    formatted = formatted.replace('\n', '<br>')
    formatted = re.sub(r'(<br>\s*){3,}', '<br><br>', formatted)
    
    return formatted

# =========================================================
# INTENT DATABASE (Rule-based Fallback)
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

def detect_intent(user_input):
    """
    Determines user intent using fuzzy string matching (Fallback).
    """
    user_input = user_input.lower()
    best_intent = None
    best_score = 0

    for intent, samples in INTENTS.items():
        for sample in samples:
            score = fuzz.partial_ratio(user_input, sample)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score < 55:
        return "unknown"

    return best_intent

@chat_bp.route('/chat')
@login_required
def index():
    return render_template('chat.html')

@chat_bp.route('/chat/message', methods=['POST'])
@login_required
def message():
    user_id = session['user_id']
    user_msg = request.json.get('message', '').strip()

    if not user_msg:
        return jsonify({'response': "Please ask a resume-related question."})

    # =====================================================
    # LOAD AUTHENTICATED USER DATA ONLY (STRICT SECURITY)
    # =====================================================
    latest_resume = Resume.query.filter_by(
        user_id=user_id
    ).order_by(
        Resume.created_at.desc()
    ).first()

    skills_list = []
    resume_name = session.get('username', 'Job Seeker')
    score_val = 0
    strength = "N/A"
    ats = None
    job_title = "Target Position"
    job_desc = ""
    parsed_text = ""

    if latest_resume:
        resume_name = latest_resume.name or resume_name
        parsed_text = latest_resume.parsed_text or ""
        
        skills = ExtractedSkill.query.filter_by(resume_id=latest_resume.id).all()
        skills_list = [s.skill_name for s in skills]

        ats = ATSScore.query.filter_by(resume_id=latest_resume.id).order_by(ATSScore.created_at.desc()).first()
        if ats:
            score_val = ats.overall_score
            strength = ats.strength_meter
            job_record = JobDescription.query.get(ats.job_description_id)
            if job_record:
                job_title = job_record.title
                job_desc = job_record.description_text

    # =====================================================
    # 1. ATTEMPT REAL GEMINI AI CHATBOT RESPONSE
    # =====================================================
    if is_ai_available():
        system_instruction = (
            "You are the AI Resume Assistant & Executive Career Coach for Resume Booster. "
            "You are conversing directly with the authenticated user about their uploaded resume and job match. "
            "Answer their questions accurately, specifically, and concisely using ONLY their provided context. "
            "If they ask for bullet rewrites, summary generation, skill recommendations, or ATS feedback, "
            "tailor your advice specifically to their resume content. "
            "Do NOT fabricate experience or metrics. Format responses clearly with line breaks (<br>) and HTML lists where appropriate."
        )
        
        prompt = f"""
AUTHENTICATED USER RESUME CONTEXT:
Candidate Name: {resume_name}
Target Role: {job_title}
Target Job Description: {job_desc[:1200] if job_desc else 'Not specified'}

RESUME TEXT:
{parsed_text[:3000] if parsed_text else 'No resume uploaded yet.'}

EXTRACTED SKILLS:
{', '.join(skills_list) if skills_list else 'None detected'}

LATEST ATS ASSESSMENT:
Overall Score: {score_val}% ({strength})

USER QUESTION:
"{user_msg}"
"""
        ai_response = call_llm(prompt, system_instruction=system_instruction)
        if ai_response:
            formatted_response = format_markdown_to_html(ai_response)
            return jsonify({'response': formatted_response})

    # =====================================================
    # 2. RULE-BASED FALLBACK CHATBOT (If Gemini offline/unavailable)
    # =====================================================
    intent = detect_intent(user_msg.lower())

    if intent == "summary":
        if not skills_list:
            response = "Upload and analyze your resume first so I can generate a professional summary."
        else:
            top_skills = skills_list[:4]
            response = (
                f"<b>Professional Summary Suggestion:</b><br><br>"
                f"<i>Results-oriented professional skilled in {', '.join(top_skills)}. "
                f"Experienced in building scalable applications, solving complex problems, and delivering key software features.</i>"
            )

    elif intent == "action_verbs":
        response = (
            "<b>Strong resume action verbs:</b><br><br>"
            "• Spearheaded<br>"
            "• Engineered<br>"
            "• Optimized<br>"
            "• Automated<br>"
            "• Implemented<br>"
            "• Orchestrated"
        )

    elif intent == "missing_skills":
        if not latest_resume:
            response = "Upload and analyze your resume first."
        else:
            recs = Recommendation.query.filter_by(resume_id=latest_resume.id).order_by(Recommendation.match_percentage.desc()).all()
            if recs:
                response = "<b>Recommended Skill Improvements:</b><br><br>"
                for r in recs[:3]:
                    gaps = r.skill_improvements if r.skill_improvements else "Strong match."
                    response += f"• <b>{r.job_title}</b> ({r.match_percentage}% Match)<br>Skills to add: {gaps}<br><br>"
            else:
                response = "No recommendation data available yet. Upload a resume on the Analyze page."

    elif intent == "certifications":
        response = (
            "<b>Useful certifications for software roles:</b><br><br>"
            "• AWS Certified Solutions Architect / Cloud Practitioner<br>"
            "• Google Cloud Professional Developer<br>"
            "• Kubernetes Application Developer (CKAD)<br>"
            "• Microsoft Certified: Azure Fundamentals"
        )

    elif intent == "projects":
        response = (
            "<b>Structure for high-impact project descriptions:</b><br><br>"
            "• <b>Problem statement</b> - What challenges were you solving?<br>"
            "• <b>Technologies used</b> - List languages, frameworks, databases<br>"
            "• <b>Key features</b> - What did you personally build?<br>"
            "• <b>Measurable impact</b> - Performance speedup, user count, or accuracy improvement"
        )

    elif intent == "ats_score":
        if latest_resume and ats:
            response = (
                f"Current ATS Score: <b>{score_val}%</b><br>"
                f"Resume Strength: <b>{strength}</b><br><br>"
                "<b>Top recommendations to boost score:</b><br>"
                "• Add key missing skills from the job description<br>"
                "• Use strong action verbs at the start of bullet points<br>"
                "• Quantify your project outcomes with metrics"
            )
        else:
            response = "Please analyze your resume first on the Analyze page."

    elif any(word in user_msg.lower() for word in ['hi', 'hello', 'hey']):
        response = (
            f"Hello {resume_name}!<br><br>"
            "I am your AI Resume Assistant. I can help you with:<br>"
            "• Resume bullet point improvements<br>"
            "• Personalized professional summaries<br>"
            "• ATS score analysis and missing skills<br>"
            "• Interview question preparation<br>"
            "• Project description optimization"
        )

    else:
        response = (
            "I'm here to help optimize your resume and career strategy! "
            "Try asking me to generate a summary, suggest missing skills, improve a project bullet point, or review your ATS score."
        )

    return jsonify({'response': response})