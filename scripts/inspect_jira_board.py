import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("JIRA_EMAIL")
token = os.getenv("JIRA_API_TOKEN")
creds = base64.b64encode(f"{email}:{token}".encode()).decode()
headers = {"Authorization": f"Basic {creds}", "Accept": "application/json"}

# Sprints
for s_id in [2, 1]:
    res = requests.get(f"https://deccanagents.atlassian.net/rest/agile/1.0/sprint/{s_id}/issue", headers=headers)
    if res.status_code == 200:
        issues = res.json().get("issues", [])
        print(f"\nSprint {s_id} issues count: {len(issues)}")
        for iss in issues:
            print(f"  [{iss.get('key')}] {iss.get('fields', {}).get('summary')} (Status: {iss.get('fields', {}).get('status', {}).get('name')})")

# Check SCRUM-18 and SCRUM-19 specific details
for k in ["SCRUM-18", "SCRUM-19"]:
    res = requests.get(f"https://deccanagents.atlassian.net/rest/api/3/issue/{k}", headers=headers)
    if res.status_code == 200:
        data = res.json()
        fields = data.get("fields", {})
        # Find sprint field
        sprint_val = None
        for f_name, f_val in fields.items():
            if isinstance(f_val, list) and f_val and isinstance(f_val[0], dict) and "sprint" in f_val[0].get("self", ""):
                sprint_val = [s.get("name") for s in f_val]
            elif isinstance(f_val, dict) and "sprint" in f_val.get("self", ""):
                sprint_val = f_val.get("name")
        print(f"\nIssue {k}: Status={fields.get('status', {}).get('name')}, Sprint={sprint_val}")
