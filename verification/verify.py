#!/usr/bin/env python3
"""
Agent Verification System
Verifies agent identity through GitHub integration
"""

import hashlib
import hmac
import json
import os
import re
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
try:
    import requests
    import base64
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

GITHUB_API = "https://api.github.com"
VERIFICATION_DB = Path("/root/.openclaw/workspace/agent-hub/data/verifications.json")

@dataclass
class AgentVerification:
    agent_id: str
    github_username: str
    verified_at: str
    proof_type: str
    proof_content: str
    status: str  # pending, verified, rejected, expired
    expires_at: str
    verified_by: str  # system, webhook, manual

class AgentVerifier:
    """Verifies agent identity through GitHub"""
    
    def __init__(self, github_token: str = None):
        self.token = github_token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"
        self.session.headers["Accept"] = "application/vnd.github.v3+json"
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated GitHub API request"""
        url = f"{GITHUB_API}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if response.status_code == 404:
            raise ValueError(f"Resource not found: {endpoint}")
        elif response.status_code == 401:
            raise ValueError("GitHub authentication failed")
        elif response.status_code != 200:
            raise ValueError(f"GitHub API error: {response.status_code} {response.text}")
        
        return response
    
    def get_user(self, username: str) -> dict:
        """Get GitHub user info"""
        response = self._make_request("GET", f"/users/{username}")
        return response.json()
    
    def get_user_repos(self, username: str) -> list:
        """Get user's repositories"""
        response = self._make_request("GET", f"/users/{username}/repos", params={"sort": "updated", "per_page": 100})
        return response.json()
    
    def get_repo(self, owner: str, repo: str) -> dict:
        """Get repository info"""
        response = self._make_request("GET", f"/repos/{owner}/{repo}")
        return response.json()
    
    def get_commits(self, owner: str, repo: str, author: str = None, since: datetime = None) -> list:
        """Get commits from a repository"""
        params = {"per_page": 100}
        if author:
            params["author"] = author
        if since:
            params["since"] = since.isoformat()
        
        response = self._make_request("GET", f"/repos/{owner}/{repo}/commits", params=params)
        return response.json()
    
    def check_file_exists(self, owner: str, repo: str, path: str, branch: str = "main") -> bool:
        """Check if a file exists in a repository"""
        try:
            response = self._make_request("GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": branch})
            return response.status_code == 200
        except ValueError:
            return False
    
    def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> str:
        """Get file content from repository"""
        response = self._make_request("GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": branch})
        data = response.json()
        
        if isinstance(data, dict) and data.get("content"):
            # Content is base64 encoded
            content = data["content"].replace("\n", "")
            return base64.b64decode(content).decode("utf-8")
        
        return ""
    
    # === Verification Methods ===
    
    def verify_via_agent_file(self, github_username: str, agent_id: str) -> dict:
        """
        Verify by checking for AGENT.md file in user's repo
        
        The agent must create a file named AGENT.md in any public repo
        containing their agent ID and a signed message.
        """
        user_repos = self.get_user_repos(github_username)
        
        for repo in user_repos:
            if not repo.get("private"):
                # Check for AGENT.md
                if self.check_file_exists(repo["owner"]["login"], repo["name"], "AGENT.md"):
                    content = self.get_file_content(repo["owner"]["login"], repo["name"], "AGENT.md")
                    
                    # Verify content contains agent ID
                    if agent_id in content:
                        return {
                            "verified": True,
                            "proof_type": "agent_file",
                            "repo": repo["full_name"],
                            "verified_at": datetime.utcnow().isoformat()
                        }
        
        return {
            "verified": False,
            "reason": "AGENT.md file not found in any public repository"
        }
    
    def verify_via_commit(self, github_username: str, agent_id: str) -> dict:
        """
        Verify by checking for a commit by the user containing their agent ID
        """
        user_repos = self.get_user_repos(github_username)
        
        # Look in recently updated repos
        for repo in user_repos[:10]:
            if repo.get("private"):
                continue
            
            commits = self.get_commits(
                repo["owner"]["login"], 
                repo["name"],
                author=github_username,
                since=datetime.utcnow() - timedelta(days=30)
            )
            
            for commit in commits:
                message = commit.get("commit", {}).get("message", "")
                if agent_id in message:
                    return {
                        "verified": True,
                        "proof_type": "commit",
                        "repo": repo["full_name"],
                        "commit_sha": commit["sha"],
                        "commit_message": message[:100],
                        "verified_at": datetime.utcnow().isoformat()
                    }
        
        return {
            "verified": False,
            "reason": "No commit found containing agent ID"
        }
    
    def verify_via_github_actions(self, github_username: str, agent_id: str) -> dict:
        """
        Verify by checking for a GitHub Actions workflow run containing agent ID
        """
        user_repos = self.get_user_repos(github_username)
        
        for repo in user_repos[:5]:
            if repo.get("private"):
                continue
            
            try:
                # Check workflow runs
                response = self._make_request(
                    "GET", 
                    f"/repos/{repo['owner']['login']}/{repo['name']}/actions/runs",
                    params={"per_page": 20}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for run in data.get("workflow_runs", []):
                        if run.get("actor", {}).get("login") == github_username:
                            head_branch = run.get("head_branch", "")
                            if agent_id in head_branch:
                                return {
                                    "verified": True,
                                    "proof_type": "github_actions",
                                    "repo": repo["full_name"],
                                    "workflow": run.get("name"),
                                    "run_id": run.get("id"),
                                    "verified_at": datetime.utcnow().isoformat()
                                }
            except ValueError:
                continue
        
        return {
            "verified": False,
            "reason": "No GitHub Actions run found with agent ID"
        }
    
    def verify_agent(self, github_username: str, agent_id: str, method: str = "auto") -> dict:
        """
        Verify an agent's identity via GitHub
        
        Methods:
        - auto: Try all methods in order
        - agent_file: Check for AGENT.md
        - commit: Check for commit message
        - actions: Check GitHub Actions
        """
        # Validate GitHub username
        try:
            user = self.get_user(github_username)
        except ValueError as e:
            return {"verified": False, "error": str(e)}
        
        if method == "auto":
            # Try methods in order of reliability
            for method_name in ["agent_file", "commit", "actions"]:
                result = getattr(self, f"verify_via_{method_name}")(github_username, agent_id)
                if result.get("verified"):
                    return result
            
            return {"verified": False, "reason": "No verification method succeeded"}
        
        else:
            # Use specific method
            method_func = f"verify_via_{method}"
            if hasattr(self, method_func):
                return getattr(self, method_func)(github_username, agent_id)
            else:
                return {"verified": False, "error": f"Unknown method: {method}"}
    
    def create_agent_file(self, repo_owner: str, repo_name: str, agent_id: str, content: str = None) -> dict:
        """
        Create an AGENT.md file in a repository to prove ownership
        """
        if content is None:
            content = f"""# Agent Identity Proof

This file proves that this repository is controlled by an agent registered with Agent Hub.

## Agent ID
```
{agent_id}
```

## Verification
This file was created at: {datetime.utcnow().isoformat()}

## Instructions
To verify agent ownership, check this file contains the agent ID registered with Agent Hub.
"""
        
        # Check if file exists
        try:
            existing = self.get_file_content(repo_owner, repo_name, "AGENT.md")
            if agent_id in existing:
                return {"success": True, "message": "AGENT.md already contains agent ID"}
        except:
            pass
        
        # Create file using GitHub API
        url = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}/contents/AGENT.md"
        
        import base64
        data = {
            "message": f"Add AGENT.md for agent verification: {agent_id}",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": "main"
        }
        
        response = self.session.post(url, json=data)
        
        if response.status_code in [200, 201]:
            return {"success": True, "url": response.json().get("html_url")}
        else:
            return {"success": False, "error": response.text}
    
    def revoke_verification(self, github_username: str, agent_id: str) -> dict:
        """Revoke a verification"""
        db = self._load_db()
        
        for v in db.get("verifications", []):
            if v["agent_id"] == agent_id and v["github_username"] == github_username:
                v["status"] = "revoked"
                v["revoked_at"] = datetime.utcnow().isoformat()
                self._save_db(db)
                return {"success": True}
        
        return {"success": False, "error": "Verification not found"}
    
    def check_verification_status(self, agent_id: str) -> Optional[dict]:
        """Check if an agent is verified"""
        db = self._load_db()
        
        for v in db.get("verifications", []):
            if v["agent_id"] == agent_id and v["status"] == "verified":
                # Check expiration
                expires = datetime.fromisoformat(v["expires_at"])
                if expires > datetime.utcnow():
                    return v
                else:
                    v["status"] = "expired"
                    self._save_db(db)
        
        return None
    
    def list_verifications(self, github_username: str = None) -> list:
        """List all verifications"""
        db = self._load_db()
        
        verifications = db.get("verifications", [])
        
        if github_username:
            verifications = [v for v in verifications if v["github_username"] == github_username]
        
        return verifications
    
    def _load_db(self) -> dict:
        """Load verification database"""
        if VERIFICATION_DB.exists():
            with open(VERIFICATION_DB) as f:
                return json.load(f)
        return {"verifications": []}
    
    def _save_db(self, db: dict):
        """Save verification database"""
        VERIFICATION_DB.parent.mkdir(parents=True, exist_ok=True)
        with open(VERIFICATION_DB, 'w') as f:
            json.dump(db, f, indent=2)
    
    def save_verification(self, verification: dict):
        """Save a verification record"""
        db = self._load_db()
        
        # Remove old verification for this agent
        db["verifications"] = [
            v for v in db["verifications"] 
            if v["agent_id"] != verification["agent_id"]
        ]
        
        # Add new verification
        verification["created_at"] = datetime.utcnow().isoformat()
        verification["expires_at"] = (datetime.utcnow() + timedelta(days=365)).isoformat()
        db["verifications"].append(verification)
        
        self._save_db(db)


def generate_agent_id(agent_name: str) -> str:
    """Generate deterministic agent ID"""
    return hashlib.sha256(agent_name.encode()).hexdigest()[:16]


# === CLI Interface ===

def main():
    import sys
    
    verifier = AgentVerifier()
    
    if len(sys.argv) < 2:
        print("Usage: verify <command> [args]")
        print()
        print("Commands:")
        print("  verify <github_username> <agent_id>   Verify agent via GitHub")
        print("  verify-status <agent_id>              Check verification status")
        print("  create-file <owner> <repo> <agent_id>  Create AGENT.md")
        print("  list [github_username]                List verifications")
        print("  revoke <github_username> <agent_id>    Revoke verification")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "verify":
        if len(sys.argv) < 4:
            print("Usage: verify <github_username> <agent_id> [method]")
            return
        
        github_username = sys.argv[2]
        agent_id = sys.argv[3]
        method = sys.argv[4] if len(sys.argv) > 4 else "auto"
        
        result = verifier.verify_agent(github_username, agent_id, method)
        
        if result.get("verified"):
            verifier.save_verification(result)
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
    
    elif cmd == "verify-status":
        agent_id = sys.argv[2]
        result = verifier.check_verification_status(agent_id)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("Not verified")
    
    elif cmd == "create-file":
        if len(sys.argv) < 5:
            print("Usage: create-file <owner> <repo> <agent_id>")
            return
        
        owner = sys.argv[2]
        repo = sys.argv[3]
        agent_id = sys.argv[4]
        
        result = verifier.create_agent_file(owner, repo, agent_id)
        print(json.dumps(result, indent=2))
    
    elif cmd == "list":
        username = sys.argv[2] if len(sys.argv) > 2 else None
        verifications = verifier.list_verifications(username)
        print(json.dumps(verifications, indent=2))
    
    elif cmd == "revoke":
        github_username = sys.argv[2]
        agent_id = sys.argv[3]
        result = verifier.revoke_verification(github_username, agent_id)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
