import sys
import os

# Set current path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.skill_extractor import extract_skills
from ai_engine.matcher import calculate_semantic_similarity, get_semantic_match_explanation
from ai_engine.keyword_optimizer import optimize_keywords
from ai_engine.ats_score import calculate_ats_score
from ai_engine.analyzer import analyze_resume_quality, rewrite_bullet_point, generate_ai_summary
from ai_engine.interview_generator import generate_interview_questions
from ai_engine.recommendation import recommend_jobs
from ai_engine.llm_client import is_ai_available, call_llm, call_llm_json

# Sample Mock Resume and Job Description for testing
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
Looking for a Senior Python Developer. Must know Django, React, and MySQL database.
Experience with Docker, AWS cloud, and Git is preferred.
Responsible for building microservices and optimizing database performance.
"""

def run_tests():
    print("="*60)
    print("RUNNING RESUME BOOSTER AI ENGINE UNIT & AI INTEGRATION TESTS")
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
    
    # Test 2: Baseline Cosine Similarity
    print("[TEST 2] Testing TF-IDF Cosine Similarity Baseline...")
    sim_score, match_percentage = calculate_semantic_similarity(MOCK_RESUME, MOCK_JOB_DESC)
    print(f"-> Cosine Similarity: {sim_score}")
    print(f"-> Job Match Percentage: {match_percentage}%")
    assert sim_score >= 0.0, "Similarity should be non-negative!"
    print("-> PASS: Baseline similarity calculated successfully!")
    print("-" * 50)
    
    # Test 3: Keyword Optimizer
    print("[TEST 3] Testing Keyword Optimizer...")
    kw_results = optimize_keywords(MOCK_RESUME, MOCK_JOB_DESC)
    print(f"-> Missing Keywords: {kw_results['missing']}")
    assert 'Docker' in kw_results['missing'], "Failed to catch missing Docker!"
    assert 'Aws' in kw_results['missing'], "Failed to catch missing AWS!"
    print("-> PASS: Keyword Optimizer operates correctly!")
    print("-" * 50)
    
    # Test 4: Weighted ATS Score Checker
    print("[TEST 4] Testing Weighted ATS Score Checker...")
    resume_meta = {
        'parsed_text': MOCK_RESUME,
        'experience': "Software Developer at TechCorp - Worked on ML project using Python and Django. Developed frontend UI in React. Leveraged MySQL and Git.",
        'education': "BS in Computer Science State University, 2023",
        'projects': "",
        'certifications': ""
    }
    ats_results = calculate_ats_score(resume_meta, MOCK_JOB_DESC)
    print(f"-> Overall ATS Score: {ats_results['overall_score']}%")
    assert ats_results['overall_score'] > 0.0, "ATS Score should be greater than zero!"
    print("-> PASS: ATS scoring algorithm executed successfully!")
    print("-" * 50)
    
    # Test 5: AI LLM Availability & Fallback Configuration Check
    print("[TEST 5] Testing AI LLM Client Configuration & Fallback Status...")
    ai_status = is_ai_available()
    print(f"-> GEMINI API Configured: {ai_status}")
    print("-> PASS: LLM availability state recognized safely!")
    print("-" * 50)
    
    # Test 6: AI Resume Quality Analysis (With Fallback)
    print("[TEST 6] Testing AI Resume Quality Analysis...")
    quality_res = analyze_resume_quality(resume_meta, MOCK_JOB_DESC)
    assert 'completeness_score' in quality_res, "Missing completeness score!"
    assert 'weak_phrases_detected' in quality_res, "Missing weak phrase list!"
    print(f"-> Completeness Score: {quality_res['completeness_score']}%")
    print(f"-> AI Feedback Present: {quality_res.get('ai_feedback') is not None}")
    print("-> PASS: Resume Quality Analysis executed cleanly!")
    print("-" * 50)
    
    # Test 7: AI Bullet Point Improver (No Fabrication Constraint)
    print("[TEST 7] Testing AI Bullet Point Improver...")
    sample_bullet = "Worked on website using React."
    improved_res = rewrite_bullet_point(sample_bullet, MOCK_JOB_DESC)
    print(f"-> Original: '{improved_res['original']}'")
    print(f"-> Improved: '{improved_res['improved']}'")
    assert improved_res['success'] is True, "Bullet improver should report success!"
    assert len(improved_res['improved']) > 0, "Improved bullet should not be empty!"
    print("-> PASS: Bullet Point Improver completed successfully!")
    print("-" * 50)
    
    # Test 8: AI Professional Summary Generator
    print("[TEST 8] Testing AI Professional Summary Generator...")
    summary = generate_ai_summary(resume_meta, MOCK_JOB_DESC)
    print(f"-> Generated Summary: '{summary}'")
    assert len(summary) > 20, "Generated summary text is too short!"
    print("-> PASS: Professional Summary Generator executed successfully!")
    print("-" * 50)
    
    # Test 9: AI Practice Interview Questions Generator
    print("[TEST 9] Testing Practice Interview Questions Generator...")
    questions = generate_interview_questions(detected_skills, MOCK_RESUME, MOCK_JOB_DESC)
    print(f"-> Generated {len(questions)} questions.")
    for idx, q in enumerate(questions[:2]):
        print(f"   Q{idx+1} ({q['skill']}): {q['question']}")
        print(f"      Guideline: {q['answer_guideline']}")
    assert len(questions) > 0, "No interview questions generated!"
    print("-> PASS: Interview Questions generated successfully!")
    print("-" * 50)
    
    # Test 10: AI Job Recommendations
    print("[TEST 10] Testing Job Recommendations...")
    recommendations = recommend_jobs(MOCK_RESUME, MOCK_JOB_DESC)
    print(f"-> Recommendations count: {len(recommendations)}")
    for r in recommendations[:2]:
        print(f"   Role: {r['job_title']} | Match: {r['match_percentage']}% | Skills: {r['skill_improvements']}")
    assert len(recommendations) > 0, "Failed to suggest job recommendations!"
    print("-> PASS: Job recommendations generated successfully!")
    print("-" * 50)
    
    # Test 11: Chatbot Markdown Formatting
    print("[TEST 11] Testing Chatbot Markdown to HTML Formatter...")
    from routes.chat import format_markdown_to_html
    raw_md = "**Hello Jane!**\nHere are suggestions:\n* Item 1\n* Item 2\n\n### Next Steps"
    html_out = format_markdown_to_html(raw_md)
    print(f"-> HTML Output: {html_out}")
    assert "<b>Hello Jane!</b>" in html_out, "Failed to format bold text!"
    assert "• Item 1" in html_out, "Failed to format bullet item!"
    assert "<b>Next Steps</b>" in html_out, "Failed to format header!"
    print("-> PASS: Chatbot Markdown formatting functions correctly!")
    print("="*60)
    print("ALL 11 TESTS PASSED SUCCESSFULLY! AI ENGINE IS FULLY OPERATIONAL.")
    print("="*60)

if __name__ == '__main__':
    run_tests()
