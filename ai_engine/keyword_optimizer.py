import re
from collections import Counter
from ai_engine.skill_extractor import extract_skills


def preprocess_text(text):
    """
    Basic lightweight preprocessing.
    """

    if not text:
        return []

    # Lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^\w\s\-\+#]', ' ', text)

    # Tokenize
    words = text.split()

    # Simple stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but',
        'in', 'on', 'at', 'to', 'for', 'with',
        'by', 'of', 'from', 'is', 'are',
        'was', 'were', 'be', 'been',
        'have', 'has', 'had',
        'do', 'does', 'did',
        'this', 'that', 'these', 'those',
        'our', 'their', 'your'
    }

    return [
        word for word in words
        if word not in stopwords and len(word) > 2
    ]


def extract_keywords_from_text(text):
    """
    Extract keywords using regex + skill extraction.
    """

    keywords = set()

    # Extract known technical skills
    skills_data = extract_skills(text)

    for skill in skills_data['flat_list']:
        keywords.add(skill.lower())

    # Extract general words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    for word in words:
        keywords.add(word)

    return list(keywords)


def optimize_keywords(resume_text, job_desc_text):
    """
    Compare resume keywords against job description keywords.
    """

    if not resume_text or not job_desc_text:

        return {
            'missing': [],
            'weak': [],
            'recommended': [],
            'resume_density': 0.0,
            'density_feedback': 'No resume text analyzed.'
        }

    # Preprocess
    resume_tokens = preprocess_text(resume_text)
    job_tokens = preprocess_text(job_desc_text)

    # Frequency counts
    resume_freq = Counter(resume_tokens)
    job_freq = Counter(job_tokens)

    # Extract keywords
    resume_keywords = set(
        extract_keywords_from_text(resume_text)
    )

    job_keywords = set(
        extract_keywords_from_text(job_desc_text)
    )

    missing_keywords = []
    weak_keywords = []

    # Check missing and weak keywords
    for keyword in job_keywords:

        if keyword not in resume_keywords:
            missing_keywords.append(keyword)

        else:
            if resume_freq[keyword] <= 1:
                weak_keywords.append(keyword)

    # Sort missing keywords by importance
    missing_keywords.sort(
        key=lambda kw: job_freq.get(kw, 0),
        reverse=True
    )

    # Clean keyword formatting
    def clean_keywords(keyword_list):

        cleaned = []

        for kw in keyword_list:

            formatted = " ".join([
                word.capitalize()
                for word in kw.split()
            ])

            cleaned.append(formatted)

        return list(dict.fromkeys(cleaned))[:15]

    cleaned_missing = clean_keywords(missing_keywords)
    cleaned_weak = clean_keywords(weak_keywords)

    # Calculate keyword density
    skills_found = extract_skills(
        resume_text
    )['flat_list']

    skills_count = 0

    for skill in skills_found:

        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        matches = re.findall(
            pattern,
            resume_text.lower()
        )

        skills_count += len(matches)

    total_words = len(resume_text.split())

    density = (
        (skills_count / total_words) * 100
        if total_words > 0
        else 0.0
    )

    # Density feedback
    if density < 3:

        density_feedback = (
            "Your technical keyword density is low. "
            "Add more relevant technologies and tools."
        )

    elif density <= 12:

        density_feedback = (
            "Great! Your technical keyword density "
            "is well optimized for ATS systems."
        )

    else:

        density_feedback = (
            "Your resume may contain excessive keyword usage. "
            "Avoid keyword stuffing."
        )

    return {
        'missing': cleaned_missing,
        'weak': cleaned_weak,
        'recommended': cleaned_missing[:6],
        'resume_density': round(density, 2),
        'density_feedback': density_feedback
    }

