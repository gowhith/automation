from sentence_transformers import SentenceTransformer, util

# Load the AI model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Your ideal job description (edit as needed)
target_job_description = """
Looking for Software Engineering Intern, Software Development Intern, Programming Intern, 
Computer Science Intern, Web Development Intern, Full Stack Intern, Frontend Intern, 
Backend Intern, Python Intern, Java Intern, JavaScript Intern, React Intern, 
Node.js Intern, Database Intern, API Intern, Mobile App Intern, UI/UX Intern, 
DevOps Intern, Cloud Intern, AWS Intern, Azure Intern, Git Intern, Agile Intern, 
Scrum Intern, Testing Intern, QA Intern, Debugging Intern, Code Review Intern, 
Version Control Intern, Software Testing Intern, Automation Intern, CI/CD Intern, 
with remote or hybrid flexibility, competitive stipend, mentorship opportunities, 
learning and growth potential.
"""

def get_match_score(job_text, target_text=target_job_description):
    """
    Returns a similarity score (0-100) between the job_text and the target_text.
    """
    try:
        embeddings = model.encode([job_text, target_text])
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        return similarity.item() * 100
    except Exception as e:
        print(f"❌ Error calculating similarity: {e}")
        return 0

# Example usage:
if __name__ == "__main__":
    job_description = """
    We are seeking a Software Engineering Intern to join our team. The ideal candidate will have experience with Python, JavaScript, and cloud technologies. This is a remote internship with mentorship opportunities.
    """
    score = get_match_score(job_description)
    print(f"AI Match Score: {score:.2f}") 