"""
Open, hand-curated career/skill taxonomy used to train a small local
TF-IDF + Logistic Regression classifier at startup, and to power
rule-based resume scoring -- with ZERO calls to any paid AI/LLM API.

Note on data source: we originally tried to pull the public Kaggle
"UpdatedResumeDataSet" (962 labeled resumes / 25 categories) mirrored on
GitHub. The sandbox this was built in blocks bulk/automated access to
raw.githubusercontent.com, so instead this taxonomy was hand-built from
well-known, publicly documented skill sets for each role (the same 25-ish
categories that dataset uses). Swap in a real CSV later (see
train_from_csv() in classifier.py) without changing any other code.
"""

CAREER_SKILLS = {
    "DevOps Engineer": {
        "core": ["docker", "kubernetes", "jenkins", "ci/cd", "ansible", "terraform",
                 "linux", "git", "aws", "shell scripting", "monitoring", "prometheus", "grafana"],
        "next": ["azure", "gcp", "cloudformation", "helm", "istio", "argo cd", "vault"],
    },
    "Site Reliability Engineer": {
        "core": ["kubernetes", "monitoring", "prometheus", "grafana", "incident response",
                 "sla", "slo", "linux", "python", "terraform", "aws", "on-call"],
        "next": ["chaos engineering", "istio", "opentelemetry", "pagerduty", "golang"],
    },
    "Cloud Engineer": {
        "core": ["aws", "azure", "gcp", "terraform", "cloudformation", "networking",
                 "iam", "vpc", "linux", "docker", "cost optimization"],
        "next": ["kubernetes", "lambda", "cloudfront", "serverless", "multi-cloud"],
    },
    "Data Scientist": {
        "core": ["python", "machine learning", "pandas", "numpy", "scikit-learn",
                 "statistics", "sql", "data visualization", "matplotlib", "regression"],
        "next": ["deep learning", "tensorflow", "pytorch", "nlp", "mlops", "spark"],
    },
    "Machine Learning Engineer": {
        "core": ["python", "tensorflow", "pytorch", "machine learning", "deep learning",
                 "mlops", "model deployment", "docker", "sql", "feature engineering"],
        "next": ["kubernetes", "llm", "mlflow", "airflow", "distributed training"],
    },
    "Data Analyst": {
        "core": ["sql", "excel", "data visualization", "tableau", "power bi",
                 "python", "statistics", "reporting", "data cleaning"],
        "next": ["pandas", "looker", "a/b testing", "dax", "google analytics"],
    },
    "Data Engineer": {
        "core": ["python", "sql", "etl", "spark", "airflow", "data warehousing",
                 "kafka", "aws", "data modeling"],
        "next": ["dbt", "snowflake", "databricks", "kubernetes", "streaming"],
    },
    "Backend Developer (Java)": {
        "core": ["java", "spring boot", "rest api", "sql", "microservices",
                 "hibernate", "maven", "git", "unit testing", "multithreading"],
        "next": ["kafka", "docker", "kubernetes", "aws", "graphql"],
    },
    "Backend Developer (Python)": {
        "core": ["python", "django", "flask", "rest api", "sql", "postgresql",
                 "git", "unit testing", "orm", "celery"],
        "next": ["fastapi", "docker", "kubernetes", "redis", "aws"],
    },
    "Frontend Developer": {
        "core": ["javascript", "react", "html", "css", "typescript", "redux",
                 "webpack", "responsive design", "git", "rest api"],
        "next": ["next.js", "vue", "graphql", "testing library", "tailwind"],
    },
    "Full Stack Developer": {
        "core": ["javascript", "react", "node.js", "html", "css", "sql",
                 "rest api", "git", "mongodb", "express"],
        "next": ["typescript", "next.js", "docker", "aws", "graphql"],
    },
    "Mobile Developer": {
        "core": ["android", "kotlin", "swift", "ios", "react native", "flutter",
                 "rest api", "git", "mobile ui design"],
        "next": ["firebase", "graphql", "ci/cd", "unit testing"],
    },
    "Database Administrator": {
        "core": ["sql", "postgresql", "oracle", "mysql", "backup and recovery",
                 "performance tuning", "database design", "replication", "indexing"],
        "next": ["mongodb", "aws rds", "sharding", "cassandra"],
    },
    "QA / Test Engineer": {
        "core": ["manual testing", "automation testing", "selenium", "test cases",
                 "regression testing", "sql", "bug tracking", "jira", "api testing"],
        "next": ["cypress", "performance testing", "ci/cd", "postman"],
    },
    "Cybersecurity Engineer": {
        "core": ["network security", "firewalls", "penetration testing", "siem",
                 "vulnerability assessment", "incident response", "linux", "iam"],
        "next": ["cloud security", "threat hunting", "soc", "compliance", "encryption"],
    },
    "Network Engineer": {
        "core": ["networking", "cisco", "routing", "switching", "firewalls",
                 "tcp/ip", "vpn", "dns", "load balancing"],
        "next": ["sdn", "aws networking", "network automation", "python"],
    },
    "Blockchain Developer": {
        "core": ["solidity", "ethereum", "smart contracts", "web3", "blockchain",
                 "cryptography", "javascript"],
        "next": ["rust", "defi", "layer 2", "nft"],
    },
    "Embedded Systems Engineer": {
        "core": ["c", "c++", "embedded systems", "microcontrollers", "rtos",
                 "firmware", "circuit design"],
        "next": ["iot", "arm", "python", "linux kernel"],
    },
    "Business Analyst": {
        "core": ["requirements gathering", "sql", "excel", "process modeling",
                 "stakeholder management", "documentation", "data analysis"],
        "next": ["power bi", "agile", "jira", "sql tuning"],
    },
    "Product Manager": {
        "core": ["product strategy", "roadmapping", "agile", "stakeholder management",
                 "user research", "analytics", "prioritization"],
        "next": ["sql", "a/b testing", "figma", "okrs"],
    },
    "Project Manager": {
        "core": ["project planning", "agile", "scrum", "risk management", "budgeting",
                 "stakeholder management", "jira", "communication"],
        "next": ["pmp", "kanban", "resource management"],
    },
    "UI/UX Designer": {
        "core": ["figma", "wireframing", "user research", "prototyping", "ui design",
                 "ux design", "adobe xd", "design systems"],
        "next": ["usability testing", "html", "css", "accessibility"],
    },
    "HR Manager": {
        "core": ["recruitment", "onboarding", "employee relations", "hr policies",
                 "performance management", "payroll", "communication"],
        "next": ["hrms", "compliance", "talent management"],
    },
    "Digital Marketing": {
        "core": ["seo", "sem", "social media marketing", "content marketing",
                 "google analytics", "email marketing", "ppc"],
        "next": ["marketing automation", "a/b testing", "google ads"],
    },
    "Financial Analyst": {
        "core": ["financial modeling", "excel", "forecasting", "budgeting",
                 "valuation", "accounting", "reporting"],
        "next": ["sql", "power bi", "python", "vba"],
    },
}

# Generic soft / cross-cutting skills that boost a resume regardless of category
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "problem solving", "collaboration",
    "time management", "critical thinking", "adaptability", "mentoring",
]

# Words that signal quantifiable, achievement-oriented writing (used in scoring)
ACTION_VERBS = [
    "led", "built", "designed", "implemented", "improved", "reduced", "increased",
    "automated", "optimized", "developed", "launched", "architected", "delivered",
    "migrated", "scaled", "mentored", "managed", "created", "deployed",
]

RESUME_SECTION_HINTS = ["experience", "education", "projects", "skills", "certification", "summary"]


def all_categories():
    return list(CAREER_SKILLS.keys())


def master_skill_list():
    """Flat, de-duplicated list of every skill keyword we know about (for detection)."""
    seen = set()
    ordered = []
    for data in CAREER_SKILLS.values():
        for skill in data["core"] + data["next"]:
            key = skill.lower()
            if key not in seen:
                seen.add(key)
                ordered.append(skill)
    for skill in SOFT_SKILLS:
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(skill)
    return ordered


# Common real-world synonyms/abbreviations/alternate phrasings, mapped to the
# canonical skill name used above. Lets skill detection catch resumes that
# write "Continuous Integration" instead of "ci/cd", "K8s" instead of
# "kubernetes", etc. Keys are lowercase phrases; values must exactly match an
# existing skill string (case-insensitively) somewhere in CAREER_SKILLS/SOFT_SKILLS.
SKILL_ALIASES = {
    "continuous integration": "ci/cd",
    "continuous integration and continuous deployment": "ci/cd",
    "continuous integration/continuous deployment": "ci/cd",
    "continuous delivery": "ci/cd",
    "ci/cd pipelines": "ci/cd",
    "ci cd": "ci/cd",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    "microsoft azure": "azure",
    "js": "javascript",
    "ecmascript": "javascript",
    "ts": "typescript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node js": "node.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "nextjs": "next.js",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "html5": "html",
    "css3": "css",
    "unix": "linux",
    "github": "git",
    "gitlab": "git",
    "version control": "git",
    "mongo": "mongodb",
    "powerbi": "power bi",
    "pen testing": "penetration testing",
    "pentest": "penetration testing",
    "pentesting": "penetration testing",
    "identity and access management": "iam",
    "virtual private cloud": "vpc",
    "unit tests": "unit testing",
    "microservice architecture": "microservices",
    "springboot": "spring boot",
    "spring-boot": "spring boot",
    "oracle db": "oracle",
    "oracle database": "oracle",
    "tf": "tensorflow",
    "sklearn": "scikit-learn",
    "ms excel": "excel",
    "microsoft excel": "excel",
    "cpp": "c++",
    "csharp": "c#",
    "c sharp": "c#",
    "react-native": "react native",
    "helm charts": "helm",
    "aws cloudformation": "cloudformation",
    "aws lambda": "lambda",
    "infrastructure as code": "terraform",
    "iac": "terraform",
    "ec2": "aws",
    "s3": "aws",
    "cloudfront": "aws",
    "route 53": "aws",
    "dynamodb": "aws",
    "azure devops": "azure",
    "gcp cloud": "gcp",
    "agile scrum": "scrum",
    "data analysis": "data analysis",
    "power bi desktop": "power bi",
    "figma design": "figma",
    "adobe xd design": "adobe xd",
}
