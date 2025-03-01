#!/usr/bin/env python3
import os
import requests
import sys

def setup_branch_protection(token, owner, repo, branch="main"):
    """Set up branch protection rules for the specified repository."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"

    protection_rules = {
        "required_status_checks": {
            "strict": True,
            "contexts": [
                "security-scan",
                "test",
                "dependency-review"
            ]
        },
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismissal_restrictions": {},
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1
        },
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False
    }

    response = requests.put(url, headers=headers, json=protection_rules)
    
    if response.status_code == 200:
        print(f"✅ Branch protection rules set for {branch}")
    else:
        print(f"❌ Failed to set branch protection rules: {response.status_code}")
        print(response.json())
        sys.exit(1)

def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        sys.exit(1)

    owner = "alihaydarsahin"  # Your GitHub username
    repo = "hospital-app"     # Your repository name

    print("Setting up branch protection rules...")
    setup_branch_protection(token, owner, repo)
    
    print("\nBranch protection setup complete!")
    print("\nProtection rules implemented:")
    print("1. Require pull request reviews")
    print("2. Require status checks to pass")
    print("3. Require linear history")
    print("4. Enforce admin restrictions")
    print("5. Prevent force pushes")
    print("6. Prevent branch deletion")

if __name__ == "__main__":
    main() 