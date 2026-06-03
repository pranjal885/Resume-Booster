import re
import json
from ai_engine.skill_extractor import extract_skills

# Strong action verbs favored by ATS systems
ACTION_VERBS = {
    'led', 'managed', 'developed', 'built', 'created', 'designed', 'implemented', 
    'optimized', 'improved', 'increased', 'decreased', 'delivered', 'automated', 
    'engineered', 'spearheaded', 'coordinated', 'achieved', 'launched', 'formulated',
    'established', 'accelerated', 'pioneered', 'restructured', 'maximized', 'generated'
}

def calculate_ats_score(resume_data, job_desc_text):
    """
    Computes overall and section-wise ATS scores based on weighted criteria:
    - Skills Match: 40%
    - Experience: 25%
    - Education: 15%
    - Projects: 10%
    - Certifications: 10%
    
    Returns overall score, section scores, strength meter, and section feedback dictionary.
    """
    feedback = {
        'skills': [],
        'experience': [],
        'education': [],
        'projects': [],
        'certifications': []
    }
    
    # 1. Skills Match Score (40%)
    resume_skills = extract_skills(resume_data.get('parsed_text', ''))['flat_list']
    job_skills = extract_skills(job_desc_text)['flat_list']
    
    if not job_skills:
        # If no skills detected in job description, fall back to default or standard match
        skills_score = 75.0
        feedback['skills'].append("No specific technical skills were detected in the target job description. We scored this section based on a general baseline.")
    else:
        # Calculate how many of the job description skills are in the resume
        matched_skills = [s for s in job_skills if s.lower() in [rs.lower() for rs in resume_skills]]
        skills_score = (len(matched_skills) / len(job_skills)) * 100
        
        # Format skills feedback
        feedback['skills'].append(f"Matched {len(matched_skills)} out of {len(job_skills)} key skills from the job description.")
        missing_skills = [s for s in job_skills if s.lower() not in [rs.lower() for rs in resume_skills]]
        if missing_skills:
            feedback['skills'].append(f"Missing critical skills: {', '.join(missing_skills[:5])}...")
        else:
            feedback['skills'].append("Fantastic! You have listed all key technical skills matching this job description.")

    # 2. Experience Score (25%)
    exp_text = resume_data.get('experience', '')
    if not exp_text or len(exp_text.strip()) < 50:
        experience_score = 0.0
        feedback['experience'].append("CRITICAL: Experience section is missing or extremely short. Recruiters and ATS heavily penalize resumes without a detailed job history.")
    else:
        # Base score based on content depth
        words_count = len(exp_text.split())
        base_exp_score = min(50.0, (words_count / 150.0) * 50.0)  # Ideal length > 150 words
        
        # Action Verbs check
        exp_words = [w.strip(',.()').lower() for w in exp_text.split()]
        found_verbs = [w for w in exp_words if w in ACTION_VERBS]
        verb_bonus = min(25.0, (len(set(found_verbs)) / 5.0) * 25.0)  # Ideal >= 5 unique action verbs
        
        # Quantifiable metrics check (numbers, percentages, $, etc.)
        # Look for numbers or percentages
        metrics_matches = re.findall(r'\b\d+(?:%|\s*percent|\s*k\b|\s*m\b|\s*million|\s*years?\b)?', exp_text)
        # Filter to keep actual percentages/numbers representing impact (e.g. 92%, $10000, 20% speedup)
        impact_metrics = [m for m in metrics_matches if '%' in m or any(term in m.lower() for term in ['k', 'm', 'million'])]
        metrics_bonus = min(25.0, (len(impact_metrics) / 3.0) * 25.0)  # Ideal >= 3 impact metrics
        
        experience_score = base_exp_score + verb_bonus + metrics_bonus
        
        feedback['experience'].append(f"Your experience descriptions contain {len(exp_words)} words.")
        if len(set(found_verbs)) < 3:
            feedback['experience'].append("TIP: Use more strong action verbs (e.g., 'Spearheaded', 'Optimized', 'Automated') to describe your achievements instead of passive descriptions.")
        else:
            feedback['experience'].append(f"Good job! Used {len(set(found_verbs))} strong action verbs to show your proactive contributions.")
            
        if len(impact_metrics) < 2:
            feedback['experience'].append("TIP: Add quantifiable achievements. Use percentages, dollar values, or speed metrics (e.g., 'Reduced loading time by 30%', 'Managed a team of 4') to prove your impact.")
        else:
            feedback['experience'].append(f"Excellent! Detected {len(impact_metrics)} quantifiable metrics representing tangible achievements.")

    # 3. Education Score (15%)
    edu_text = resume_data.get('education', '')
    if not edu_text or len(edu_text.strip()) < 30:
        education_score = 0.0
        feedback['education'].append("CRITICAL: Education section is missing or too brief. Make sure to list your degrees, university name, and graduation year.")
    else:
        # Check for degree keywords
        degree_keywords = [r'bachelor', r'master', r'phd', r'b\.s\b', r'm\.s\b', r'b\.tech', r'm\.tech', r'degree', r'diploma', r'university', r'college', r'school']
        matches = [kw for kw in degree_keywords if re.search(kw, edu_text.lower())]
        
        # If we find at least degree keyword + university keyword, score is high
        if len(matches) >= 2:
            education_score = 100.0
            feedback['education'].append("Your education section is well-structured and clearly details your academic credentials.")
        else:
            education_score = 70.0
            feedback['education'].append("Your education section is present but could be improved. Ensure your full degree names (e.g., 'Bachelor of Science') and college/university names are written clearly.")

    # 4. Projects Score (10%)
    proj_text = resume_data.get('projects', '')
    if not proj_text or len(proj_text.strip()) < 40:
        projects_score = 50.0  # Default baseline if missing but experience is good, or 0 if strictly missing
        if not exp_text:
            projects_score = 0.0
            feedback['projects'].append("CRITICAL: Both Projects and Experience sections are missing. You must add projects or work experience to be considered by ATS.")
        else:
            feedback['projects'].append("TIP: We did not detect a separate 'Projects' section. If you have done academic or personal projects, consider adding them to highlight extra coding experience.")
    else:
        proj_words = len(proj_text.split())
        projects_score = min(100.0, (proj_words / 100.0) * 100.0)  # Ideal length > 100 words
        feedback['projects'].append("Your projects section is present and contains details of your practical work.")
        if proj_words < 80:
            feedback['projects'].append("TIP: Elaborate on your projects. Describe the technology stack used, your specific role, and the final outcome of the project.")

    # 5. Certifications Score (10%)
    cert_text = resume_data.get('certifications', '')
    if not cert_text or len(cert_text.strip()) < 15:
        # If certifications section is empty
        # We check if job description explicitly mentions certifications
        if 'cert' in job_desc_text.lower():
            certifications_score = 30.0
            feedback['certifications'].append("WARNING: The job description mentions certifications, but we didn't find any in your resume. Adding relevant certifications would boost your matching rate.")
        else:
            certifications_score = 60.0
            feedback['certifications'].append("We did not find a separate 'Certifications' section. If you have relevant industry certifications (e.g. AWS, Scrum, Google Cloud), list them to boost credibility.")
    else:
        certifications_score = 100.0
        feedback['certifications'].append("Excellent! Certifications section detected. Having credentials shows continuous learning and specialized knowledge.")

    # 6. Overall Weighted Score calculation
    overall_score = (
        (skills_score * 0.40) +
        (experience_score * 0.25) +
        (education_score * 0.15) +
        (projects_score * 0.10) +
        (certifications_score * 0.10)
    )
    overall_score = round(overall_score, 2)
    
    # Classify overall strength
    if overall_score < 50:
        strength_meter = "Weak"
    elif 50 <= overall_score <= 75:
        strength_meter = "Good"
    else:
        strength_meter = "Excellent"
        
    return {
        'overall_score': overall_score,
        'skills_score': round(skills_score, 2),
        'experience_score': round(experience_score, 2),
        'education_score': round(education_score, 2),
        'projects_score': round(projects_score, 2),
        'certifications_score': round(certifications_score, 2),
        'strength_meter': strength_meter,
        'feedback_json': json.dumps(feedback)
    }
