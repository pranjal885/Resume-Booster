import numpy as np
from sentence_transformers import SentenceTransformer

# Cache the model in memory to avoid reloading it on every request
_model = None

def get_model():
    """
    Loads and caches the SentenceTransformer model.
    """
    global _model
    if _model is None:
        print("[AI INFO] Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
        # This will download the model to the local machine on first run
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def calculate_semantic_similarity(resume_text, job_desc_text):
    """
    Calculates semantic cosine similarity between resume text and target job description.
    Formula: cos(theta) = (A . B) / (||A|| ||B||)
    """
    if not resume_text.strip() or not job_desc_text.strip():
        return 0.0, 0.0
        
    try:
        model = get_model()
        
        # Generate embeddings
        embeddings = model.encode([resume_text, job_desc_text])
        emb_resume = embeddings[0]
        emb_job = embeddings[1]
        
        # Calculate dot product
        dot_product = np.dot(emb_resume, emb_job)
        
        # Calculate norms
        norm_resume = np.linalg.norm(emb_resume)
        norm_job = np.linalg.norm(emb_job)
        
        if norm_resume == 0.0 or norm_job == 0.0:
            return 0.0, 0.0
            
        cosine_similarity = dot_product / (norm_resume * norm_job)
        
        # Normalize similarity: Cosine similarity for these embeddings is typically 0 to 1
        # Let's map it to percentage (0 - 100)
        similarity_score = float(cosine_similarity)
        
        # Match percentage can be calculated or adjusted slightly for user display
        # A raw cosine similarity of 0.4 with MiniLM often indicates a moderate match.
        # Let's scale it slightly to feel natural as a Job Match percentage (e.g. 0.3 -> 30%, 0.7 -> 90%)
        # But keeping it mathematically grounded.
        match_percentage = max(0.0, min(100.0, similarity_score * 100))
        
        return similarity_score, round(match_percentage, 2)
        
    except Exception as e:
        print(f"[AI ERROR] Sentence Transformer matching failed: {e}")
        return 0.0, 0.0
