import re #Used for cleaning the text with regular expressions.
from sklearn.feature_extraction.text import TfidfVectorizer
#This comes from scikit-learn.
#It converts text into numerical vectors using TF-IDF.
#Why numerical? Because computers can't directly calculate mathematical similarity between:
#"Python developer" and "Java developer"
#So we convert text → numbers.
from sklearn.metrics.pairwise import cosine_similarity
#Once the two texts are converted into vectors, this calculates how similar their directions are.


def preprocess_text(text):
    """
    Clean and normalize text before vectorization.
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()
    #This prevents Python and python from being treated differently.

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
    #The similarity calculation is placed inside try.
    #If something goes wrong, the except block will handle it.

        # Preprocess texts
        resume_text = preprocess_text(resume_text)
        job_desc_text = preprocess_text(job_desc_text)

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english')
        #This creates the TF-IDF processor.
        #The important part here is: stop_words='english'
        #It tells scikit-learn to ignore common English words such as:
        #the
        #is
        #a
        #and
        #of
        #to
        #because these words usually don't help much in determining whether a resume matches a job.

        tfidf_matrix = vectorizer.fit_transform([
            resume_text,
            job_desc_text
        ])
        #It converts the two text documents into numerical TF-IDF vectors.

        # Calculate cosine similarity
        similarity = cosine_similarity(
            tfidf_matrix[0:1],#Resume vector
            tfidf_matrix[1:2] #Job-description vector
        )[0][0]
        #The result is a number generally between:
        #0 → completely different
        #1 → very similar
        #For example:
        #0.82
        #means the vectors are quite similar.

        # Convert to percentage
        match_percentage = round(float(similarity * 100), 2)

        return float(similarity), match_percentage

    except Exception as e:
        print(f"[AI ERROR] Similarity calculation failed: {e}")
        return 0.0, 0.0

