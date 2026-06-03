import os
import json
from io import BytesIO
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_file
from werkzeug.utils import secure_filename

from models import db, Resume, JobDescription, ATSScore, ExtractedSkill, Recommendation, InterviewQuestion
from routes.dashboard import login_required
from config import Config
from utils.file_validator import save_uploaded_file

# AI Engines
from ai_engine.parser import parse_resume
from ai_engine.skill_extractor import extract_skills
from ai_engine.matcher import calculate_semantic_similarity
from ai_engine.keyword_optimizer import optimize_keywords
from ai_engine.ats_score import calculate_ats_score
from ai_engine.analyzer import analyze_resume_quality
from ai_engine.recommendation import recommend_jobs
from ai_engine.interview_generator import generate_interview_questions

# PDF Reporting (ReportLab)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Check files
        if 'resume' not in request.files:
            flash('No resume file selected.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        job_title = request.form.get('job_title', '').strip()
        job_desc = request.form.get('job_description', '').strip()
        
        if not job_title or not job_desc:
            flash('Target Job Title and Job Description are required.', 'danger')
            return redirect(request.url)
            
        # Validate and save resume file
        filename, result = save_uploaded_file(file, Config.UPLOAD_FOLDER, Config.ALLOWED_EXTENSIONS)
        if not filename:
            flash(result, 'danger')
            return redirect(request.url)
            
        file_path = result
        
        try:
            # 1. Parse Resume Text and Structure
            parsed_data = parse_resume(file_path)
            
            # Save Resume model
            new_resume = Resume(
                user_id=session['user_id'],
                filename=filename,
                file_path=file_path,
                parsed_text=parsed_data['parsed_text'],
                name=parsed_data['name'],
                email=parsed_data['email'],
                phone=parsed_data['phone'],
                education=parsed_data['education'],
                experience=parsed_data['experience'],
                projects=parsed_data['projects'],
                certifications=parsed_data['certifications']
            )
            db.session.add(new_resume)
            db.session.flush() # Populate new_resume.id
            
            # Save Target Job Description model
            new_job_desc = JobDescription(
                user_id=session['user_id'],
                title=job_title,
                description_text=job_desc
            )
            db.session.add(new_job_desc)
            db.session.flush()
            
            # 2. Extract and Save Resume Skills
            skills_data = extract_skills(parsed_data['parsed_text'])
            for cat, skills_list in skills_data['categorized'].items():
                for skill_name in skills_list:
                    new_skill = ExtractedSkill(
                        resume_id=new_resume.id,
                        skill_name=skill_name,
                        skill_type=cat
                    )
                    db.session.add(new_skill)
                    
            # 3. Calculate Semantic Similarity
            similarity_score, match_percentage = calculate_semantic_similarity(
                parsed_data['parsed_text'],
                job_desc
            )
            
            # 4. Keyword Optimization and Analysis
            opt_data = optimize_keywords(parsed_data['parsed_text'], job_desc)
            quality_data = analyze_resume_quality(parsed_data)
            
            # Combine standard feedback from ATS score and weak phrase detections
            ats_results = calculate_ats_score(parsed_data, job_desc)
            
            # Inject extra analysis details into JSON feedback
            feedback_dict = json.loads(ats_results['feedback_json'])
            feedback_dict['missing_keywords'] = opt_data['missing']
            feedback_dict['weak_keywords'] = opt_data['weak']
            feedback_dict['recommended_keywords'] = opt_data['recommended']
            feedback_dict['density'] = opt_data['resume_density']
            feedback_dict['density_feedback'] = opt_data['density_feedback']
            feedback_dict['weak_phrases'] = quality_data['weak_phrases_detected']
            feedback_dict['formatting'] = quality_data['formatting_tips']
            feedback_dict['suggestions'] = quality_data['general_suggestions']
            feedback_dict['match_percentage'] = match_percentage
            feedback_dict['similarity_score'] = similarity_score
            
            # Save ATS Score
            new_ats_score = ATSScore(
                resume_id=new_resume.id,
                job_description_id=new_job_desc.id,
                overall_score=ats_results['overall_score'],
                skills_score=ats_results['skills_score'],
                experience_score=ats_results['experience_score'],
                education_score=ats_results['education_score'],
                projects_score=ats_results['projects_score'],
                certifications_score=ats_results['certifications_score'],
                strength_meter=ats_results['strength_meter'],
                feedback_json=json.dumps(feedback_dict)
            )
            db.session.add(new_ats_score)
            
            # 5. Job Recommendations (based on profile mapping)
            recommendations_list = recommend_jobs(parsed_data['parsed_text'])
            for rec in recommendations_list:
                new_rec = Recommendation(
                    resume_id=new_resume.id,
                    job_title=rec['job_title'],
                    match_percentage=rec['match_percentage'],
                    skill_improvements=", ".join(rec['skill_improvements'])
                )
                db.session.add(new_rec)
                
            # 6. Interview Questions Generation
            interview_q_list = generate_interview_questions(skills_data['flat_list'])
            for iq in interview_q_list:
                new_iq = InterviewQuestion(
                    resume_id=new_resume.id,
                    skill=iq['skill'],
                    question=iq['question'],
                    answer_guideline=iq['answer_guideline']
                )
                db.session.add(new_iq)
                
            # Commit all changes to database
            db.session.commit()
            flash('Resume analyzed successfully!', 'success')
            return redirect(url_for('analyze.results', score_id=new_ats_score.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"[ANALYZE ERROR] Pipeline failed: {e}")
            flash(f'An error occurred during analysis: {str(e)}', 'danger')
            return redirect(request.url)
            
    return render_template('analyze.html')

@analyze_bp.route('/analyze/results/<int:score_id>')
@login_required
def results(score_id):
    # Verify score belongs to user
    score_record = ATSScore.query.join(Resume).filter(
        ATSScore.id == score_id, 
        Resume.user_id == session['user_id']
    ).first_or_404()
    
    resume_record = Resume.query.get(score_record.resume_id)
    job_record = JobDescription.query.get(score_record.job_description_id)
    
    # Parse the feedback JSON details
    feedback = json.loads(score_record.feedback_json) if score_record.feedback_json else {}
    
    # Get recommendations and interview questions
    recommendations = Recommendation.query.filter_by(resume_id=resume_record.id).order_by(Recommendation.match_percentage.desc()).all()
    interview_qs = InterviewQuestion.query.filter_by(resume_id=resume_record.id).all()
    
    # Categorize skills for rendering
    skills = ExtractedSkill.query.filter_by(resume_id=resume_record.id).all()
    skills_by_category = {
        'programming_language': [],
        'framework': [],
        'database': [],
        'tool': [],
        'technology': [],
        'soft_skill': []
    }
    for s in skills:
        if s.skill_type in skills_by_category:
            skills_by_category[s.skill_type].append(s.skill_name)
            
    return render_template(
        'results.html',
        score=score_record,
        resume=resume_record,
        job=job_record,
        feedback=feedback,
        recommendations=recommendations,
        interview_qs=interview_qs,
        skills_by_category=skills_by_category
    )

@analyze_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    # Query history of scores
    history_records = db.session.query(ATSScore, Resume, JobDescription).join(
        Resume, ATSScore.resume_id == Resume.id
    ).join(
        JobDescription, ATSScore.job_description_id == JobDescription.id
    ).filter(
        Resume.user_id == user_id
    ).order_by(ATSScore.created_at.desc()).all()
    
    history_data = []
    for score, resume, job in history_records:
        history_data.append({
            'score_id': score.id,
            'filename': resume.filename,
            'job_title': job.title,
            'overall_score': score.overall_score,
            'match_percentage': json.loads(score.feedback_json).get('match_percentage', 0.0) if score.feedback_json else 0.0,
            'strength_meter': score.strength_meter,
            'created_at': score.created_at.strftime('%Y-%m-%d %H:%M')
        })
        
    return render_template('history.html', history=history_data)

@analyze_bp.route('/analyze/report/<int:score_id>')
@login_required
def download_report(score_id):
    # Verify owner
    score_record = ATSScore.query.join(Resume).filter(
        ATSScore.id == score_id, 
        Resume.user_id == session['user_id']
    ).first_or_404()
    
    resume_record = Resume.query.get(score_record.resume_id)
    job_record = JobDescription.query.get(score_record.job_description_id)
    
    feedback = json.loads(score_record.feedback_json) if score_record.feedback_json else {}
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=25
    )
    
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # Header Section
    story.append(Paragraph("Resume Booster ATS Analysis Report", title_style))
    story.append(Paragraph(f"Candidate: {resume_record.name} | Target Position: {job_record.title}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Overall Scores Table
    score_data = [
        [
            Paragraph("<b>Assessment Metric</b>", body_style),
            Paragraph("<b>Score</b>", body_style),
            Paragraph("<b>Weight</b>", body_style)
        ],
        [Paragraph("Overall ATS Score", body_style), f"{score_record.overall_score}%", "100%"],
        [Paragraph("Semantic Job Match", body_style), f"{feedback.get('match_percentage', 0.0)}%", "N/A"],
        [Paragraph("Skills Profile Match", body_style), f"{score_record.skills_score}%", "40%"],
        [Paragraph("Professional Experience", body_style), f"{score_record.experience_score}%", "25%"],
        [Paragraph("Academic Credentials", body_style), f"{score_record.education_score}%", "15%"],
        [Paragraph("Projects & Applications", body_style), f"{score_record.projects_score}%", "10%"],
        [Paragraph("Certifications & Badges", body_style), f"{score_record.certifications_score}%", "10%"]
    ]
    
    t = Table(score_data, colWidths=[250, 100, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#ECFDF5') if score_record.overall_score >= 70 else colors.HexColor('#FFFBEB'))
    ]))
    
    story.append(t)
    story.append(Spacer(1, 20))
    
    # Strengths Summary
    story.append(Paragraph("Resume Strength Meter Summary", section_title))
    strength_desc = f"Your resume has been classified as <b>{score_record.strength_meter}</b> with an overall rating of <b>{score_record.overall_score}%</b>. "
    if score_record.strength_meter == "Excellent":
        strength_desc += "This indicates your experience and skills align exceptionally well with the target role, and the formatting complies with industry standards. You are ready to apply!"
    elif score_record.strength_meter == "Good":
        strength_desc += "Your profile is competitive. By integrating a few of the recommended keywords and polishing weak descriptions, you can further optimize your chance of passing ATS filters."
    else:
        strength_desc += "Significant improvements are recommended. Focus on detailing your experience using impact-driven metrics, incorporating technical keywords, and ensuring your contact details are complete."
        
    story.append(Paragraph(strength_desc, body_style))
    story.append(Spacer(1, 15))
    
    # Section Breakdown Feedback
    story.append(Paragraph("Detailed Section Analysis", section_title))
    
    # Skills feedback
    story.append(Paragraph("<b>1. Skills & Key Terminology</b>", body_style))
    for f in feedback.get('skills', []):
        story.append(Paragraph(f"• {f}", bullet_style))
    story.append(Spacer(1, 8))
        
    # Experience feedback
    story.append(Paragraph("<b>2. Professional Experience</b>", body_style))
    for f in feedback.get('experience', []):
        story.append(Paragraph(f"• {f}", bullet_style))
    story.append(Spacer(1, 8))
    
    # Education feedback
    story.append(Paragraph("<b>3. Education & Credentials</b>", body_style))
    for f in feedback.get('education', []):
        story.append(Paragraph(f"• {f}", bullet_style))
    story.append(Spacer(1, 8))
    
    # Projects feedback
    story.append(Paragraph("<b>4. Projects & Portfolio</b>", body_style))
    for f in feedback.get('projects', []):
        story.append(Paragraph(f"• {f}", bullet_style))
    story.append(Spacer(1, 8))
    
    # Certs feedback
    story.append(Paragraph("<b>5. Professional Certifications</b>", body_style))
    for f in feedback.get('certifications', []):
        story.append(Paragraph(f"• {f}", bullet_style))
        
    story.append(PageBreak()) # Shift optimization details to page 2
    
    # Keyword Optimization details
    story.append(Paragraph("Keyword & ATS Optimization", section_title))
    story.append(Paragraph(feedback.get('density_feedback', ''), body_style))
    story.append(Spacer(1, 10))
    
    missing_kws = feedback.get('missing_keywords', [])
    if missing_kws:
        story.append(Paragraph("<b>Critical Keywords Missing:</b>", body_style))
        story.append(Paragraph("These terms exist in the job description but were not identified on your resume. You should incorporate them naturally.", body_style))
        story.append(Paragraph(", ".join(missing_kws), bullet_style))
        story.append(Spacer(1, 10))
        
    weak_kws = feedback.get('weak_keywords', [])
    if weak_kws:
        story.append(Paragraph("<b>Weak Keyword Presence:</b>", body_style))
        story.append(Paragraph("These terms appear on your resume but have very low density. Ensure they are associated with clear impact statements.", body_style))
        story.append(Paragraph(", ".join(weak_kws), bullet_style))
        story.append(Spacer(1, 10))
        
    # Weak Phrasings
    weak_phrases = feedback.get('weak_phrases', [])
    if weak_phrases:
        story.append(Paragraph("<b>Passive/Weak Expressions Identified:</b>", body_style))
        for wp in weak_phrases:
            story.append(Paragraph(f"• Identified: <i>{wp['snippet']}</i>. <b>Rewrite Recommendation:</b> Use action verbs like <i>'{wp['suggestion']}'</i>. {wp['tip']}", bullet_style))
            
    doc.build(story)
    
    # Send file from buffer
    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True, 
        download_name=f"{secure_filename(resume_record.name)}_ATS_Report.pdf", 
        mimetype='application/pdf'
    )
