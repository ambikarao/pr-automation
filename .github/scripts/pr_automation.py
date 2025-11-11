import os
from github import Github
from openai import OpenAI

# Initialize GitHub and OpenAI clients
g = Github(os.getenv('GITHUB_TOKEN'))
repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
pr_number = int(os.getenv('PR_NUMBER'))
pr = repo.get_pull(pr_number)
action = os.getenv('ACTION')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Get the PR diff
diff = pr.get_files()
diff_text = ''
for file in diff:
    diff_text += f'File: {file.filename}\n{file.patch}\n'

if action == 'fix_build':
    prompt = f"The CI build failed for this PR. Here is the diff:\n{diff_text}\nSuggest fixes to make the build pass. Provide specific code changes."
elif action == 'review_code':
    prompt = f"Review this PR diff:\n{diff_text}\nProvide constructive review comments, suggestions for improvements, and check for potential issues."
else:
    prompt = "Unknown action"

if prompt != "Unknown action":
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content
    comment_body = f"**{action.replace('_', ' ').title()} Result:**\n\n{result}"
    pr.create_issue_comment(comment_body)
