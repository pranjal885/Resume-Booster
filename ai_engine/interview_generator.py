from ai_engine.llm_client import call_llm_json, is_ai_available

# Pre-defined interview questions database (Rule-based Fallback)
SKILL_INTERVIEW_DB = {
    'Python': [
        {
            'question': 'What is the difference between a list and a tuple in Python? When would you choose one over the other?',
            'answer_guideline': 'Lists are mutable (can be changed), while tuples are immutable. Tuples are slightly faster and occupy less memory. Use tuples for fixed data structures to protect data integrity, and lists for dynamic collections.'
        },
        {
            'question': 'Explain Python list comprehensions and how they differ from standard for-loops.',
            'answer_guideline': 'List comprehensions provide a concise way to create lists. They are generally faster because they are optimized under the hood. Avoid nested or overly complex list comprehensions for readability.'
        }
    ],
    'JavaScript': [
        {
            'question': 'Explain the difference between event bubble propagation and event capturing in JavaScript.',
            'answer_guideline': 'In bubbling, the event starts from the target element and bubbles up to the window. In capturing, the event goes down from the window to the target. Standard event listeners use bubbling by default.'
        },
        {
            'question': 'What are closures in JavaScript, and what is their practical use case?',
            'answer_guideline': 'A closure is the combination of a function bundled together with references to its surrounding state. Closures allow functions to have "private" variables or maintain state between invocations.'
        }
    ],
    'React': [
        {
            'question': 'What are React Hooks? Explain useState and useEffect with examples.',
            'answer_guideline': 'Hooks let functional components manage state and lifecycle side-effects. useState declares a state variable, and useEffect handles operations like fetching data or DOM updates after rendering.'
        },
        {
            'question': 'What is the Virtual DOM, and how does React use it to optimize rendering?',
            'answer_guideline': 'The Virtual DOM is a lightweight in-memory representation of the real DOM. When state changes, React diffs the virtual DOM with the previous version and batches updates to the real DOM.'
        }
    ],
    'Docker': [
        {
            'question': 'What is the difference between a Docker Image and a Docker Container?',
            'answer_guideline': 'A Docker Image is a read-only template containing instructions to build a container. A Docker Container is a runnable, isolated instance of that image.'
        }
    ],
    'Kubernetes': [
        {
            'question': 'Explain the difference between a Pod, a Deployment, and a Service in Kubernetes.',
            'answer_guideline': 'A Pod is the smallest deployable unit. A Deployment manages state, scaling, and rolling updates for Pods. A Service exposes a group of Pods as a network service with a stable IP.'
        }
    ],
    'SQL': [
        {
            'question': 'What is the difference between INNER JOIN, LEFT JOIN, and OUTER JOIN in database queries?',
            'answer_guideline': 'INNER JOIN returns records with matching values in both tables. LEFT JOIN returns all records from the left table and matched right records. OUTER JOIN returns all records when there is a match in either table.'
        }
    ],
    'MySQL': [
        {
            'question': 'What are indexes in MySQL, and how do they speed up database performance?',
            'answer_guideline': 'Indexes are data structures (usually B-Trees) that allow fast searching. They speed up SELECT queries but slow down INSERT, UPDATE, and DELETE operations since index tables must also be updated.'
        }
    ],
    'AWS': [
        {
            'question': 'Explain the difference between AWS EC2, AWS Lambda, and AWS S3.',
            'answer_guideline': 'EC2 provides virtual servers (IaaS). Lambda is serverless computing that runs code in response to events (FaaS). S3 is object storage (SaaS) for assets and static files.'
        }
    ],
    'Machine Learning': [
        {
            'question': 'What is the bias-variance tradeoff in Machine Learning models?',
            'answer_guideline': 'Bias refers to errors from simple assumptions (underfitting). Variance refers to errors from sensitivity to training noise (overfitting). The goal is an optimal balance minimizing total error.'
        }
    ],
    'Git': [
        {
            'question': 'Describe the differences between git merge and git rebase. When should you use which?',
            'answer_guideline': 'Merge creates a new commit joining history branch timelines together. Rebase reapplies commits on top of another base, keeping a linear commit log. Use merge to preserve history, rebase for cleanup.'
        }
    ]
}

def generate_interview_questions_ai(skills_list, resume_text="", job_desc=""):
    """
    Uses Gemini LLM to generate highly personalized interview practice questions spanning:
    - Technical questions
    - Project-based questions
    - Behavioral questions
    - Resume-specific questions
    - Job-specific questions
    
    Returns list of dicts, or None if API fails.
    """
    if not is_ai_available():
        return None
        
    system_instruction = (
        "You are a Hiring Manager and Technical Recruiter conducting an interview. "
        "Generate realistic, challenging, and personalized interview practice questions based on the candidate's resume and target job description. "
        "Include actionable answer guidelines for every question."
    )
    
    prompt = f"""
CANDIDATE SKILLS:
{', '.join(skills_list[:15]) if skills_list else 'General Software Engineering'}

RESUME TEXT:
{resume_text[:2500] if resume_text else 'Not provided'}

TARGET JOB DESCRIPTION:
{job_desc[:1500] if job_desc else 'Not provided'}

TASK:
Generate 6 to 8 tailored interview questions covering a mix of:
1. Technical Skills
2. Project-based (based on candidate projects)
3. Behavioral / Problem Solving
4. Resume-specific / Job-specific scenarios

Return a JSON array of objects with the following schema:
[
  {{
    "skill": "Category or Target Skill (e.g. Python, React, Project Experience, Behavioral)",
    "question": "The interview question",
    "answer_guideline": "A clear, 2-3 sentence guide on how to answer effectively using the STAR method or technical details"
  }}
]
"""
    result = call_llm_json(prompt, system_instruction=system_instruction)
    if isinstance(result, list) and len(result) > 0:
        #isinstance is python's built in function. 
        #For example:
# if isinstance(result, list):
# This means:
# “Check whether result is a Python list.”
# And:
# if isinstance(q, dict):
# means:
# “Check whether q is a Python dictionary.”
        cleaned_questions = []
        for q in result:
            if isinstance(q, dict) and 'question' in q and 'answer_guideline' in q:
                cleaned_questions.append({
                    'skill': q.get('skill', 'General'),
                    'question': q['question'],
                    'answer_guideline': q['answer_guideline']
                })
        if cleaned_questions:
            return cleaned_questions[:8]
            
    return None
#If Gemini:
# fails
# returns invalid JSON
# returns an empty list
# doesn't provide required fields
# then this function returns None.

def generate_interview_questions(skills_list, resume_text="", job_desc=""):
    """
    Generates interview questions using Gemini LLM if available, falling back to static DB.
    """
    # 1. Attempt Real Gemini AI generation
    ai_questions = generate_interview_questions_ai(skills_list, resume_text, job_desc)
    #We first try the AI version.
    if ai_questions:
        return ai_questions
        
    # 2. Rule-based Fallback
    questions = []
    processed_skills = set()
    #questions stores the final questions.
    #processed_skills keeps track of skills we've already processed so we don't duplicate them.
    
    for skill in skills_list:
        skill_lower = skill.lower()
        matched_key = None
        for key in SKILL_INTERVIEW_DB.keys():
            if key.lower() == skill_lower:
                #checks whether the candidate's skill matches one of our database skills.
                matched_key = key
                break
                
        if matched_key and matched_key not in processed_skills:
            #This ensures we don't process the same skill repeatedly.
            processed_skills.add(matched_key)
            for q_data in SKILL_INTERVIEW_DB[matched_key]:
                questions.append({
                    'skill': matched_key,
                    'question': q_data['question'],
                    'answer_guideline': q_data['answer_guideline']
                })
                
    # Generic fallback if still under 5 questions
    if len(questions) < 5:
        for skill in skills_list:
            if skill not in processed_skills and len(processed_skills) < 5:
                processed_skills.add(skill)
                questions.append({
                    'skill': skill,
                    'question': f"Explain a challenging technical problem you solved using {skill}. What were the key constraints, and how did you resolve them?",
                    'answer_guideline': f"When answering, use the STAR method (Situation, Task, Action, Result). State the problem, how you applied {skill}, alternative solutions evaluated, and final metric/impact."
                })
                
    return questions[:8]


#The interview generator uses a hybrid approach. First, it sends the candidate's skills, resume, and target job description to Gemini to generate 6–8 personalized technical, project-based, behavioral, and job-specific questions with answer guidelines.
#We validate the AI response before using it. If Gemini is unavailable or returns an invalid response, we fall back to our predefined skill-based question database and generic questions, ensuring the interview feature continues to work.