# Resume Booster 🚀

An AI-powered Resume Analysis and ATS Optimization Platform built using Flask, Python, NLP, and Google Gemini AI.

## 📌 Overview

Resume Booster helps users analyze and improve their resumes for Applicant Tracking Systems (ATS) and job applications.

The platform evaluates resume quality, identifies missing skills and keywords, compares resumes with job descriptions, and provides personalized recommendations. With Google Gemini AI integration, it also generates resume improvements, professional summaries, interview questions, job role recommendations, and contextual resume guidance through an AI chatbot.

The application combines rule-based analysis and traditional NLP techniques with generative AI to provide useful results, while retaining fallback functionality when AI services are unavailable.

## ✨ Features

### ✅ ATS Resume Analysis
- Calculates an ATS compatibility score.
- Evaluates resume content and keyword relevance.
- Identifies areas that need improvement.
- Provides resume quality feedback.

### ✅ Resume–Job Description Matching
- Uses TF-IDF and cosine similarity to calculate a match score.
- Compares resume content with a target job description.
- Uses Gemini AI to explain the match and suggest improvements.

### ✅ AI-Powered Resume Improvement
- Analyzes resume quality using Gemini AI.
- Improves resume bullet points with clearer, more professional wording.
- Generates professional resume summaries.
- Provides actionable suggestions for enhancing resume content.

### ✅ Skill Gap Analysis
- Extracts and categorizes skills from resume content.
- Identifies relevant missing skills.
- Helps users understand which skills may need improvement for a target role.

### ✅ Job Role Recommendations
- Recommends suitable job roles based on resume skills and experience.
- Uses AI to generate personalized recommendations.
- Provides fallback recommendations when AI is unavailable.

### ✅ Interview Preparation
- Generates personalized interview questions based on resume information and skills.
- Helps users prepare for interviews related to their profiles.
- Includes fallback question sets when AI services are unavailable.

### ✅ AI Resume Coach
- Provides an interactive chatbot for resume-related guidance.
- Uses resume and job-related context when available.
- Answers relevant career and resume questions.
- Includes fallback handling for unavailable AI services.

## 🧠 AI and NLP Workflow

The application combines traditional NLP methods, rule-based logic, and generative AI.

1. Resume upload and text extraction.
2. Resume parsing and skill extraction.
3. ATS and resume quality analysis.
4. TF-IDF and cosine similarity for job matching.
5. Gemini AI analysis and personalized suggestions.
6. AI-generated summaries, improved bullet points, interview questions, and job recommendations.
7. Results displayed through the web interface.

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

### Backend
- Python
- Flask
- Flask Blueprints

### AI and NLP
- Google Gemini API
- TF-IDF
- Cosine Similarity
- scikit-learn and other project-specific NLP libraries

### Database
- SQLite
- MySQL support
- Flask-SQLAlchemy

### Tools and Libraries
- Python-dotenv for environment configuration
- PDF processing libraries used by the project
- PyMySQL for MySQL connectivity

## 📂 Project Structure

```text
Resume-Booster/
├── ai_engine/
│   ├── llm_client.py
│   ├── analyzer.py
│   ├── interview_generator.py
│   ├── matcher.py
│   └── recommendation.py
├── models/
├── routes/
│   ├── analyze.py
│   ├── auth.py
│   └── chat.py
├── static/
├── templates/
├── config.py
├── app.py
├── requirements.txt
├── .env.example
├── test_ai_engine.py
└── README.md
```

*Note: This is a representative structure. Keep only files and folders that exist in your current repository.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/pranjal885/Resume-Booster.git
cd Resume-Booster
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Environment

**Windows**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file using `.env.example` as a reference.

Configure the Gemini API key and model, along with the database settings supported by your application.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash

DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=resume_booster
```

Use your actual environment variable names from `llm_client.py` and `config.py`. Never commit your real API key or other secrets to GitHub.

When `DB_USER` is empty, the current configuration selects SQLite. When valid MySQL settings are provided, the application attempts to connect to MySQL and falls back to SQLite if the connection fails.

### 6. Run the Application

```bash
python app.py
```

Open the local URL displayed in the terminal.

## 🧪 Testing

Run the AI engine tests with:

```bash
python -m pytest test_ai_engine.py -v
```

The test suite checks the AI engine functionality covered by the project tests. Live Gemini requests may depend on API quota and network availability.

## 🛡️ Reliability and Fallback Handling

- Uses a centralized AI client for Gemini API calls.
- Handles unavailable AI services through fallback logic where implemented.
- Combines AI-generated output with traditional scoring and matching techniques.
- Keeps API credentials in environment variables rather than source code.

## 🚀 Future Improvements

- Export improved resumes as downloadable PDFs.
- Add more advanced resume–job matching.
- Expand resume templates and formatting options.
- Improve multi-resume comparison.
- Enhance deployment and scalability.

## 🎯 Learning Outcomes

Through this project, I explored:

- Full-stack web application development using Flask.
- Integration of Google Gemini AI into an existing application.
- Prompt-based generation of structured and natural-language responses.
- Resume analysis and ATS optimization.
- TF-IDF and cosine similarity for text matching.
- Database integration using Flask-SQLAlchemy.
- API error handling and fallback mechanisms.
- Testing and maintaining an AI-powered application.

## 👨‍💻 Author

**Pranjal Patil**

GitHub: [pranjal885](https://github.com/pranjal885)

---

⭐ If you find this project useful, consider giving it a star!
