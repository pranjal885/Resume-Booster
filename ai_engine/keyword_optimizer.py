import re
from collections import Counter
import spacy
from ai_engine.skill_extractor import extract_skills

_nlp = None

def get_nlp():
    """
    Loads and caches the spaCy en_core_web_sm model.
    """
    global _nlp
    if _nlp is None:
        try:
            print("[AI INFO] Loading spaCy 'en_core_web_sm' model...")
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("[AI WARNING] spaCy model 'en_core_web_sm' not found. Falling back to basic preprocessing.")
    return _nlp

def preprocess_text(text):
    """
    Tokenizes, lowercases, removes stopwords/punctuation, and lemmatizes text using spaCy.
    """
    if not text:
        return []
        
    nlp = get_nlp()
    if nlp:
        doc = nlp(text.lower())
        tokens = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space and not token.like_num:
                # Store lemmatized forms
                tokens.append(token.lemma_)
        return tokens
    else:
        # Fallback basic preprocessing
        # Remove punctuation and split on whitespace
        clean_text = re.sub(r'[^\w\s\-\+#]', '', text.lower())
        words = clean_text.split()
        # Simple stop words list
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of', 'at', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'as', 'about', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'our', 'their', 'will', 'would', 'can', 'could', 'should', 'with'}
        return [w for w in words if w not in stopwords]

def extract_keywords_from_text(text):
    """
    Extracts key concepts, nouns, and skills from a text using spaCy.
    """
    keywords = set()
    
    # 1. Extract skills from vocabulary
    skills_data = extract_skills(text)
    for skill in skills_data['flat_list']:
        keywords.add(skill.lower())
        
    # 2. Extract Noun Chunks and Nouns using spaCy
    nlp = get_nlp()
    if nlp:
        doc = nlp(text)
        # Noun chunks are often descriptive compound nouns like "web application" or "machine learning"
        for chunk in doc.noun_chunks:
            # Exclude long chunks and sanitize
            chunk_text = chunk.text.strip().lower()
            # If chunk is 1 to 3 words
            if len(chunk_text.split()) <= 3 and not any(char.isdigit() for char in chunk_text):
                # Remove stopwords inside the chunk if any
                clean_chunk = " ".join([t.text for t in nlp(chunk_text) if not t.is_stop])
                if len(clean_chunk) > 2:
                    keywords.add(clean_chunk)
                    
        # Also extract individual proper nouns (PROPN) or nouns (NOUN)
        for token in doc:
            if token.pos_ in {'PROPN', 'NOUN'} and not token.is_stop:
                word = token.text.strip().lower()
                if len(word) > 2 and not word.isdigit():
                    keywords.add(word)
    else:
        # Heuristic fallback: split by non-alphanumeric and keep words > 3 chars
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords.update(words)
        
    return list(keywords)

def optimize_keywords(resume_text, job_desc_text):
    """
    Compares resume keywords against job description keywords.
    Returns lists of:
      - missing_keywords (high importance in job description but absent in resume)
      - weak_keywords (present in resume but very low density / count)
      - recommended_keywords (missing keywords ranked by importance)
      - density metrics
    """
    if not resume_text or not job_desc_text:
        return {
            'missing': [],
            'weak': [],
            'recommended': [],
            'resume_density': 0.0,
            'density_feedback': 'No resume text analyzed.'
        }
        
    # Preprocess text to lists of lemmas/tokens for density counting
    resume_tokens = preprocess_text(resume_text)
    job_tokens = preprocess_text(job_desc_text)
    
    # Count frequencies
    resume_freq = Counter(resume_tokens)
    job_freq = Counter(job_tokens)
    
    # Extract structural keywords
    resume_keywords_raw = extract_keywords_from_text(resume_text)
    job_keywords_raw = extract_keywords_from_text(job_desc_text)
    
    # We will normalize words to match
    resume_keywords_set = {k.lower() for k in resume_keywords_raw}
    job_keywords_set = {k.lower() for k in job_keywords_raw}
    
    # Find missing keywords
    missing_keywords = []
    weak_keywords = []
    
    # Check each job keyword in the resume
    for kw in job_keywords_set:
        # Check if matched directly or as substring
        is_missing = True
        for r_kw in resume_keywords_set:
            if kw == r_kw or (len(kw) > 3 and kw in r_kw) or (len(r_kw) > 3 and r_kw in kw):
                is_missing = False
                break
                
        if is_missing:
            # Check if this keyword is genuinely in the job description tokens
            # Or if it's a multi-word phrase check if parts exist
            missing_keywords.append(kw)
        else:
            # If present, check frequency of tokens in resume
            # If the keyword consists of multiple words, check individual words
            kw_words = kw.split()
            low_density = True
            for word in kw_words:
                # If any word in the phrase appears more than 2 times, it's not weak
                if resume_freq[word] > 1:
                    low_density = False
                    break
            if low_density:
                weak_keywords.append(kw)
                
    # Sort missing keywords by frequency in job description (higher frequency = more important)
    def get_job_importance(keyword):
        words = keyword.split()
        if not words:
            return 0
        return sum(job_freq[w] for w in words)
        
    missing_keywords.sort(key=get_job_importance, reverse=True)
    
    # Clean lists to look professional (e.g. capitalize)
    def clean_keyword_list(kw_list):
        cleaned = []
        for kw in kw_list:
            # If it's a known skill, format nicely
            # Capitalize each word otherwise
            cleaned.append(kw.title())
        return list(set(cleaned))[:15]  # Limit to top 15
        
    cleaned_missing = clean_keyword_list(missing_keywords)
    cleaned_weak = clean_keyword_list(weak_keywords)
    
    # Density check (ratio of technical skills tokens to total tokens)
    skills_in_resume = extract_skills(resume_text)['flat_list']
    skills_tokens_count = 0
    for skill in skills_in_resume:
        # Count occurrences of the skill in resume
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        matches = re.findall(pattern, resume_text.lower())
        skills_tokens_count += len(matches)
        
    total_words = len(resume_text.split())
    density = (skills_tokens_count / total_words * 100) if total_words > 0 else 0.0
    
    if density < 3.0:
        density_feedback = "Your technical keyword density is very low (less than 3%). Add more relevant technologies, frameworks, and programming languages mentioned in the job description to pass automated ATS filters."
    elif 3.0 <= density <= 12.0:
        density_feedback = "Perfect! Your technical keyword density is optimal (between 3% and 12%). This is highly favored by ATS scanners without appearing stuffed."
    else:
        density_feedback = "Your technical keyword density is high (over 12%). Avoid keyword stuffing or simply listing technologies without context. Ensure your skills are woven naturally into your project and experience sections."
        
    return {
        'missing': cleaned_missing,
        'weak': cleaned_weak,
        'recommended': cleaned_missing[:6],  # Suggest top 6 missing keywords
        'resume_density': round(density, 2),
        'density_feedback': density_feedback
    }
