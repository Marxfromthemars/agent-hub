#!/usr/bin/env python3
"""
Agent Security Scanner
Scans agent code for security vulnerabilities.
"""

import json
import re
from datetime import datetime
from pathlib import Path

class SecurityScanner:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.findings_file = self.data_dir / "security_findings.json"
        self.findings = self._load_findings()
    
    def _load_findings(self):
        if self.findings_file.exists():
            with open(self.findings_file) as f:
                return json.load(f)
        return {"findings": [], "by_severity": {}}
    
    def _save_findings(self):
        with open(self.findings_file, 'w') as f:
            json.dump(self.findings, f, indent=2)
    
    def scan_code(self, code, language="python"):
        """Scan code for security issues."""
        issues = []
        
        # Security patterns to check
        patterns = [
            {"pattern": r"password\s*=\s*['\"][^'\"]+['\"]", "severity": "critical", "type": "hardcoded_password", "msg": "Hardcoded password found"},
            {"pattern": r"api_?key\s*=\s*['\"][^'\"]+['\"]", "severity": "critical", "type": "hardcoded_api_key", "msg": "Hardcoded API key found"},
            {"pattern": r"secret\s*=\s*['\"][^'\"]+['\"]", "severity": "critical", "type": "hardcoded_secret", "msg": "Hardcoded secret found"},
            {"pattern": r"eval\s*\(", "severity": "high", "type": "code_injection", "msg": "eval() can be dangerous"},
            {"pattern": r"exec\s*\(", "severity": "high", "type": "code_injection", "msg": "exec() can be dangerous"},
            {"pattern": r"os\.system\s*\(", "severity": "high", "type": "command_injection", "msg": "os.system() can allow command injection"},
            {"pattern": r"subprocess\.call\s*\([^,)]*\s+shell\s*=\s*True", "severity": "high", "type": "command_injection", "msg": "shell=True is dangerous"},
            {"pattern": r"SQL\s*.*SELECT.*\+", "severity": "high", "type": "sql_injection", "msg": "Potential SQL injection"},
            {"pattern": r"requests\.get\s*\([^)]*\+", "severity": "medium", "type": "ssrf", "msg": "Potential SSRF via URL concatenation"},
            {"pattern": r"random\.random\(\)", "severity": "medium", "type": "weak_random", "msg": "random.random() is not cryptographically secure"},
            {"pattern": r"file\s*=\s*open\([^)]*mode\s*=\s*['\"]w", "severity": "low", "type": "file_write", "msg": "Check file write permissions"},
        ]
        
        for match in re.finditer(r'(.*)', code):
            line = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            
            for p in patterns:
                if re.search(p["pattern"], line, re.IGNORECASE):
                    issues.append({
                        "line": line_num,
                        "severity": p["severity"],
                        "type": p["type"],
                        "message": p["msg"],
                        "code": line.strip()[:80]
                    })
        
        finding = {
            "id": f"sec-{len(self.findings['findings']) + 1}",
            "language": language,
            "lines_scanned": len(code.split('\n')),
            "issues": issues,
            "issue_count": len(issues),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.findings["findings"].append(finding)
        self._save_findings()
        
        return finding
    
    def get_findings(self, severity=None):
        """Get security findings."""
        if severity:
            return [f for f in self.findings["findings"] if any(i["severity"] == severity for i in f["issues"])]
        return self.findings["findings"]
    
    def get_summary(self):
        """Get security summary."""
        total_issues = sum(f["issue_count"] for f in self.findings["findings"])
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for f in self.findings["findings"]:
            for i in f["issues"]:
                by_severity[i["severity"]] = by_severity.get(i["severity"], 0) + 1
        
        return {
            "total_scans": len(self.findings["findings"]),
            "total_issues": total_issues,
            "by_severity": by_severity
        }


def main():
    import sys
    scanner = SecurityScanner()
    
    if len(sys.argv) < 2:
        print("Agent Security Scanner")
        print("Usage: security-scanner.py <command> [args]")
        print("Commands:")
        print("  scan <language> [code_file]")
        print("  findings [severity]")
        print("  summary")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "scan":
        language = sys.argv[2] if len(sys.argv) > 2 else "python"
        code_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        if code_file and Path(code_file).exists():
            code = Path(code_file).read_text()
        else:
            code = "password = 'secret123'\neval(user_input)"
        
        result = scanner.scan_code(code, language)
        print(json.dumps(result, indent=2))
    
    elif cmd == "findings":
        severity = sys.argv[2] if len(sys.argv) > 2 else None
        result = scanner.get_findings(severity)
        print(json.dumps(result, indent=2))
    
    elif cmd == "summary":
        result = scanner.get_summary()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()