import re

# Dictionary of weak phrasing to strong achievement-based suggestions
WEAK_PHRASE_MAPPINGS = {
    r'\bworked on\b': (
        "Developed, engineered, or designed",
        "Instead of 'Worked on X', use 'Built, engineered, or launched X using [Tech Stack] to achieve [Specific outcome].'"
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

def analyze_completeness(resume_data):
    """
    Analyzes whether the resume contains all standard parts.
    Returns completeness score (0-100) and missing sections.
    """
    total_components = 8
    present_count = 0
    missing = []
    
    components = {
        'name': ('Name', resume_data.get('name')),
        'email': ('Email Address', resume_data.get('email')),
        'phone': ('Phone Number', resume_data.get('phone')),
        'skills': ('Skills List/Section', resume_data.get('skills_section') or resume_data.get('education')),  # Backup checks
        'education': ('Education History', resume_data.get('education')),
        'experience': ('Professional Experience', resume_data.get('experience')),
        'projects': ('Projects Section', resume_data.get('projects')),
        'certifications': ('Certifications Section', resume_data.get('certifications'))
    }
    
    # If the user has fields in database model
    for key, (label, val) in components.items():
        if val and len(str(val).strip()) > 10:
            present_count += 1
        else:
            # Name and contact details can be shorter
            if key in ['name', 'email', 'phone'] and val and len(str(val).strip()) > 2:
                present_count += 1
            else:
                missing.append(label)
                
    completeness_score = int((present_count / total_components) * 100)
    return completeness_score, missing

def check_weak_descriptions(text):
    """
    Scans experience and project text for weak phrasing.
    Returns a list of specific rewrites and replacement suggestions.
    """
    suggestions = []
    if not text:
        return suggestions
        
    for pattern, (strong_verb, tip) in WEAK_PHRASE_MAPPINGS.items():
        if re.search(pattern, text.lower()):
            # Find a short snippet containing the weak phrase to show the user
            match = re.search(r'([^.]{0,30}' + pattern + r'[^.]{0,40})', text, re.IGNORECASE)
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
            
    return suggestions

def get_formatting_tips(resume_data):
    """
    Generates layout and structural formatting suggestions.
    """
    tips = []
    
    # Text length checks
    raw_text = resume_data.get('parsed_text', '')
    word_count = len(raw_text.split())
    
    if word_count < 200:
        tips.append("Your resume is very short (under 200 words). Expand on your project tech stacks and experience to provide enough content for ATS parsers.")
    elif word_count > 800:
        tips.append("Your resume is quite long (over 800 words). ATS systems and recruiters prefer concise resumes. Try to condense your content to a clean, highly readable single-page or two-page format.")
        
    # Check bullet point counts (bullet points are favored for readability)
    bullets = len(re.findall(r'[\u2022\u2023\u25E6\u2043\u2219\*\-]\s', raw_text))
    if bullets < 5:
        tips.append("Incorporate more bullet points to list accomplishments. Walls of text are difficult for human recruiters to skim and can throw off parsing algorithms.")
        
    # Check email and phone formatting
    if not resume_data.get('email'):
        tips.append("Ensure your email address is listed clearly near the top. Use a professional format (e.g. firstname.lastname@email.com).")
    if not resume_data.get('phone'):
        tips.append("Ensure a contact phone number is present so hiring managers can reach you.")
        
    return tips

def analyze_resume_quality(resume_data):
    """
    Combines completeness, phrasing, and formatting checks to yield structured suggestions.
    """
    completeness, missing_sections = analyze_completeness(resume_data)
    
    # Check weak terms in experience and projects
    experience_text = resume_data.get('experience', '')
    projects_text = resume_data.get('projects', '')
    combined_body = f"{experience_text}\n{projects_text}"
    
    weak_phrases = check_weak_descriptions(combined_body)
    formatting_tips = get_formatting_tips(resume_data)
    
    # General recommendations
    general_suggestions = []
    if missing_sections:
        general_suggestions.append(f"Add the following missing sections: {', '.join(missing_sections)}.")
    if len(weak_phrases) > 0:
        general_suggestions.append("Replace passive phrasing ('worked on', 'assisted') with high-impact action verbs.")
    if not re.search(r'\d+%', combined_body):
        general_suggestions.append("Add quantifiable metrics (e.g., 'improved speed by 20%', 'managed $10K budget') to demonstrate business impact.")
        
    # Ensure there are always default constructive tips
    if not general_suggestions:
        general_suggestions.append("Great job! Keep refining your bullet points to align with the job description keywords.")
        
    return {
        'completeness_score': completeness,
        'missing_sections': missing_sections,
        'weak_phrases_detected': weak_phrases,
        'formatting_tips': formatting_tips,
        'general_suggestions': general_suggestions
    }
