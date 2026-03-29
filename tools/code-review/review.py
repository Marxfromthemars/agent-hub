#!/usr/bin/env python3
"""
ENHANCED CODE REVIEW TOOL - Comprehensive analysis
Detects bugs, security issues, performance problems, style issues
"""
import sys
import re
import json
from pathlib import Path

class CodeReview:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.issues = []
        self.stats = {
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "comments": 0,
            "blank": 0
        }
        self.language = None
    
    def analyze_file(self, filepath):
        """Full analysis of a code file"""
        self.filepath = Path(filepath)
        
        if not self.filepath.exists():
            return {"error": f"File not found: {filepath}"}
        
        content = self.filepath.read_text()
        lines = content.split('\n')
        self.stats["lines"] = len(lines)
        
        # Detect language
        ext = self.filepath.suffix
        self.language = self.detect_language(ext)
        
        # Analyze each line
        for i, line in enumerate(lines, 1):
            self.stats["lines"] += 1
            if line.strip() == '':
                self.stats["blank"] += 1
            elif line.strip().startswith('#') or line.strip().startswith('//'):
                self.stats["comments"] += 1
            
            self.check_issues(line, i)
        
        # Pattern-based analysis
        self.check_patterns(content)
        
        return self.get_results()
    
    def detect_language(self, ext):
        """Detect programming language from extension"""
        langs = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.go': 'Go',
            '.rs': 'Rust',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        return langs.get(ext, 'Unknown')
    
    def check_issues(self, line, line_num):
        """Check for issues in a single line"""
        line_stripped = line.strip()
        
        # Security issues
        if 'eval(' in line:
            self.add_issue('critical', 'Security: eval() usage detected', line_num, 'security')
        if 'exec(' in line and 'subprocess' not in line:
            self.add_issue('high', 'Security: exec() usage detected', line_num, 'security')
        if 'password' in line.lower() and '=' in line:
            self.add_issue('critical', 'Security: hardcoded password detected', line_num, 'security')
        if 'api_key' in line.lower() or 'secret' in line.lower():
            if '=' in line and not line.strip().startswith('#'):
                self.add_issue('critical', 'Security: potential API key leak', line_num, 'security')
        if 'http://' in line and 'localhost' not in line:
            self.add_issue('medium', 'Security: non-HTTPS URL detected', line_num, 'security')
        
        # Code quality
        if 'TODO' in line:
            self.add_issue('low', 'TODO comment found', line_num, 'quality')
        if 'FIXME' in line:
            self.add_issue('medium', 'FIXME comment found', line_num, 'quality')
        if 'HACK' in line:
            self.add_issue('medium', 'HACK comment found', line_num, 'quality')
        if 'XXX' in line:
            self.add_issue('low', 'XXX comment found', line_num, 'quality')
        
        # Style issues
        if len(line) > 120:
            self.add_issue('low', f'Line too long ({len(line)} chars)', line_num, 'style')
        if line_stripped and not line_stripped.endswith(':'):
            if line_stripped.endswith('{') or line_stripped.endswith('}'):
                self.add_issue('low', 'Opening brace on own line', line_num, 'style')
        
        # Performance
        if 'global ' in line and self.language == 'Python':
            self.add_issue('medium', 'Global variable usage detected', line_num, 'performance')
        if re.search(r'for.*in.*\.keys\(\)', line):
            self.add_issue('low', 'Unnecessary .keys() call', line_num, 'performance')
        if '.append(' in line and '[' in line:
            self.add_issue('low', 'Consider list comprehension', line_num, 'performance')
    
    def check_patterns(self, content):
        """Pattern-based analysis on full content"""
        # Count functions and classes
        if self.language == 'Python':
            funcs = len(re.findall(r'def \w+', content))
            classes = len(re.findall(r'class \w+', content))
            self.stats["functions"] = funcs
            self.stats["classes"] = classes
        elif self.language == 'Go':
            funcs = len(re.findall(r'func \w+', content))
            self.stats["functions"] = funcs
        
        # Check for common bugs
        if re.search(r'if.*==.*True|if.*==.*False', content):
            self.add_issue('medium', 'Unnecessary True/False comparison', 0, 'bug')
        
        # Check for missing error handling
        if 'open(' in content and 'try:' not in content:
            self.add_issue('high', 'File operations without try-except', 0, 'reliability')
        
        # Check for TODO without priority
        if '# TODO' in content and re.search(r'# TODO: [a-z]', content):
            pass  # Good - has description
        elif '# TODO' in content:
            self.add_issue('low', 'TODO without description', 0, 'quality')
    
    def add_issue(self, severity, message, line, category):
        """Add an issue to the list"""
        self.issues.append({
            "severity": severity,
            "message": message,
            "line": line,
            "category": category
        })
    
    def get_results(self):
        """Get analysis results"""
        # Severity scores
        severity_weights = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1
        }
        
        total_score = sum(severity_weights.get(i['severity'], 1) for i in self.issues)
        
        return {
            "filepath": str(self.filepath),
            "language": self.language,
            "stats": self.stats,
            "issues": self.issues,
            "summary": {
                "total": len(self.issues),
                "critical": len([i for i in self.issues if i['severity'] == 'critical']),
                "high": len([i for i in self.issues if i['severity'] == 'high']),
                "medium": len([i for i in self.issues if i['severity'] == 'medium']),
                "low": len([i for i in self.issues if i['severity'] == 'low']),
                "score": max(0, 100 - total_score)  # Higher = cleaner
            }
        }
    
    def print_report(self, results):
        """Print a formatted report"""
        print(f"\n📋 Code Review Report: {results['filepath']}")
        print(f"   Language: {results['language']}")
        print(f"\n📊 Stats:")
        print(f"   Lines: {results['stats']['lines']}")
        print(f"   Functions: {results['stats']['functions']}")
        print(f"   Classes: {results['stats']['classes']}")
        print(f"   Comments: {results['stats']['comments']}")
        
        summary = results['summary']
        print(f"\n📈 Quality Score: {summary['score']}/100")
        print(f"   Issues: {summary['total']} ({summary['critical']} critical, {summary['high']} high, {summary['medium']} medium, {summary['low']} low)")
        
        if summary['critical'] > 0:
            print("\n🚨 CRITICAL ISSUES:")
            for i in results['issues']:
                if i['severity'] == 'critical':
                    loc = f"Line {i['line']}" if i['line'] else "File-wide"
                    print(f"   [{loc}] {i['message']}")
        
        if summary['high'] > 0:
            print("\n⚠️  HIGH PRIORITY ISSUES:")
            for i in results['issues']:
                if i['severity'] == 'high':
                    loc = f"Line {i['line']}" if i['line'] else "File-wide"
                    print(f"   [{loc}] {i['message']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 review.py <filepath> [--json]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    json_output = '--json' in sys.argv
    
    review = CodeReview()
    results = review.analyze_file(filepath)
    
    if json_output:
        print(json.dumps(results, indent=2))
    else:
        review.print_report(results)
    
    # Exit with error code if critical issues found
    if results['summary']['critical'] > 0:
        sys.exit(2)
    elif results['summary']['score'] < 70:
        sys.exit(1)


if __name__ == "__main__":
    main()