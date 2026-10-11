import re
from ai_engine.llm_client import call_llm, call_llm_json, is_ai_available

# Dictionary of weak phrasing to strong achievement-based suggestions (Rule-based fallback)
#Its purpose is to store:
#Weak resume phrases → stronger alternatives + suggestions
WEAK_PHRASE_MAPPINGS = {
    r'\bworked on\b': ( #Find the phrase "worked on" in the resume.
        #The \b basically helps identify the phrase as a whole word/phrase, rather than matching it as part of another word.
        "Developed, engineered, or designed", #This gives stronger alternatives to the weak phrase.
        "Instead of 'Worked on X', use 'Built, engineered, or launched X using [Tech Stack] to achieve [Specific outcome].'"
        #gives the user a suggestion for rewriting the bullet point.
    ),
    r'\bresponsible for\b': (
        "Spearheaded, coordinated, or executed",
        "Instead of 'Responsible for X', write 'Spearheaded X, resulting in [Quantifiable metric].'"
    ),
    r'\bhelped\b': (
        "Collaborated on, facilitated, or supported",
        "Instead of 'Helped with X', use 'Collaborated with a team of N to design and deploy X, accelerating delivery by Y%.'"
    ),
    r'\bassisted\b': (
        "Collaborated on, facilitated, or supported",
        "Instead of 'Assisted with X', use 'Collaborated on X, taking ownership of [Specific module] and optimizing [Performance metric].'"
    ),
    r'\bhandled\b': (
        "Managed, directed, or oversaw",
        "Instead of 'Handled customer calls', write 'Managed a client base of N, maintaining a 98% satisfaction rating.'"
    ),
    r'\bknowledge of\b': (
        "Proficient in, experienced with, or leveraged",
        "Instead of writing 'Knowledge of Python', say 'Leveraged Python to automate database cleaning pipelines, saving 5 hours weekly.'"
    ),
    r'\bduty was to\b': (
        "Oversaw, directed, or spearheaded",
        "Instead of 'My duty was to build APIs', write 'Designed and integrated RESTful APIs supporting 10k+ active users.'"
    )
}

#WEAK_PHRASE_MAPPINGS is our rule-based fallback for the AI bullet improvement feature.
#It detects weak resume phrases and provides stronger achievement-oriented alternatives when Gemini is unavailable.

def analyze_completeness(resume_data):
    """
    Analyzes whether the resume contains all standard parts.
    Returns completeness score (0-100) and missing sections.
    """
    total_components = 8
    present_count = 0 #How many of those 8 components are present?
    missing = [] #This creates an empty list. If something is missing, its name will be added here.
    
    components = { #This creates a dictionary containing the 8 things we want to check.
        'name': ('Name', resume_data.get('name')),
        #means:
# 'name' → internal key
# 'Name' → label we show to the user
# resume_data.get('name') → actual value extracted from the resume
# So if the resume contains:
# Name: Rahul
# then:
# resume_data.get('name') → Rahul
        'email': ('Email Address', resume_data.get('email')),
        'phone': ('Phone Number', resume_data.get('phone')),
        'skills': ('Skills List/Section', resume_data.get('skills_section') or resume_data.get('education')),  # Backup checks
        'education': ('Education History', resume_data.get('education')),
        'experience': ('Professional Experience', resume_data.get('experience')),
        'projects': ('Projects Section', resume_data.get('projects')),
        'certifications': ('Certifications Section', resume_data.get('certifications'))
    }
    
    for key, (label, val) in components.items():
        if val and len(str(val).strip()) > 10:
            #Does this section exist and contain more than 10 characters?
            present_count += 1
        else:
            if key in ['name', 'email', 'phone'] and val and len(str(val).strip()) > 2:
                #For basic personal information, the function uses a smaller minimum length.
                present_count += 1
            else:
                missing.append(label)
                
    completeness_score = int((present_count / total_components) * 100)
    return completeness_score, missing

def check_weak_descriptions(text):
    #Its job is to find weak wording in the resume and create suggestions.
    #It takes:
# text
# which can contain the user's experience or project descriptions.
#Its job is:
#Find weak phrases and suggest stronger alternatives.
    """
    Scans experience and project text for weak phrasing using regex rule-based matching.
    """
    suggestions = [] #This list will store all the suggestions we find.
    if not text:
        return suggestions

    #Loop through our weak-phrase dictionary    
    for pattern, (strong_verb, tip) in WEAK_PHRASE_MAPPINGS.items():
        if re.search(pattern, text.lower()):
            #Does this weak phrase exist in the resume text?
            match = re.search(r'([^.]{0,30}' + pattern + r'[^.]{0,40})', text, re.IGNORECASE)
            #Find the weak phrase along with some surrounding text.
            #For example, if the resume contains:
# Worked on backend APIs using Flask and MySQL.
# Instead of showing only:
# worked on
# the program tries to capture something like:
# Worked on backend APIs using Flask and MySQL
# So the user can see where the weak phrase appeared.
            snippet = match.group(0).strip() if match else ""
            if snippet:
                snippet = f"\"...{snippet}...\""
            else:
                snippet = "your description"
                
            suggestions.append({
                'weak_phrase': pattern.replace(r'\b', ''),
                'snippet': snippet,
                'suggestion': strong_verb,
                'tip': tip
            })
            #This adds a dictionary containing four pieces of information.
            
    return suggestions
#check_weak_descriptions() scans resume experience and project descriptions for predefined weak phrases using regular expressions. 
#It extracts the relevant text and generates stronger wording suggestions. It acts as a rule-based fallback when AI is unavailable.

def get_formatting_tips(resume_data):
    """
    Generates layout and structural formatting suggestions.
    """
    tips = [] #We create an empty list where we'll store the tips.
    raw_text = resume_data.get('parsed_text', '') #This gets the full text extracted from the resume.
    word_count = len(raw_text.split()) #This calculates how many words are in the resume.
    
    if word_count < 200:
        tips.append("Your resume is very short (under 200 words). Expand on your project tech stacks and experience to provide enough content for ATS parsers.")
    elif word_count > 800:
        tips.append("Your resume is quite long (over 800 words). ATS systems and recruiters prefer concise resumes. Try to condense your content to a clean, highly readable format.")
        
    bullets = len(re.findall(r'[\u2022\u2023\u25E6\u2043\u2219\*\-]\s', raw_text)) #Count how many bullet points are present in the resume.
    if bullets < 5:
        tips.append("Incorporate more bullet points to list accomplishments. Walls of text are difficult for human recruiters to skim.")
        
    if not resume_data.get('email'): #Is an email address missing?
        tips.append("Ensure your email address is listed clearly near the top.")
    if not resume_data.get('phone'): #Ensure a contact phone number is present.
        tips.append("Ensure a contact phone number is present.")
        
    return tips

# =========================================================
# AI-POWERED RESUME ANALYSIS & GENERATION (GEMINI LLM)
# =========================================================

def analyze_resume_quality_ai(resume_data, job_desc_text=""):
    #Send the user's resume to Gemini and ask Gemini to evaluate the resume intelligently.
    """
    Calls Google Gemini LLM to analyze the resume contextually.
    Evaluates: overall quality, summary, experience, projects, clarity, grammar, impact, tech relevance, missing info, and actionable feedback.
    
    Returns structured JSON dictionary or None if API fails.
    """
    if not is_ai_available():
        return None
        
    parsed_text = resume_data.get('parsed_text', '') #Get the actual resume text that we want Gemini to analyze.
    if not parsed_text or len(parsed_text.strip()) < 30:
        #Why?
        #Because sending an empty or extremely short resume to Gemini would not give us a meaningful analysis.
        return None
        
    system_instruction = (
        "You are an expert ATS Optimization Coach and Executive Resume Reviewer. "
        "Analyze the provided resume against the target job description carefully. "
        "CRITICAL RULE: Do NOT fabricate or invent experience, companies, metrics, or technologies that are not present. "
        #This is a safety/accuracy instruction.Only use information that actually exists in the candidate's resume.
        "Provide constructive, specific, actionable feedback with concrete 'Good' vs 'Bad' examples based on the candidate's actual text."
    )
    
    prompt = f"""
RESUME TEXT:
{parsed_text[:4000]} 

TARGET JOB DESCRIPTION:
{job_desc_text[:2000] if job_desc_text else "General Software Industry Role"}

TASK:
Analyze the resume and return a valid JSON object with the following keys:
{{
  "overall_summary": "A 2-3 sentence overview of the resume quality and overall alignment.",
  "strengths": ["List 3 specific strengths found in the resume"],
  "weaknesses": ["List 3 specific weak areas in the resume"],
  "impact_analysis": "Feedback on whether project/work descriptions use measurable metrics and results.",
  "clarity_and_grammar": "Feedback on grammar, tone, and readability.",
  "job_relevance": "Evaluation of how well the skills and experience match the target job description.",
  "actionable_improvements": [
    {{
      "section": "Experience / Projects / Summary",
      "issue": "Specific description of what is weak",
      "example_bad": "Original weak phrase from resume",
      "example_good": "Suggested improved phrase based ONLY on facts in the resume"
    }}
  ]
}}
"""
    return call_llm_json(prompt, system_instruction=system_instruction)

def analyze_resume_quality(resume_data, job_desc_text=""):
    #resume_data → information extracted from the resume
    # job_desc_text → optional target job description
    """
    Combines rule-based checks with AI contextual evaluation.
    Always returns a valid dictionary. Uses deterministic logic as fallback.
    """
    completeness, missing_sections = analyze_completeness(resume_data)
    experience_text = resume_data.get('experience', '')
    projects_text = resume_data.get('projects', '')
    combined_body = f"{experience_text}\n{projects_text}"
    
    weak_phrases = check_weak_descriptions(combined_body)
    formatting_tips = get_formatting_tips(resume_data)
    
    general_suggestions = []
    if missing_sections:
        general_suggestions.append(f"Add the following missing sections: {', '.join(missing_sections)}.")
    if len(weak_phrases) > 0:
        general_suggestions.append("Replace passive phrasing ('worked on', 'assisted') with high-impact action verbs.")
    if not re.search(r'\d+%', combined_body):
        general_suggestions.append("Add quantifiable metrics (e.g., 'improved speed by 20%', 'managed $10K budget') to demonstrate business impact.")
        
    if not general_suggestions:
        general_suggestions.append("Great job! Keep refining your bullet points to align with the job description keywords.")
        
    # Attempt Real Gemini AI Analysis
    ai_feedback = analyze_resume_quality_ai(resume_data, job_desc_text)
    
    # Standardize result object
    return {
        'completeness_score': completeness,
        'missing_sections': missing_sections,
        'weak_phrases_detected': weak_phrases,
        'formatting_tips': formatting_tips,
        'general_suggestions': general_suggestions,
        'ai_feedback': ai_feedback  # None if AI unavailable or failed
    }

def rewrite_bullet_point(bullet_text, job_desc="", skills_list=None):
    """
    AI Bullet Point Improver:
    Uses Gemini LLM to rewrite a single resume bullet point.
    
    STRICT RULES:
    - Preserve the original meaning
    - NEVER invent experience, technologies, metrics, or companies
    - Improve grammar, conciseness, action verbs, and job relevance
    - If no metric is present in the original text, DO NOT make up a fake percentage or dollar figure!
    """
    if not bullet_text or not bullet_text.strip():
        return {
            'success': False,
            'original': bullet_text,
            'improved': "",
            'explanation': "Please provide a valid bullet point to improve."
        }
        
    if not is_ai_available():
        # Fallback rewrite using strong action verb replacement
        words = bullet_text.strip().split() #the program breaks the bullet point into individual words.
        improved_fallback = bullet_text.strip()
        if words:
            # Replace common weak initial words
            first_word = words[0].lower()
            verb_map = {
                'worked': 'Engineered', 'responsible': 'Spearheaded', 'helped': 'Collaborated on',
                'assisted': 'Facilitated', 'handled': 'Managed', 'built': 'Developed'
            }
            if first_word in verb_map:
                words[0] = verb_map[first_word]
                improved_fallback = " ".join(words)
                
        return {
            'success': True,
            'original': bullet_text,
            'improved': improved_fallback,
            'explanation': "Rule-based fallback: Upgraded starting action verb. (Set GEMINI_API_KEY for deep AI rewriting)."
        }
        
    system_instruction = (
        "You are an expert resume writer. Rewrite the user's resume bullet point to make it concise, "
        "achievement-oriented, and impactful. "
        "STRICT CONSTRAINT: Do NOT fabricate or invent metrics, numbers, technologies, or job titles not in the input. "
        "If no metric exists, focus on action verbs, clarity, and structural impact."
    )
    #This tells Gemini how to behave while rewriting the bullet.
    
    prompt = f"""
ORIGINAL BULLET POINT:
"{bullet_text.strip()}"

TARGET JOB CONTEXT:
"{job_desc[:500] if job_desc else 'General Engineering/Technology Role'}"

TASK:
Return a JSON object with:
{{
  "improved_bullet": "The rewritten high-impact bullet point", 
  "explanation": "Brief 1-sentence note explaining what was improved (e.g. enhanced action verbs, improved clarity)"
}}
"""
    result_json = call_llm_json(prompt, system_instruction=system_instruction)
    if result_json and 'improved_bullet' in result_json:
    #Did Gemini return something? and Does the returned JSON contain the required improved_bullet field?
        return {
            'success': True,
            'original': bullet_text,
            'improved': result_json['improved_bullet'],
            'explanation': result_json.get('explanation', 'Enhanced structure and action verbs via Gemini AI.')
        }
    else:
        # Fallback if Gemini response is malformed
        return {
            'success': True,
            'original': bullet_text,
            'improved': f"Developed and optimized {bullet_text.strip()}",
            'explanation': "Fallback rewrite applied due to API formatting error."
        }
    #The user provides a bullet point and optionally a target job description. 
    #We send both to Gemini along with strict instructions to preserve the original meaning and never invent metrics or technologies. Gemini returns a structured JSON response containing the improved bullet and an explanation.
    #If Gemini is unavailable, we use a rule-based fallback, so the feature can still work.

def generate_ai_summary(resume_data, job_desc=""):
    """
    AI Professional Summary Generator:
    Generates a concise, 2-4 sentence professional summary customized for the target role
    based ONLY on details found in the resume.
    """
    if not is_ai_available():
        # Fallback: Deterministic summary generation
        name = resume_data.get('name', 'Professional')
        skills = resume_data.get('skills_section', '') or "software engineering and modern technology"
        return (
            f"Results-oriented professional skilled in {skills[:150]}. "
            f"Demonstrated track record of delivering technical solutions, optimizing application performance, "
            f"and collaborating on impactful projects."
        )
        
    parsed_text = resume_data.get('parsed_text', '')
    
    system_instruction = (
        "You are a executive career coach. Generate a compelling, ATS-friendly professional summary (2 to 4 sentences). "
        "CRITICAL RULE: Base the summary ONLY on details present in the candidate's resume text. "
        "Do NOT invent years of experience, degree names, companies, or certifications."
    )
    
    prompt = f"""
CANDIDATE RESUME DETAILS:
{parsed_text[:3500]}

TARGET JOB DESCRIPTION:
{job_desc[:1500] if job_desc else 'General Professional Position'}

TASK:
Write a professional, ATS-optimized 2-4 sentence summary statement highlighting the candidate's background and core skills relative to the target role.
Return ONLY the summary text, no extra commentary or quotes.
"""
    summary = call_llm(prompt, system_instruction=system_instruction)
    if summary:
        # Remove surrounding quotes if model added any
        cleaned = summary.strip().strip('"').strip("'")
        return cleaned
    else:
        # Fallback
        skills = resume_data.get('skills_section', '') or "technical development and domain expertise"
        return f"Dedicated technology professional with expertise in {skills[:150]}. Experienced in building scalable applications and driving project outcomes."
