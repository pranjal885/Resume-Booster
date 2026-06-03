import re

# Comprehensive categorized dictionary of industry skills
SKILLS_VOCABULARY = {
    'programming_language': [
        'python', 'javascript', 'typescript', 'java', 'c\\+\\+', 'c#', 'c', 'ruby', 'php', 
        'swift', 'kotlin', 'go', 'golang', 'rust', 'scala', 'perl', 'r', 'matlab', 'dart', 
        'cobol', 'fortran', 'solidity', 'html', 'css', 'sass', 'less', 'sql', 'shell', 'bash', 'powershell'
    ],
    'framework': [
        'react', 'react\\.js', 'reactjs', 'angular', 'angularjs', 'vue', 'vue\\.js', 'vuejs', 
        'node', 'node\\.js', 'nodejs', 'express', 'expressjs', 'django', 'flask', 'fastapi', 
        'ruby on rails', 'rails', 'spring', 'spring boot', 'laravel', 'symfony', 'codeigniter', 
        'asp\\.net', 'dotnet', 'jquery', 'bootstrap', 'tailwind', 'tailwindcss', 'material-ui', 
        'next\\.js', 'nextjs', 'nuxt\\.js', 'svelte', 'gatsby', 'ember', 'backbone'
    ],
    'database': [
        'mysql', 'postgresql', 'postgres', 'mongodb', 'sqlite', 'redis', 'oracle', 'sql server', 
        'microsoft sql server', 'cassandra', 'mariadb', 'dynamodb', 'firebase', 'neo4j', 
        'couchdb', 'influxdb', 'elasticsearch'
    ],
    'tool': [
        'docker', 'kubernetes', 'k8s', 'git', 'github', 'gitlab', 'bitbucket', 'aws', 'amazon web services', 
        'azure', 'microsoft azure', 'gcp', 'google cloud', 'google cloud platform', 'heroku', 'netlify', 
        'vercel', 'jenkins', 'circleci', 'travis ci', 'github actions', 'jira', 'confluence', 'trello', 
        'postman', 'slack', 'linux', 'unix', 'ubuntu', 'nginx', 'apache', 'ansible', 'terraform', 'vagrant',
        'prometheus', 'grafana', 'webpack', 'vite', 'gulp', 'npm', 'yarn'
    ],
    'technology': [
        'machine learning', 'ml', 'deep learning', 'dl', 'nlp', 'natural language processing', 
        'computer vision', 'cv', 'artificial intelligence', 'ai', 'neural networks', 'data science', 
        'data analytics', 'big data', 'hadoop', 'spark', 'apache spark', 'rest api', 'restful api', 
        'graphql', 'soap', 'microservices', 'ci/cd', 'continuous integration', 'continuous deployment', 
        'unit testing', 'tdd', 'test driven development', 'oop', 'object-oriented programming', 
        'system design', 'data structures', 'algorithms', 'web scraping', 'selenium', 'puppeteer', 
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'spacy', 'nltk', 
        'opencv', 'flutter', 'react native', 'ionic', 'xamarin', 'electron', 'web3', 'blockchain', 
        'iot', 'internet of things', 'cloud computing', 'devops', 'agile', 'scrum', 'kanban'
    ],
    'soft_skill': [
        'communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking', 
        'time management', 'adaptability', 'creativity', 'work ethic', 'attention to detail', 
        'presentation', 'collaboration', 'mentoring', 'customer service', 'negotiation', 
        'active listening', 'conflict resolution', 'emotional intelligence', 'decision making', 
        'interpersonal skills', 'organization'
    ]
}

def extract_skills(text):
    """
    Scans the given text against SKILLS_VOCABULARY.
    Returns a dictionary of categorized matched skills and a flat list of all skills.
    """
    if not text:
        return {'categorized': {}, 'flat_list': []}
        
    categorized_skills = {
        'programming_language': [],
        'framework': [],
        'database': [],
        'tool': [],
        'technology': [],
        'soft_skill': []
    }
    
    flat_list = []
    
    # Preprocess text slightly (lowercase, clean spaces)
    cleaned_text = re.sub(r'\s+', ' ', text).lower()
    
    for category, skills in SKILLS_VOCABULARY.items():
        for skill in skills:
            # Handle special characters in regex patterns (like c++)
            pattern = r'\b' + skill + r'\b'
            
            # For programming languages with special symbols (C++, C#), word boundaries might not match at the end
            if '++' in skill or '#' in skill:
                pattern = r'\b' + re.escape(skill.replace('\\', '')) + r'(?:\b|\s|$)'
            
            if re.search(pattern, cleaned_text, re.IGNORECASE):
                # Clean clean name to display beautifully (e.g. capitalize python -> Python)
                display_name = skill.replace('\\', '')
                
                # Make display name nice
                capitalization_map = {
                    'python': 'Python', 'javascript': 'JavaScript', 'typescript': 'TypeScript',
                    'java': 'Java', 'c++': 'C++', 'c#': 'C#', 'c': 'C', 'ruby': 'Ruby', 'php': 'PHP',
                    'swift': 'Swift', 'kotlin': 'Kotlin', 'go': 'Go', 'golang': 'Go', 'rust': 'Rust',
                    'scala': 'Scala', 'perl': 'Perl', 'r': 'R', 'matlab': 'MATLAB', 'dart': 'Dart',
                    'html': 'HTML', 'css': 'CSS', 'sass': 'Sass', 'less': 'Less', 'sql': 'SQL',
                    'shell': 'Shell', 'bash': 'Bash', 'powershell': 'PowerShell',
                    
                    'react': 'React', 'react.js': 'React.js', 'reactjs': 'React', 'angular': 'Angular',
                    'vue': 'Vue', 'vue.js': 'Vue.js', 'vuejs': 'Vue', 'node': 'Node.js', 'node.js': 'Node.js',
                    'nodejs': 'Node.js', 'express': 'Express.js', 'expressjs': 'Express.js', 'django': 'Django',
                    'flask': 'Flask', 'fastapi': 'FastAPI', 'ruby on rails': 'Ruby on Rails', 'rails': 'Rails',
                    'spring': 'Spring', 'spring boot': 'Spring Boot', 'laravel': 'Laravel', 'symfony': 'Symfony',
                    'dotnet': '.NET', 'asp.net': 'ASP.NET', 'jquery': 'jQuery', 'bootstrap': 'Bootstrap',
                    'tailwind': 'Tailwind CSS', 'tailwindcss': 'Tailwind CSS', 'material-ui': 'Material-UI',
                    'next.js': 'Next.js', 'nextjs': 'Next.js', 'next.js': 'Next.js', 'svelte': 'Svelte',
                    
                    'mysql': 'MySQL', 'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL', 'mongodb': 'MongoDB',
                    'sqlite': 'SQLite', 'redis': 'Redis', 'oracle': 'Oracle', 'sql server': 'SQL Server',
                    'cassandra': 'Cassandra', 'mariadb': 'MariaDB', 'dynamodb': 'DynamoDB', 'firebase': 'Firebase',
                    'elasticsearch': 'Elasticsearch',
                    
                    'docker': 'Docker', 'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes', 'git': 'Git',
                    'github': 'GitHub', 'gitlab': 'GitLab', 'aws': 'AWS', 'azure': 'Azure', 'gcp': 'GCP',
                    'heroku': 'Heroku', 'netlify': 'Netlify', 'vercel': 'Vercel', 'jenkins': 'Jenkins',
                    'circleci': 'CircleCI', 'github actions': 'GitHub Actions', 'jira': 'Jira',
                    'confluence': 'Confluence', 'postman': 'Postman', 'slack': 'Slack', 'linux': 'Linux',
                    'unix': 'Unix', 'ubuntu': 'Ubuntu', 'nginx': 'Nginx', 'apache': 'Apache',
                    'ansible': 'Ansible', 'terraform': 'Terraform', 'npm': 'npm', 'yarn': 'Yarn',
                    
                    'machine learning': 'Machine Learning', 'ml': 'Machine Learning',
                    'deep learning': 'Deep Learning', 'dl': 'Deep Learning',
                    'nlp': 'NLP', 'natural language processing': 'NLP',
                    'computer vision': 'Computer Vision', 'cv': 'Computer Vision',
                    'artificial intelligence': 'AI', 'ai': 'AI',
                    'data science': 'Data Science', 'data analytics': 'Data Analytics',
                    'rest api': 'REST API', 'restful api': 'REST API', 'graphql': 'GraphQL',
                    'microservices': 'Microservices', 'ci/cd': 'CI/CD',
                    'unit testing': 'Unit Testing', 'tdd': 'TDD', 'oop': 'OOP',
                    'system design': 'System Design', 'data structures': 'Data Structures',
                    'algorithms': 'Algorithms', 'web scraping': 'Web Scraping',
                    'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch', 'keras': 'Keras',
                    'scikit-learn': 'scikit-learn', 'sklearn': 'scikit-learn',
                    'pandas': 'Pandas', 'numpy': 'NumPy', 'spacy': 'spaCy', 'nltk': 'NLTK',
                    'opencv': 'OpenCV', 'flutter': 'Flutter', 'react native': 'React Native'
                }
                
                name_to_use = capitalization_map.get(display_name, display_name.title())
                
                # Deduplicate aliases (e.g. reactjs vs react, postgres vs postgresql)
                # Map values to their canonical display forms
                canonical_map = {
                    'react.js': 'React', 'reactjs': 'React', 'vue.js': 'Vue', 'vuejs': 'Vue',
                    'node.js': 'Node.js', 'nodejs': 'Node.js', 'expressjs': 'Express.js',
                    'tailwindcss': 'Tailwind CSS', 'nextjs': 'Next.js', 'postgres': 'PostgreSQL',
                    'sql server': 'SQL Server', 'microsoft sql server': 'SQL Server',
                    'google cloud': 'GCP', 'google cloud platform': 'GCP', 'amazon web services': 'AWS',
                    'ml': 'Machine Learning', 'dl': 'Deep Learning', 'natural language processing': 'NLP',
                    'cv': 'Computer Vision', 'sklearn': 'scikit-learn', 'k8s': 'Kubernetes',
                    'golang': 'Go'
                }
                
                canonical_name = canonical_map.get(display_name, name_to_use)
                
                if canonical_name not in categorized_skills[category]:
                    categorized_skills[category].append(canonical_name)
                if canonical_name not in flat_list:
                    flat_list.append(canonical_name)
                    
    return {
        'categorized': categorized_skills,
        'flat_list': flat_list
    }
