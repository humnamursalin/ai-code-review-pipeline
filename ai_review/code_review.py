import openai
import os
from git import Repo

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_git_diff(repo_path="."):
    repo = Repo(repo_path)
    diff = repo.git.diff('HEAD~1', 'HEAD')
    return diff

def review_code(diff):
    if not diff.strip():
        return "No changes detected."

    print("Sending diff to OpenAI...")
    
    prompt = f"""
    You are a senior software engineer. Review the following code diff and identify:
    - Bugs
    - Security vulnerabilities
    - Improvements
    - Best practices
    - Any risky patterns

    Code Diff:
    {diff}

    Provide a structured report with clear headings.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message["content"]

def save_report(report):
    with open("ai_review_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    diff = get_git_diff()
    report = review_code(diff)
    save_report(report)
    print("AI Review Completed! Report saved to ai_review_report.txt")
