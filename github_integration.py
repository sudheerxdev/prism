"""
GitHub Integration for Prism - ENHANCED
Auto-ingest, create, and sync issues with GitHub repositories.
"""

import requests
import json
from typing import Optional, List, Dict
from queue_store import add_message, get_cfg, set_cfg, _conn
from datetime import datetime


class GitHubClient:
    """Manage GitHub issue operations with sync capabilities."""
    
    def __init__(self, owner: str, repo: str, token: str):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.api_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {"Authorization": f"token {token}"}
    
    def fetch_issues(self, state: str = "open") -> List[Dict]:
        """Fetch issues from GitHub repository."""
        url = f"{self.api_url}/issues"
        params = {
            "state": state,
            "sort": "updated",
            "direction": "desc",
            "per_page": 100
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            print(f"✓ Fetched {len(response.json())} {state} issues from {self.owner}/{self.repo}")
            return response.json()
        except requests.RequestException as e:
            print(f"✗ GitHub API error: {e}")
            return []
    
    def create_issue(self, title: str, body: str, labels: List[str] = None, assignee: str = None) -> Optional[Dict]:
        """Create a new issue on GitHub."""
        url = f"{self.api_url}/issues"
        
        payload = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        
        if assignee:
            payload["assignee"] = assignee
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            issue_data = response.json()
            print(f"✓ Created GitHub issue #{issue_data['number']}: {title}")
            return issue_data
        except requests.RequestException as e:
            print(f"✗ Failed to create issue: {e}")
            return None
    
    def create_from_prism(self, item_id: str, title: str, content: str, priority: str = "medium") -> Optional[Dict]:
        """Create GitHub issue from Prism feedback with context."""
        body = f"""**Priority:** {priority.upper()}
**Prism ID:** {item_id}

## Description
{content}

---
*Auto-created by Prism feedback intelligence system*
"""
        
        labels = []
        if priority == "critical":
            labels.append("urgent")
        elif priority == "high":
            labels.append("important")
        
        labels.append("prism")
        
        return self.create_issue(title, body, labels)
    
    def update_issue(self, issue_number: int, state: str = None, labels: List[str] = None) -> bool:
        """Update GitHub issue state or labels."""
        url = f"{self.api_url}/issues/{issue_number}"
        
        payload = {}
        if state:
            payload["state"] = state
        if labels:
            payload["labels"] = labels
        
        try:
            response = requests.patch(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✓ Updated GitHub issue #{issue_number}")
            return True
        except requests.RequestException as e:
            print(f"✗ Failed to update issue: {e}")
            return False
    
    def close_issue(self, issue_number: int) -> bool:
        """Close a GitHub issue."""
        return self.update_issue(issue_number, state="closed")
    
    def sync_status(self, item_id: str, gh_issue_number: int, prism_status: str) -> bool:
        """Sync Prism status to GitHub issue."""
        status_map = {
            "closed": "closed",
            "pending": "open",
            "in_progress": "open",
        }
        gh_state = status_map.get(prism_status, "open")
        return self.update_issue(gh_issue_number, state=gh_state)


def fetch_github_issues(owner: str, repo: str, token: Optional[str] = None) -> list[dict]:
    """Fetch recent issues from a GitHub repository."""
    client = GitHubClient(owner, repo, token or "")
    return client.fetch_issues()


def ingest_github_issues(owner: str, repo: str, token: Optional[str] = None) -> int:
    """Ingest GitHub issues into Prism inbox."""
    client = GitHubClient(owner, repo, token or "")
    issues = client.fetch_issues()
    
    count = 0
    for issue in issues:
        # Skip pull requests
        if "pull_request" in issue:
            continue
        
        content = f"""
GitHub Issue #{issue['number']}: {issue['title']}

Description:
{issue['body'] or '(No description provided)'}

Labels: {', '.join(label['name'] for label in issue.get('labels', []))}
Author: {issue['user']['login']}
Link: {issue['html_url']}
""".strip()
        
        added = add_message(
            source="github",
            content=content,
            channel=f"{owner}/{repo}",
            author=issue['user']['login']
        )
        
        if added:
            count += 1
    
    return count


def create_github_issue_from_prism(owner: str, repo: str, item_id: str, title: str, 
                                   content: str, priority: str = "medium", token: Optional[str] = None) -> Optional[Dict]:
    """Create a GitHub issue from a Prism feedback item."""
    client = GitHubClient(owner, repo, token or "")
    return client.create_from_prism(item_id, title, content, priority)


def get_github_config() -> dict:
    """Get GitHub configuration from database."""
    return {
        "repo_owner": get_cfg("github_repo_owner", ""),
        "repo_name": get_cfg("github_repo_name", ""),
        "access_token": get_cfg("github_access_token", ""),
        "auto_sync_enabled": get_cfg("github_auto_sync", "false") == "true"
    }


def set_github_config(owner: str, repo: str, token: str = "", auto_sync: bool = False):
    """Save GitHub configuration."""
    set_cfg("github_repo_owner", owner)
    set_cfg("github_repo_name", repo)
    if token:
        set_cfg("github_access_token", token)
    set_cfg("github_auto_sync", "true" if auto_sync else "false")


# Example usage (would be called from UI):
if __name__ == "__main__":
    # Ingest issues from a repo
    count = ingest_github_issues("torvalds", "linux", token=None)
    print(f"Ingested {count} issues from Linux kernel repo")
