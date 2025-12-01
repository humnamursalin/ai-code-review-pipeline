import openai
import os
import sys
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

    if not openai.api_key:
        error_msg = "⚠️ OpenAI API key not found. Skipping AI code review."
        print(error_msg)
        return error_msg

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

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
    except openai.RateLimitError as e:
        error_msg = f"⚠️ OpenAI API Rate Limit Error: {str(e)}\nSkipping AI code review. Please check your API quota and billing."
        print(error_msg)
        return error_msg
    except openai.APIError as e:
        error_msg = f"⚠️ OpenAI API Error: {str(e)}\nSkipping AI code review."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"⚠️ Unexpected error during AI code review: {str(e)}\nSkipping AI code review."
        print(error_msg)
        return error_msg

def save_report(report):
    with open("ai_review_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    try:
        diff = get_git_diff()
        report = review_code(diff)
        save_report(report)
        print("AI Review Completed! Report saved to ai_review_report.txt")
    except Exception as e:
        error_msg = f"⚠️ Error in code review process: {str(e)}"
        print(error_msg)
        save_report(error_msg)
        # Exit with code 0 to allow pipeline to continue
        sys.exit(0)
