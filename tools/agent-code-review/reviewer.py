#!/usr/bin/env python3
"""
Agent Code Review System
Automated code review for agent-generated code.
"""

import json
from datetime import datetime
from pathlib import Path

class CodeReviewer:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.reviews_file = self.data_dir / "code_reviews.json"
        self.reviews = self._load_reviews()
    
    def _load_reviews(self):
        if self.reviews_file.exists():
            with open(self.reviews_file) as f:
                return json.load(f)
        return {"reviews": []}
    
    def _save_reviews(self):
        with open(self.reviews_file, 'w') as f:
            json.dump(self.reviews, f, indent=2)
    
    def review(self, code, language="python"):
        """Review code and provide feedback."""
        issues = []
        score = 100
        
        # Basic checks
        lines = code.split('\n')
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                issues.append({
                    "line": i,
                    "severity": "warning",
                    "type": "style",
                    "message": "Line exceeds 120 characters"
                })
                score -= 1
            
            # Check for TODO
            if "TODO" in line.upper():
                issues.append({
                    "line": i,
                    "severity": "info",
                    "type": "todo",
                    "message": "TODO comment found"
                })
                score -= 0.5
            
            # Check for hardcoded values
            if "password" in line.lower() or "secret" in line.lower():
                if "=" in line and ("'" in line or '"' in line):
                    issues.append({
                        "line": i,
                        "severity": "critical",
                        "type": "security",
                        "message": "Potential hardcoded secret detected"
                    })
                    score -= 10
        
        # Language-specific checks
        if language == "python":
            # Check for common Python issues
            if "except:" in code:
                issues.append({
                    "line": "N/A",
                    "severity": "warning",
                    "type": "best_practice",
                    "message": "Bare except clause - specify exception type"
                })
                score -= 3
            
            if "==" in code and "True" in code:
                issues.append({
                    "line": "N/A",
                    "severity": "info",
                    "type": "style",
                    "message": "Prefer 'if x:' over 'if x == True:'"
                })
                score -= 1
        
        review = {
            "id": f"review-{len(self.reviews['reviews']) + 1}",
            "timestamp": datetime.utcnow().isoformat(),
            "language": language,
            "lines": len(lines),
            "score": max(0, round(score, 1)),
            "issues": issues,
            "issues_count": len(issues)
        }
        
        self.reviews["reviews"].append(review)
        self._save_reviews()
        
        return review
    
    def get_reviews(self, limit=10):
        """Get recent reviews."""
        return self.reviews["reviews"][-limit:]
    
    def get_stats(self):
        """Get review statistics."""
        reviews = self.reviews["reviews"]
        if not reviews:
            return {"total": 0, "avg_score": 0}
        
        avg_score = sum(r["score"] for r in reviews) / len(reviews)
        issues_by_severity = {"critical": 0, "warning": 0, "info": 0}
        
        for r in reviews:
            for issue in r["issues"]:
                issues_by_severity[issue["severity"]] = issues_by_severity.get(issue["severity"], 0) + 1
        
        return {
            "total_reviews": len(reviews),
            "avg_score": round(avg_score, 1),
            "issues_by_severity": issues_by_severity
        }


def main():
    import sys
    reviewer = CodeReviewer()
    
    if len(sys.argv) < 2:
        print("Agent Code Review System")
        print("Usage: code-review.py <command> [args]")
        print("Commands:")
        print("  review <language> <code_file>")
        print("  reviews [limit]")
        print("  stats")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "review":
        language = sys.argv[2] if len(sys.argv) > 2 else "python"
        code_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        if code_file and Path(code_file).exists():
            code = Path(code_file).read_text()
        else:
            code = "def hello():\n    print('Hello, world!')\n    return True\n\nif hello() == True:\n    pass"
        
        result = reviewer.review(code, language)
        print(json.dumps(result, indent=2))
    
    elif cmd == "reviews":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        results = reviewer.get_reviews(limit)
        print(json.dumps(results, indent=2))
    
    elif cmd == "stats":
        result = reviewer.get_stats()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()