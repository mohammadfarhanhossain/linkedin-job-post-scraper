"""
Career Advisor & AI Pitch Generator Module.
Provides:
- Tailored Job Application Cover Letter generation
- LinkedIn Recruiter Outreach Pitch generator
- Dynamic Industry Skill Roadmaps
- Curated Interview Question Banks by Specialization
"""

from typing import Dict, Any, List, Optional


ROADMAP_DATA: Dict[str, Dict[str, Any]] = {
    "Machine Learning & AI": {
        "demand": "Very High (🔥 Hot Global & Local Demand)",
        "summary": "Focuses on predictive models, deep learning, LLM fine-tuning, RAG pipelines, and scalable inference.",
        "phase1": ["Python Mastery, NumPy, Pandas, Vector Math", "Linear Algebra, Multivariable Calculus, Probability & Stats", "Classical ML: Scikit-Learn (Regression, Trees, XGBoost, Clustering)"],
        "phase2": ["Deep Learning: PyTorch or TensorFlow, CNNs, Transformers", "NLP & LLMs: HuggingFace, LangChain, LlamaIndex, Vector DBs (Chroma, Pinecone)", "MLOps: Docker, MLflow, FastAPI for Model Serving, ONNX Runtime"],
        "phase3": ["End-to-End Multimodal or Agentic AI Project deployed on Cloud (GCP/AWS)", "Distributed Training, LoRA/PEFT Fine-Tuning, Quantization (bitsandbytes)"],
        "certifications": ["AWS Certified Machine Learning - Specialty", "Google Cloud Professional ML Engineer", "DeepLearning.AI TensorFlow / GenAI Specialization"],
        "interview_questions": [
            {"q": "How do you mitigate catastrophic forgetting and hallucination in LLMs?", "hint": "RAG architecture, RLHF, DPO, temperature tuning, and fine-tuning with replay buffers."},
            {"q": "Explain the difference between L1 and L2 regularization.", "hint": "L1 (Lasso) produces sparse weights (feature selection); L2 (Ridge) shrinks weights toward zero without forcing absolute zero."},
            {"q": "How does multi-head self-attention work in Transformer models?", "hint": "Queries, Keys, Values matrices scaled dot-product attention split into multiple parallel representation subspaces."},
            {"q": "How do you evaluate an imbalanced classification problem?", "hint": "Precision-Recall curves, F1-Score, PR-AUC, Confusion Matrix, not standard Accuracy."}
        ]
    },
    "Python & FastAPI Backend": {
        "demand": "High (Core Engine for SaaS, AI & Microservices)",
        "summary": "Specializes in high-throughput REST/GraphQL APIs, asynchronous I/O, database ORMs, and microservices architecture.",
        "phase1": ["Advanced Python: AsyncIO, Generators, Type Hints, Metaclasses", "Relational DBs: PostgreSQL, indexing, query optimization, EXPLAIN ANALYZE", "HTTP/HTTPS specs, RESTful API design conventions, JSON schemas"],
        "phase2": ["FastAPI & Pydantic v2, SQLAlchemy 2.0 / Tortoise ORM", "Redis Caching, Celery / ARQ background tasks, RabbitMQ / Kafka message queues", "Authentication: JWT, OAuth2, RBAC, Rate-Limiting, CORS"],
        "phase3": ["Docker, Docker Compose, Kubernetes deployment manifests", "CI/CD automated testing with Pytest, Locust load testing, Grafana/Prometheus monitoring"],
        "certifications": ["AWS Certified Developer - Associate", "Certified Kubernetes Application Developer (CKAD)"],
        "interview_questions": [
            {"q": "How does Python AsyncIO event loop differ from multi-threading / multi-processing?", "hint": "AsyncIO uses cooperative single-threaded event loop for I/O bound tasks; multiprocessing bypasses the GIL for CPU-bound tasks."},
            {"q": "How do you handle N+1 query problem in SQLAlchemy?", "hint": "Use joinedload or selectinload eager loading strategies instead of lazy loading."},
            {"q": "What is database connection pooling and how do you size the pool?", "hint": "Reusing pre-established connections to eliminate TCP handshake overhead; sized according to DB CPU cores and I/O concurrency."}
        ]
    },
    "Cloud & DevOps": {
        "demand": "Critical (Top Salary Benchmark in Local & Remote Markets)",
        "summary": "Bridges development and operations via Infrastructure as Code (IaC), GitOps, container orchestration, and zero-downtime CI/CD.",
        "phase1": ["Linux System Administration, Bash scripting, SSH, Networking (TCP/IP, DNS, VPC)", "Git Version Control, Trunk-Based Development", "Docker containerization best practices (multi-stage builds, rootless images)"],
        "phase2": ["Kubernetes (Pods, Deployments, Services, Ingress, Helm Charts)", "Terraform / OpenTofu for declarative Cloud IaC", "CI/CD: GitHub Actions, GitLab CI, ArgoCD for GitOps"],
        "phase3": ["Observability: Prometheus, Grafana, OpenTelemetry, ELK stack", "Cloud Security: IAM least-privilege, Vault secret management, Trivy image scanning"],
        "certifications": ["CKA (Certified Kubernetes Administrator)", "AWS Solutions Architect Associate", "HashiCorp Terraform Associate"],
        "interview_questions": [
            {"q": "Describe the lifecycle of a request entering a Kubernetes cluster through an Ingress controller.", "hint": "External DNS -> LoadBalancer -> Ingress Controller (Nginx/Traefik) -> Ingress Rules -> ClusterIP Service -> Endpoint slices -> Target Pod container."},
            {"q": "How do you manage state and avoid drift in multi-environment Terraform?", "hint": "Remote backend (S3/GCS with DynamoDB state locking), workspace partitioning or Terragrunt, and automated plan drifts."},
            {"q": "Explain Blue-Green vs Canary deployments.", "hint": "Blue-Green switches 100% traffic immediately between two environments; Canary gradually routes a small percentage (e.g. 5% -> 25% -> 100%) while observing error metrics."}
        ]
    },
    "VLSI / ASIC Design": {
        "demand": "Ultra-Specialized (Very High Global & Growing BD Semiconductor)",
        "summary": "Hardware description, RTL verification, logic synthesis, FPGA prototyping, and physical design for chips and microelectronics.",
        "phase1": ["Digital Logic Design, Boolean Algebra, Finite State Machines (FSM)", "Computer Architecture: RISC-V, pipelining, caching, memory hierarchies", "Verilog and SystemVerilog HDL fundamentals"],
        "phase2": ["SystemVerilog for Verification, UVM (Universal Verification Methodology)", "EDA Tools: Synopsys VCS, Cadence Incisive, ModelSim, Vivado FPGA prototyping", "Static Timing Analysis (STA), clock domain crossing (CDC)"],
        "phase3": ["Physical Design (ASIC synthesis, floorplanning, placement & routing, DRC/LVS)", "Tape-out flow, DFT (Design for Testability), ATPG"],
        "certifications": ["Synopsys Certified Semiconductor Professional", "IEEE VLSI Training Certifications"],
        "interview_questions": [
            {"q": "What is Clock Domain Crossing (CDC) and how do you resolve metastability?", "hint": "Signals passing between asynchronous clocks; mitigated using multi-flop synchronizers (2-FF/3-FF), asynchronous FIFOs, or handshake protocols."},
            {"q": "Explain Setup Time and Hold Time violations in sequential circuits.", "hint": "Setup time: data must be stable before clock edge. Hold time: data must be stable after clock edge. Setup violation fixed by reducing combinational delay; hold violation fixed by inserting delay buffers."},
            {"q": "What is the difference between blocking (=) and non-blocking (<=) assignments in Verilog?", "hint": "Blocking executes sequentially in the procedural block (used in combinational logic); non-blocking evaluates in parallel at end of timestep (used in sequential clocked registers)."}
        ]
    },
    "Full Stack Software Engineer": {
        "demand": "Extremely High (Highest Volume of Vacancies)",
        "summary": "End-to-end web product development covering front-end user experience, robust backend APIs, and database architecture.",
        "phase1": ["JavaScript (ES6+), TypeScript, HTML5/CSS3 semantics", "Modern React (Hooks, Context, State Management)", "Node.js / Python backend, REST APIs, PostgreSQL / MongoDB"],
        "phase2": ["Next.js (App Router, Server Components, SSR)", "Tailwind CSS, TanStack Query, Zustand / Redux Toolkit", "Prisma / Drizzle ORM, Dockerized container deployment"],
        "phase3": ["System Design: Caching, Load Balancing, Micro-frontends, WebSockets", "Automated Testing: Jest, React Testing Library, Playwright E2E"],
        "certifications": ["Meta Front-End & Back-End Developer Professional Certificate", "AWS Certified Developer"],
        "interview_questions": [
            {"q": "How does React 19 / Server Components change data fetching and hydration?", "hint": "RSC execute exclusively on the server, zero bundle impact, direct DB access, eliminating client-side waterfall fetches."},
            {"q": "Explain database indexing tradeoffs (B-Tree vs Hash index).", "hint": "Indexes speed up read queries significantly (O(log n)), but add write overhead (INSERT/UPDATE/DELETE) and consume storage disk space."}
        ]
    }
}


def get_career_roadmap(specialization: str) -> Dict[str, Any]:
    """Returns curated career roadmap, phases, certifications and questions for a specialization."""
    # Find closest match
    for k, v in ROADMAP_DATA.items():
        if k.lower() in specialization.lower() or specialization.lower() in k.lower():
            return {"role": k, **v}

    # High quality general engineering fallback
    return {
        "role": specialization,
        "demand": "Active Market Demand",
        "summary": f"Professional specialization focused on {specialization} engineering practices, domain expertise, and enterprise delivery.",
        "phase1": [
            "Core theoretical fundamentals, data analysis, and domain standards",
            "Professional programming / scripting or engineering CAD/EDA software proficiency",
            "Understanding industry safety codes, compliance, and architectural best practices"
        ],
        "phase2": [
            "Industry-standard tools, frameworks, and modern automation pipelines",
            "Cross-functional collaboration with Git, JIRA, and Agile methodologies",
            "Performance optimization, quality assurance, and automated verification"
        ],
        "phase3": [
            "Leading end-to-end projects with production impact and documentation",
            "Mentoring junior talent and establishing architectural design patterns"
        ],
        "certifications": ["Relevant Global Industry Certification (Vendor Specific)", "Professional Engineering (PE / BPERB) Accreditation"],
        "interview_questions": [
            {"q": "What is the most technically complex problem you solved in your recent work?", "hint": "Use the STAR method (Situation, Task, Action, Result) with quantitative metrics."},
            {"q": "How do you ensure reliability, error handling, and security in your domain?", "hint": "Describe defensive architecture, automated validation, and fail-safe fallbacks."}
        ]
    }


def generate_cover_letter(
    candidate_name: str,
    years_exp: str,
    current_role: str,
    user_skills: List[str],
    job: Dict[str, Any]
) -> str:
    """
    Generates a personalized, professional application cover letter.
    """
    company = job.get("company", "Hiring Team")
    title = job.get("title", "Open Vacancy")
    location = job.get("location", "your office")
    req_skills = job.get("skills", "")
    spec = job.get("specialization") or job.get("category") or "Engineering"

    skills_joined = ", ".join(user_skills[:4]) if user_skills else "modern software engineering and problem-solving"

    cover_letter = f"""Subject: Application for {title} - {candidate_name}

Dear Hiring Team at {company},

I am writing to express my strong interest in the {title} position currently open at {company} in {location}. With {years_exp} of hands-on experience as a {current_role}, coupled with a solid foundation in {spec}, I am confident in my ability to immediately contribute to your engineering objectives.

In reviewing your requirements, I noted your emphasis on {req_skills if req_skills else 'scalable technical solutions'}. Throughout my recent work, I have specialized in {skills_joined}, successfully delivering robust, maintainable, and high-performance solutions under tight schedules.

What particularly excites me about {company} is your technical focus and reputation for engineering excellence. I thrive in collaborative environments where continuous improvement, code craftsmanship, and business impact are prioritized.

Key highlights of what I bring to {company}:
• Proven track record in designing, implementing, and shipping production-ready systems.
• Practical expertise in {skills_joined}.
• Strong problem-solving aptitude with a proactive commitment to clean architecture and testing.

I welcome the opportunity to discuss how my skill set and enthusiasm align with your team's goals. Thank you for your time and consideration.

Sincerely,

{candidate_name}
Email / Portfolio: [Insert Your Contact Info]
LinkedIn Profile: [Insert Your Profile URL]
"""
    return cover_letter.strip()


def generate_recruiter_pitch(
    candidate_name: str,
    years_exp: str,
    user_skills: List[str],
    job: Dict[str, Any]
) -> str:
    """
    Generates a high-converting, crisp (< 140 words) cold message for LinkedIn DM or email.
    """
    company = job.get("company", "your team")
    title = job.get("title", "the open role")
    skills_joined = ", ".join(user_skills[:3]) if user_skills else "full-cycle engineering"

    pitch = f"""Hi [Hiring Manager / Recruiter Name],

I noticed that {company} is hiring for a {title}, and I wanted to reach out directly.

I am a software professional with {years_exp} of experience specializing in {skills_joined}. Having built scalable systems and followed {company}'s impressive growth, I believe my background aligns closely with the technical challenges your team is solving.

I've already submitted a formal application, but I'd love to share my portfolio and explore if my skill set would be a great fit for your pipeline. 

Would you be open to a brief 5-minute chat this week?

Best regards,
{candidate_name}
[Insert Phone / Portfolio Link]
"""
    return pitch.strip()
