import re #Used to clean the resume and JD text.
from sklearn.feature_extraction.text import TfidfVectorizer #Used to convert text into numerical vectors based on important words.
from sklearn.metrics.pairwise import cosine_similarity #Used to calculate how similar the two text vectors are.
from ai_engine.llm_client import call_llm, is_ai_available

def preprocess_text(text):
    #This function cleans the text before comparing it.
    """
    Clean and normalize text before vectorization.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text) #remove special characters and replace them with spaces
    text = re.sub(r'\s+', ' ', text).strip() #remoove extra spaces
    return text

def calculate_semantic_similarity(resume_text, job_desc_text):
    """
    Calculates numerical similarity between resume and job description
    using TF-IDF vectorization + Cosine Similarity as the primary baseline.
    
    Returns tuple: (similarity_decimal, match_percentage)
    """
    if not resume_text or not resume_text.strip() or not job_desc_text or not job_desc_text.strip():
        return 0.0, 0.0

    try:
        clean_resume = preprocess_text(resume_text)
        clean_job = preprocess_text(job_desc_text)

        vectorizer = TfidfVectorizer(stop_words='english')
        #This creates a TF-IDF processor.
# What is TF-IDF?
# TF-IDF identifies words that are important in the text.
# For example, common words like:
# the
# is
# and
# a
# are not very useful for matching.
# That's why:
# stop_words='english'
# removes common English words.
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_job])
       #This converts both pieces of text into numbers/vectors.
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        #This calculates how similar the two vectors are.
# The result is generally between:
# 0 → very little similarity
# 1 → very high similarity
# For example:
# 0.72
# means the calculated similarity is 0.72.
        match_percentage = round(float(similarity * 100), 2)
        #Convert to percentage
        return float(similarity), match_percentage

    except Exception as e:
        print(f"[AI ENGINE ERROR] TF-IDF Similarity calculation failed: {e}")
        return 0.0, 0.0

def get_semantic_match_explanation(resume_text, job_desc_text):
    """
    AI Semantic Match Explainer:
    Uses Gemini LLM to explain how resume concepts match the job description
    (e.g., recognizing that 'Spring Boot REST APIs' matches 'Java backend development').
    """
    if not is_ai_available():
        return "TF-IDF keyword baseline similarity evaluated."
        
    system_instruction = (
        "You are an AI Job Matching Specialist. Analyze how the candidate's experience and skills "
        "conceptually relate to the target job description. Focus on semantic equivalence "
        "(e.g. Spring Boot <-> Java backend, React <-> Frontend UI)."
    )
    
    prompt = f"""
RESUME HIGHLIGHTS:
{resume_text[:2000]}

TARGET JOB DESCRIPTION:
{job_desc_text[:1500]}

TASK:
Provide a concise, 2-sentence explanation of how well the candidate's domain experience matches the job description conceptually.
Highlight matched equivalent tech stacks.
"""
    explanation = call_llm(prompt, system_instruction=system_instruction)
    return explanation.strip() if explanation else "Semantic concepts evaluated against target role."


#I use TF-IDF with cosine similarity as the numerical baseline for resume-JD matching, and Gemini AI separately provides a human-readable semantic explanation of the match.