#!/usr/bin/env python3
"""Data Analyzer Tool - Analyze datasets and generate insights."""

import os
import sys
import json
import csv
from collections import Counter, defaultdict

def analyze_csv(filepath):
    """Analyze CSV file."""
    rows = []
    headers = []
    
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            for row in reader:
                rows.append(row)
    except Exception as e:
        return {'error': str(e)}
    
    if not rows:
        return {'error': 'Empty file'}
    
    # Basic stats
    stats = {
        'rows': len(rows),
        'columns': len(headers),
        'headers': headers
    }
    
    # Column analysis
    column_analysis = {}
    for col in headers:
        values = [r.get(col, '') for r in rows]
        non_empty = [v for v in values if v]
        
        col_stats = {
            'non_empty': len(non_empty),
            'empty': len(values) - len(non_empty),
            'unique': len(set(non_empty))
        }
        
        # Detect type
        try:
            nums = [float(v) for v in non_empty if v.replace('.', '').replace('-', '').isdigit()]
            if len(nums) > len(non_empty) * 0.5:
                col_stats['type'] = 'numeric'
                col_stats['min'] = min(nums) if nums else None
                col_stats['max'] = max(nums) if nums else None
                col_stats['avg'] = sum(nums) / len(nums) if nums else None
            else:
                col_stats['type'] = 'text'
                col_stats['top_values'] = Counter(non_empty).most_common(5)
        except:
            col_stats['type'] = 'text'
            col_stats['top_values'] = Counter(non_empty).most_common(5)
        
        column_analysis[col] = col_stats
    
    return {'stats': stats, 'columns': column_analysis}

def analyze_json(filepath):
    """Analyze JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return {'error': str(e)}
    
    if isinstance(data, list):
        return {
            'type': 'array',
            'length': len(data),
            'sample': data[:3] if len(data) > 3 else data
        }
    elif isinstance(data, dict):
        return {
            'type': 'object',
            'keys': list(data.keys()),
            'nested_depth': get_depth(data)
        }
    
    return {'type': 'unknown'}

def get_depth(obj, depth=0):
    """Get nesting depth of object."""
    if isinstance(obj, dict):
        return max([get_depth(v, depth+1) for v in obj.values()], default=depth+1)
    elif isinstance(obj, list):
        return max([get_depth(i, depth+1) for i in obj], default=depth+1)
    return depth

def main():
    if len(sys.argv) < 2:
        print("Usage: data-analyzer <file.csv|file.json>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.csv':
        result = analyze_csv(filepath)
    elif ext == '.json':
        result = analyze_json(filepath)
    else:
        print(f"Unsupported file type: {ext}")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()