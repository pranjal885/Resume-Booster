import sys
import os

# Set current path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.skill_extractor import extract_skills
from ai_engine.matcher import calculate_semantic_similarity
from ai_engine.keyword_optimizer import optimize_keywords
from ai_engine.ats_score import calculate_ats_score
from ai_engine.interview_generator import generate_interview_questions
from ai_engine.recommendation import recommend_jobs

# Sample Mock Resume and Job Description for pipeline checking
MOCK_RESUME = """
Jane Doe
Email: jane.doe@example.com | Phone: +1-555-0199
SUMMARY
Ambitious Full Stack Engineer with 3 years of experience. Experienced in building web apps.

EXPERIENCE
Software Developer at TechCorp (2024 - Present)
- Worked on ML project using Python and Django.
- Developed frontend UI in React and Javascript.
- Leveraged MySQL and Git.
- Responsible for database optimization.

EDUCATION
BS in Computer Science
State University, 2023
"""

MOCK_JOB_DESC = """
Looking for a Python Developer. Must know Django, React, and MySQL database.
Experience with Docker, AWS cloud, and Git is preferred.
Responsible for building microservices and optimizing database performance.
"""

def run_tests():
    print("="*60)
    print("RUNNING RESUME BOOSTER AI ENGINE UNIT TESTS")
    print("="*60)
    
    # Test 1: Skill Extraction
    print("[TEST 1] Testing Skill Extraction Engine...")
    skills_data = extract_skills(MOCK_RESUME)
    detected_skills = skills_data['flat_list']
    print(f"-> Extracted Skills: {detected_skills}")
    assert 'Python' in detected_skills, "Failed to detect Python!"
    assert 'React' in detected_skills, "Failed to detect React!"
    assert 'MySQL' in detected_skills, "Failed to detect MySQL!"
    print("-> PASS: Skill Extraction behaves correctly!")
    print("-" * 50)
    
    # Test 2: Semantic Matcher (Sentence Transformers)
    print("[TEST 2] Testing Semantic Cosine Similarity...")
    sim_score, match_percentage = calculate_semantic_similarity(MOCK_RESUME, MOCK_JOB_DESC)
    print(f"-> Cosine Similarity: {sim_score}")
    print(f"-> Job Match Percentage: {match_percentage}%")
    assert sim_score >= 0.0, "Similarity should be non-negative!"
    print("-> PASS: Semantic Similarity calculated successfully!")
    print("-" * 50)
    
    # Test 3: Keyword Optimizer
    print("[TEST 3] Testing Keyword Optimizer...")
    kw_results = optimize_keywords(MOCK_RESUME, MOCK_JOB_DESC)
    print(f"-> Missing Keywords: {kw_results['missing']}")
    print(f"-> Weak Keywords: {kw_results['weak']}")
    print(f"-> Density: {kw_results['resume_density']}%")
    # Docker and AWS are in job desc but not mock resume
    assert 'Docker' in kw_results['missing'], "Failed to catch missing Docker!"
    assert 'Aws' in kw_results['missing'], "Failed to catch missing AWS!"
    print("-> PASS: Keyword Optimizer detects missing and weak keywords successfully!")
    print("-" * 50)
    
    # Test 4: Weighted ATS Score Checker
    print("[TEST 4] Testing Weighted ATS Score Checker...")
    resume_meta = {
        'parsed_text': MOCK_RESUME,
        'experience': "Software Developer at TechCorp (2024 - Present) - Worked on ML project using Python and Django. Developed frontend UI in React and Javascript. Leveraged MySQL and Git. Responsible for database optimization.",
        'education': "BS in Computer Science State University, 2023",
        'projects': "",
        'certifications': ""
    }
    ats_results = calculate_ats_score(resume_meta, MOCK_JOB_DESC)
    print(f"-> Overall ATS Score: {ats_results['overall_score']}%")
    print(f"-> Skills Section Score: {ats_results['skills_score']}%")
    print(f"-> Experience Section Score: {ats_results['experience_score']}%")
    print(f"-> Strength: {ats_results['strength_meter']}")
    assert ats_results['overall_score'] > 0.0, "ATS Score should be greater than zero!"
    print("-> PASS: ATS scoring algorithm executed successfully!")
    print("-" * 50)
    
    # Test 5: Interview Questions Generator
    print("[TEST 5] Testing Interview Practice Questions Generator...")
    questions = generate_interview_questions(detected_skills)
    print(f"-> Generated {len(questions)} questions.")
    for idx, q in enumerate(questions[:3]):
        print(f"   Q{idx+1} ({q['skill']}): {q['question']}")
    assert len(questions) > 0, "No questions were generated!"
    print("-> PASS: Interview Questions generated successfully!")
    print("-" * 50)
    
    # Test 6: Job Recommendations
    print("[TEST 6] Testing Job Recommendations...")
    recommendations = recommend_jobs(MOCK_RESUME)
    print(f"-> Recommendations generated: {[r['job_title'] for r in recommendations]}")
    assert len(recommendations) > 0, "Failed to suggest jobs!"
    print("-> PASS: Job recommendations mapped successfully!")
    print("="*60)
    print("ALL TESTS PASSED SUCCESSFULLY! AI PIPELINE IS STABLE.")
    print("="*60)

if __name__ == '__main__':
    run_tests()
