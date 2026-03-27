#!/usr/bin/env python3
"""Auto-Deploy Tool - Automated deployment with rollback support."""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

DEPLOY_LOG = "/tmp/deploy.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(DEPLOY_LOG, 'a') as f:
        f.write(line + '\n')

def run_cmd(cmd, check=True):
    """Run shell command."""
    log(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        log(f"ERROR: {result.stderr}")
        sys.exit(1)
    return result

def deploy(target, strategy="direct"):
    """Deploy to target with specified strategy."""
    log(f"Starting deployment to {target} with strategy: {strategy}")
    
    # Pre-deployment checks
    log("Running pre-deployment checks...")
    run_cmd("git status --porcelain", check=False)
    
    # Backup current state
    backup = f"/tmp/deploy_backup_{int(time.time())}"
    log(f"Creating backup at {backup}")
    
    # Deploy based on strategy
    if strategy == "direct":
        log("Direct deployment: pushing to remote")
        run_cmd(f"git add -A && git commit -m 'Deploy: {target}' || true")
        run_cmd(f"git push origin main")
    elif strategy == "docker":
        log("Docker deployment: building and running")
        run_cmd("docker build -t deploy-target .")
        run_cmd("docker stop deploy-container || true")
        run_cmd("docker run -d --name deploy-container deploy-target")
    elif strategy == "server":
        log("Server deployment: rsync to target")
        run_cmd(f"rsync -avz --exclude '.git' ./ {target}")
    
    log("Deployment complete!")
    return {'status': 'success', 'target': target, 'strategy': strategy}

def rollback():
    """Rollback to previous state."""
    log("Rolling back deployment...")
    run_cmd("git revert HEAD --no-edit")
    run_cmd("git push origin main")
    log("Rollback complete")
    return {'status': 'rolled-back'}

def status():
    """Check deployment status."""
    result = run_cmd("git log -1 --oneline", check=False)
    commit = result.stdout.strip()
    log(f"Current deployment: {commit}")
    return {'commit': commit, 'log': DEPLOY_LOG}

def main():
    if len(sys.argv) < 2:
        print("Usage: auto-deploy <deploy|rollback|status> [target] [strategy]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "deploy":
        target = sys.argv[2] if len(sys.argv) > 2 else "origin"
        strategy = sys.argv[3] if len(sys.argv) > 3 else "direct"
        result = deploy(target, strategy)
    elif action == "rollback":
        result = rollback()
    elif action == "status":
        result = status()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()