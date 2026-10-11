#this function recommends suitable job roles based on the candidate's resume and target job description.

from ai_engine.skill_extractor import extract_skills
from ai_engine.llm_client import call_llm_json, is_ai_available

# Standard industry roles with their typical required skill profiles (Rule-based Fallback)
JOB_PROFILES = [
    {
        'title': 'Full Stack Developer',
        'required_skills': ['Python', 'JavaScript', 'React', 'HTML', 'CSS', 'Node.js', 'Flask', 'MySQL', 'Git', 'Docker', 'REST API'],
        'description': 'Develop and maintain end-to-end web applications, integrating elegant client UIs with scalable backend services and databases.'
    },
    {
        'title': 'Data Scientist / ML Engineer',
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning', 'SQL', 'Pandas', 'NumPy', 'scikit-learn', 'TensorFlow', 'PyTorch', 'NLP', 'Data Science'],
        'description': 'Design, train, and deploy predictive models and deep learning solutions to extract valuable business insights.'
    },
    {
        'title': 'DevOps Engineer',
        'required_skills': ['Docker', 'Kubernetes', 'AWS', 'Linux', 'CI/CD', 'GitHub Actions', 'Jenkins', 'Terraform', 'Nginx', 'Git', 'Bash'],
        'description': 'Architect and automate cloud infrastructure, continuous deployment pipelines, and system monitoring tools.'
    },
    {
        'title': 'Frontend Engineer',
        'required_skills': ['JavaScript', 'TypeScript', 'React', 'HTML', 'CSS', 'Tailwind CSS', 'Bootstrap', 'Git', 'Yarn', 'Vite'],
        'description': 'Implement interactive interfaces and responsive layouts, translating design mockups into web applications.'
    },
    {
        'title': 'Backend Engineer',
        'required_skills': ['Python', 'SQL', 'PostgreSQL', 'MySQL', 'Node.js', 'Express.js', 'REST API', 'Docker', 'AWS', 'Microservices', 'Git'],
        'description': 'Architect server-side logic, optimize database engines, structure microservices, and deploy secure APIs.'
    },
    {
        'title': 'Mobile App Developer',
        'required_skills': ['Dart', 'Flutter', 'React Native', 'Swift', 'Kotlin', 'REST API', 'Firebase', 'Git'],
        'description': 'Build high-performance, native and cross-platform mobile apps for Android and iOS devices.'
    }
]

def recommend_jobs_ai(resume_text, job_desc=""):
    """
    Uses Gemini LLM to analyze resume skills, experience, projects, and target role,
    providing personalized career path recommendations with fit explanations and skill improvement roadmaps.
    
    STRICT RULE: Do not claim candidate is qualified for roles unsupported by their resume facts.
    """
    if not is_ai_available() or not resume_text:
        return None
        
    system_instruction = (
        "You are an AI Career Advisor & Tech Industry Recruiter. "
        "Analyze the candidate's resume and target job description to recommend realistic suitable roles, "
        "explain WHY each role fits their current skills, and list actionable missing skills to learn."
    )
    
    prompt = f"""
CANDIDATE RESUME TEXT:
{resume_text[:3000]}

TARGET JOB DESCRIPTION:
{job_desc[:1000] if job_desc else 'Not provided'}

TASK:
Provide 3-5 personalized job role recommendations in a JSON array of objects:
[
  {{
    "job_title": "Role Title",
    "description": "Why this role fits the candidate's actual projects/skills and what they would do.",
    "match_percentage": 85.0,
    "skill_improvements": ["Skill 1", "Skill 2", "Skill 3"]
  }}
]
"""
    result = call_llm_json(prompt, system_instruction=system_instruction)
    if isinstance(result, list) and len(result) > 0:
        cleaned_recs = []
        for rec in result:
            if isinstance(rec, dict) and 'job_title' in rec:
                cleaned_recs.append({
                    'job_title': rec['job_title'],
                    'description': rec.get('description', 'Role alignment based on parsed resume skills.'),
                    'match_percentage': float(rec.get('match_percentage', 70.0)),
                    'skill_improvements': rec.get('skill_improvements', [])
                })
        if cleaned_recs:
            cleaned_recs.sort(key=lambda x: x['match_percentage'], reverse=True)
            #This sorts the recommendations according to their match percentage.
            return cleaned_recs
            
    return None

def recommend_jobs(resume_text, job_desc=""):
    """
    Compares resume against target roles using Gemini AI if available, falling back to static JOB_PROFILES.
    """
    if not resume_text:
        return []
        
    # 1. Attempt Gemini AI job recommendations
    ai_recs = recommend_jobs_ai(resume_text, job_desc)
    if ai_recs:
        return ai_recs
        
    # 2. Rule-based Fallback
    extracted_skills_data = extract_skills(resume_text)
    user_skills = {s.lower() for s in extracted_skills_data['flat_list']}
    #This creates a set of the user's skills in lowercase.
    recommendations = []
    
    for profile in JOB_PROFILES:
        req_skills_lower = {s.lower() for s in profile['required_skills']}
        matched = req_skills_lower.intersection(user_skills)
        #This finds skills that both the job and candidate have.
        missing = req_skills_lower.difference(user_skills)
        #finds skills required by the job that the candidate doesn't have.
        
        if req_skills_lower:
            match_percentage = (len(matched) / len(req_skills_lower)) * 100
            #For example:
# Job requires 10 skills.
# Candidate has 7 of them.
# 7 / 10 × 100 = 70%
# So the fallback gives a 70% skill match.
        else:
            match_percentage = 0.0
            
        missing_display = [s for s in profile['required_skills'] if s.lower() in missing]
        skill_improvements = missing_display[:4]
        
        recommendations.append({
            'job_title': profile['title'],
            'description': profile['description'],
            'match_percentage': round(match_percentage, 2),
            'skill_improvements': skill_improvements
        })
        
    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    return recommendations
