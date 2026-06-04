
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess_text(text):
    """
    Clean and normalize text before vectorization.
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def calculate_semantic_similarity(resume_text, job_desc_text):
    """
    Calculates similarity between resume and job description
    using TF-IDF vectorization + cosine similarity.
    """

    if not resume_text.strip() or not job_desc_text.strip():
        return 0.0, 0.0

    try:
        # Preprocess texts
        resume_text = preprocess_text(resume_text)
        job_desc_text = preprocess_text(job_desc_text)

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')

        tfidf_matrix = vectorizer.fit_transform([
            resume_text,
            job_desc_text
        ])

        # Calculate cosine similarity
        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        # Convert to percentage
        match_percentage = round(float(similarity * 100), 2)

        return float(similarity), match_percentage

    except Exception as e:
        print(f"[AI ERROR] Similarity calculation failed: {e}")
        return 0.0, 0.0

