SKILLS_DB = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
        "r", "matlab", "perl", "dart", "sql", "bash", "shell scripting"
    ],
    "Web Development": [
        "html", "css", "react", "reactjs", "angular", "vue", "vuejs",
        "next.js", "nextjs", "node.js", "nodejs", "express.js", "django",
        "flask", "fastapi", "spring boot", "asp.net", "bootstrap",
        "tailwind css", "jquery", "rest api", "restful api", "graphql",
        "webpack", "redux"
    ],
    "Data Science & AI/ML": [
        "machine learning", "deep learning", "artificial intelligence",
        "natural language processing", "nlp", "computer vision",
        "data science", "data analysis", "data visualization",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "matplotlib", "seaborn", "opencv",
        "large language models", "llm", "generative ai", "neural networks",
        "statistics", "hugging face", "langchain"
    ],
    "Databases": [
        "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis",
        "cassandra", "firebase", "dynamodb", "elasticsearch",
        "database management", "nosql"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "google cloud", "gcp",
        "docker", "kubernetes", "jenkins", "ci/cd", "terraform",
        "ansible", "linux", "git", "github", "gitlab", "devops",
        "microservices", "serverless"
    ],
    "Tools & Platforms": [
        "jira", "confluence", "postman", "figma", "excel", "power bi",
        "tableau", "vs code", "intellij", "slack", "notion"
    ],
    "Soft Skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "critical thinking", "time management", "adaptability",
        "collaboration", "project management", "presentation skills",
        "analytical skills", "creativity", "attention to detail",
        "decision making", "conflict resolution"
    ],
    "Methodologies": [
        "agile", "scrum", "kanban", "waterfall", "test driven development",
        "tdd", "object oriented programming", "oop", "design patterns",
        "software development lifecycle", "sdlc"
    ],
}


ALL_SKILLS = {}
for category, skills in SKILLS_DB.items():
    for s in skills:
        ALL_SKILLS[s.lower()] = category


ACTION_VERBS = [
    "achieved", "improved", "trained", "managed", "created", "resolved",
    "volunteered", "influenced", "increased", "decreased", "researched",
    "authored", "spearheaded", "launched", "designed", "built", "developed",
    "implemented", "led", "optimized", "automated", "reduced", "delivered",
    "streamlined", "established", "coordinated", "engineered", "architected",
    "analyzed", "collaborated", "mentored", "negotiated", "generated",
    "executed", "presented", "restructured", "transformed", "pioneered"
]

STANDARD_SECTIONS = {
    "contact": ["contact", "email", "phone", "address"],
    "summary": ["summary", "objective", "profile", "about me"],
    "education": ["education", "academic", "qualification"],
    "experience": ["experience", "employment", "work history", "career"],
    "skills": ["skills", "technical skills", "core competencies", "expertise"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certification", "certificate", "license"],
}
