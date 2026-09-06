import json
from flask import Blueprint, render_template, request, jsonify, session
from rapidfuzz import fuzz
#RapidFuzz is a Python library used for fuzzy string matching.
#Instead of requiring an exact match:
#"missing skills"
#it can recognize something similar like:
#"What skills am I missing?"

from models import (
    db,
    Resume,
    ExtractedSkill,
    Recommendation,
    ATSScore
)
#These models allow the chat to access the user's stored data:
#Resume, ExtractedSkill, Recommendation ,ATSScore
#For example, if the user asks:What's my ATS score?
#the chat can get the score from ATSScore.

from routes.dashboard import login_required
#only chat users who are logged in can access the chat page and send messages.


chat_bp = Blueprint('chat', __name__)


# =========================================================
# INTENT DATABASE
# =========================================================

#This dictionary contains the different types of questions your chatbot understands.
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
#This function determines what the user is asking for.

    user_input = user_input.lower()
    #convert the user input to lowercase to make the matching case-insensitive.

    best_intent = None
    best_score = 0
    #As we compare the user's question against the examples, we'll update these values.

    for intent, samples in INTENTS.items():
    #Loop through intents
    #intent = "ats_score"
    #samples = [
    #    "ats score",
    #    "resume score",
    #    "resume strength"
    #]

        for sample in samples:
        #Loop through sample phrases for each intent

            score = fuzz.partial_ratio(
                user_input,
                sample
            )
            #This calculates how similar the user's message is to the sample phrase.
            #partial_ratio() is useful when one string contains a phrase similar to another.
        #     For example:
        #    User: "What is my current ATS score?"
        #    Sample: "ats score"
        #    The similarity score will be high.
        #    The exact numeric result depends on the strings.

            if score > best_score:

                best_score = score
                best_intent = intent

    # Confidence threshold
    if best_score < 55:
        return "unknown"
    #for e.g., if the user asks a question unrelated to resumes, like:
    #User:"Tell me a joke"
   #Similarity with resume-related intents → low
    #best_score = 20
    #20 < 55
    #↓
    #unknown

    return best_intent


# =========================================================
# CHAT PAGE
# =========================================================

@chat_bp.route('/chat')
@login_required
def index():
#Creates: /chat , And protects it with: @login_required
    
    return render_template('chat.html')


# =========================================================
# CHAT MESSAGE API
# =========================================================

@chat_bp.route('/chat/message', methods=['POST'])
@login_required
def message():

    user_id = session['user_id']
    #Gets the logged-in user's ID.
    #This is important because the chatbot needs to access that user's resume, not someone else's.

    user_msg = request.json.get(
        'message',
        ''
    ).strip().lower()
    #This reads the JSON sent by the frontend.
    #For example:{
    #             "message": "  What is my ATS Score?  "
    #            }
    #becomes:"what is my ats score?"

    if not user_msg:

        return jsonify({
            'response':
                "Please ask a resume-related question."
        })
        #If the user sends nothing: The backend sends JSON back to the frontend.

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
    #These are default values.
    #If the user doesn't have a resume yet, the chatbot can still respond without crashing.

    if latest_resume:
    
        resume_name = latest_resume.name or "Job Seeker"
        #If the user has a resume, we get the name from the database.
        skills = ExtractedSkill.query.filter_by(
            resume_id=latest_resume.id
        ).all()
        #Gets all skills belonging to the latest resume.

        skills_list = [
            s.skill_name
            for s in skills
        ]
        #converts skills into a simple list:["Python", "Flask", "SQL", "Docker"]

        ats = ATSScore.query.filter_by(
            resume_id=latest_resume.id
        ).order_by(
            ATSScore.created_at.desc()
        ).first()
        #Gets the most recent ATS score for that resume.

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
            #take the first four skills.Then create a predefined summary:

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
            #So it gets recommendations generated earlier by the analysis pipeline.

            if recs:

                response = (
                    "Recommended improvements:<br><br>"
                )

                for r in recs[:3]:
                #it creates a response showing:
                # Job title
                # Match percentage
                # Skills to add

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
    #Returns predefined certification suggestions.

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
                #The score itself comes from the database:score_val = ats.overall_score
                #So the chatbot isn't calculating the score here.
                #It's retrieving the previously calculated score.


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
    #This checks whether the user's message contains: it gives a friendly greeting if the user says "hi", "hello", or "hey".

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
    #The backend sends the chatbot's answer back to the frontend as JSON.