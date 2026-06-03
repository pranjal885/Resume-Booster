# Dictionary of pre-defined interview questions and answer guidelines for standard skills
SKILL_INTERVIEW_DB = {
    'Python': [
        {
            'question': 'What is the difference between a list and a tuple in Python? When would you choose one over the other?',
            'answer_guideline': 'Lists are mutable (can be changed), while tuples are immutable (cannot be changed). Tuples are slightly faster and occupy less memory. Use tuples for fixed data structures (e.g. coordinates or configuration) to protect data integrity, and lists for dynamic collections.'
        },
        {
            'question': 'Explain Python list comprehensions and how they differ from standard for-loops.',
            'answer_guideline': 'List comprehensions provide a concise way to create lists. They are generally faster because they are optimized in C under the hood. Avoid nested or overly complex list comprehensions, as they reduce code readability.'
        }
    ],
    'JavaScript': [
        {
            'question': 'Explain the difference between event bubble propagation and event capturing in JavaScript.',
            'answer_guideline': 'In bubbling, the event starts from the target element and bubbles up to the window. In capturing, the event goes down from the window to the target. Standard event listeners use bubbling by default.'
        },
        {
            'question': 'What are closures in JavaScript, and what is their practical use case?',
            'answer_guideline': 'A closure is the combination of a function bundled together with references to its surrounding state (lexical environment). Closures allow functions to have "private" variables or maintain state between invocations.'
        }
    ],
    'React': [
        {
            'question': 'What are React Hooks? Explain useState and useEffect with examples.',
            'answer_guideline': 'Hooks let functional components manage state and lifecycle side-effects. useState declares a state variable, and useEffect handles operations like fetching data, subscriptions, or manual DOM updates after rendering.'
        },
        {
            'question': 'What is the Virtual DOM, and how does React use it to optimize rendering?',
            'answer_guideline': 'The Virtual DOM is a lightweight in-memory representation of the real DOM. When state changes, React creates a new virtual DOM, compares it with the previous one (diffing), and batches updates to change only the modified elements in the real DOM.'
        }
    ],
    'Docker': [
        {
            'question': 'What is the difference between a Docker Image and a Docker Container?',
            'answer_guideline': 'A Docker Image is a read-only template containing instructions to build a container. A Docker Container is a runnable, isolated instance of that image.'
        }
    ],
    'Kubernetes': [
        {
            'question': 'Explain the difference between a Pod, a Deployment, and a Service in Kubernetes.',
            'answer_guideline': 'A Pod is the smallest deployable unit (running one or more containers). A Deployment manages state, scaling, and rolling updates for Pods. A Service exposes a group of Pods as a network service with a stable IP and DNS name.'
        }
    ],
    'SQL': [
        {
            'question': 'What is the difference between INNER JOIN, LEFT JOIN, and OUTER JOIN in database queries?',
            'answer_guideline': 'INNER JOIN returns records with matching values in both tables. LEFT JOIN returns all records from the left table and matched records from the right (returns NULL if no match). OUTER JOIN (or FULL OUTER JOIN) returns all records when there is a match in either table.'
        }
    ],
    'MySQL': [
        {
            'question': 'What are indexes in MySQL, and how do they speed up database performance? Are there any disadvantages?',
            'answer_guideline': 'Indexes are data structures (usually B-Trees) that allow fast searching. They speed up SELECT queries but slow down INSERT, UPDATE, and DELETE operations since index tables must also be updated. They also take up extra disk space.'
        }
    ],
    'PostgreSQL': [
        {
            'question': 'Compare MySQL and PostgreSQL in terms of data integrity, features, and concurrency models.',
            'answer_guideline': 'PostgreSQL is highly standards-compliant, object-relational, supports advanced types (like JSONB, arrays), and utilizes MVCC (Multi-Version Concurrency Control) for concurrency. MySQL is historically faster for read-intensive, simple queries but has fewer features.'
        }
    ],
    'AWS': [
        {
            'question': 'Explain the difference between AWS EC2, AWS Lambda, and AWS S3.',
            'answer_guideline': 'EC2 provides virtual servers in the cloud (IaaS). Lambda is serverless computing that runs code in response to events (FaaS). S3 is a simple object storage service (SaaS) for storing assets, logs, or static web pages.'
        }
    ],
    'Machine Learning': [
        {
            'question': 'What is the bias-variance tradeoff in Machine Learning models?',
            'answer_guideline': 'Bias refers to errors from simple assumptions (leading to underfitting). Variance refers to errors from sensitivity to training noise (leading to overfitting). The goal is to find an optimal balance that minimizes total error.'
        }
    ],
    'Deep Learning': [
        {
            'question': 'What is the role of activation functions in a Neural Network? Give examples.',
            'answer_guideline': 'Activation functions introduce non-linearity, allowing neural networks to learn complex non-linear decision boundaries. Examples include ReLU (rectified linear unit), Sigmoid (for binary probability output), and Softmax (for multi-class probabilities).'
        }
    ],
    'Git': [
        {
            'question': 'Describe the differences between git merge and git rebase. When should you use which?',
            'answer_guideline': 'Merge creates a new commit joining history branch timelines together. Rebase reapplies commits on top of another base, keeping a linear commit log. Use merge to preserve complete historical branches, and rebase for cleanup before pushing to shared branches.'
        }
    ],
    'HTML': [
        {
            'question': 'What is semantic HTML? Why is it crucial for modern web development?',
            'answer_guideline': 'Semantic HTML uses tags that clearly describe their meaning (e.g. <article>, <header>, <section>). It improves web accessibility (screen readers), SEO indexing, and code maintainability.'
        }
    ],
    'CSS': [
        {
            'question': 'Explain the differences between CSS Flexbox and CSS Grid. When would you use each layout model?',
            'answer_guideline': 'Flexbox is designed for one-dimensional layouts (a single row or column), while Grid is designed for two-dimensional layouts (rows AND columns simultaneously). Use Flexbox for alignments inside navbars/lists, and Grid for page structures.'
        }
    ]
}

def generate_interview_questions(skills_list):
    """
    Takes a list of skills and generates a set of practice interview questions.
    """
    questions = []
    
    # Track which skills we have added questions for to avoid duplicates
    processed_skills = set()
    
    # 1. First, scan extracted skills to find matching pre-defined questions
    for skill in skills_list:
        skill_lower = skill.lower()
        
        # Match case-insensitively with keys in DB
        matched_key = None
        for key in SKILL_INTERVIEW_DB.keys():
            if key.lower() == skill_lower:
                matched_key = key
                break
                
        if matched_key and matched_key not in processed_skills:
            processed_skills.add(matched_key)
            # Add all questions associated with this skill
            for q_data in SKILL_INTERVIEW_DB[matched_key]:
                questions.append({
                    'skill': matched_key,
                    'question': q_data['question'],
                    'answer_guideline': q_data['answer_guideline']
                })
                
    # 2. Fallback: If we have few or no questions, generate dynamic generic ones
    if len(questions) < 5:
        for skill in skills_list:
            if skill not in processed_skills and len(processed_skills) < 5:
                processed_skills.add(skill)
                questions.append({
                    'skill': skill,
                    'question': f"Explain a challenging technical problem you solved using {skill}. What were the key constraints, and how did you resolve them?",
                    'answer_guideline': f"When answering, use the STAR method (Situation, Task, Action, Result). State the problem, how you applied {skill}, the alternative solutions you evaluated, and the final impact (e.g. speedup, lines written, user adoption)."
                })
                
    # Limit to maximum 8 questions
    return questions[:8]
