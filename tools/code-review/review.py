#!/usr/bin/env python3
"""Auto Code Review"""
import sys
issues = []
for line in open(sys.argv[1] if len(sys.argv)>1 else '/dev/stdin'):
    if 'TODO' in line: issues.append(('low','TODO found'))
    if 'FIXME' in line: issues.append(('high','FIXME found'))
    if len(line)>120: issues.append(('medium','Line too long'))
print(json.dumps(issues))
