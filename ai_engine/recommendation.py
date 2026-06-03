from ai_engine.skill_extractor import extract_skills

# Standard industry roles with their typical required skill profiles
JOB_PROFILES = [
    {
        'title': 'Full Stack Developer',
        'required_skills': ['Python', 'JavaScript', 'React', 'HTML', 'CSS', 'Node.js', 'Flask', 'MySQL', 'Git', 'Docker', 'REST API'],
        'description': 'Develop and maintain end-to-end web applications, integrating elegant client UIs with scalable backend services and databases.'
    },
    {
        'title': 'Data Scientist / ML Engineer',
        'required_skills': ['Python', 'Machine Learning', 'Deep Learning', 'SQL', 'Pandas', 'NumPy', 'scikit-learn', 'TensorFlow', 'PyTorch', 'NLP', 'Data Science'],
        'description': 'Design, train, and deploy predictive models and deep learning solutions to extract valuable business insights and automate decision pipelines.'
    },
    {
        'title': 'DevOps Engineer',
        'required_skills': ['Docker', 'Kubernetes', 'AWS', 'Linux', 'CI/CD', 'GitHub Actions', 'Jenkins', 'Terraform', 'Nginx', 'Git', 'Bash'],
        'description': 'Architect and automate cloud infrastructure, continuous deployment pipelines, and system monitoring tools to ensure high availability.'
    },
    {
        'title': 'Frontend Engineer',
        'required_skills': ['JavaScript', 'TypeScript', 'React', 'HTML', 'CSS', 'Tailwind CSS', 'Bootstrap', 'Git', 'Yarn', 'Vite'],
        'description': 'Implement interactive interfaces and responsive layouts, translating design mockups into pixel-perfect web application screens.'
    },
    {
        'title': 'Backend Engineer',
        'required_skills': ['Python', 'SQL', 'PostgreSQL', 'MySQL', 'Node.js', 'Express.js', 'REST API', 'Docker', 'AWS', 'Microservices', 'Git'],
        'description': 'Architect server-side logic, optimize database engines, structure microservices, and deploy secure APIs for web and mobile clients.'
    },
    {
        'title': 'Mobile App Developer',
        'required_skills': ['Dart', 'Flutter', 'React Native', 'Swift', 'Kotlin', 'REST API', 'Firebase', 'Git'],
        'description': 'Build high-performance, native and cross-platform mobile apps for Android and iOS devices, ensuring smooth offline capabilities.'
    }
]

def recommend_jobs(resume_text):
    """
    Compares resume skills against JOB_PROFILES.
    Returns a sorted list of recommended jobs with matching percentages and suggested improvements.
    """
    if not resume_text:
        return []
        
    extracted_skills_data = extract_skills(resume_text)
    user_skills = {s.lower() for s in extracted_skills_data['flat_list']}
    
    recommendations = []
    
    for profile in JOB_PROFILES:
        req_skills_lower = {s.lower() for s in profile['required_skills']}
        
        # Calculate intersection
        matched = req_skills_lower.intersection(user_skills)
        missing = req_skills_lower.difference(user_skills)
        
        # Match percentage calculation
        if req_skills_lower:
            match_percentage = (len(matched) / len(req_skills_lower)) * 100
        else:
            match_percentage = 0.0
            
        # Map missing lowercased skills back to their display names
        missing_display = []
        for s in profile['required_skills']:
            if s.lower() in missing:
                missing_display.append(s)
                
        # Calculate suggested skill improvements (e.g. top 4 missing skills)
        skill_improvements = missing_display[:4]
        
        recommendations.append({
            'job_title': profile['title'],
            'description': profile['description'],
            'match_percentage': round(match_percentage, 2),
            'skill_improvements': skill_improvements
        })
        
    # Sort recommendations by match percentage (descending)
    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return recommendations
