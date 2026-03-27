#!/usr/bin/env python3
"""Analyze platform data"""
import json, os
for f in os.listdir('data'):
    if f.endswith('.json'):
        with open(f'data/{f}') as j:
            d = json.load(j)
            print(f"{f}: {len(d.get('tools',d.get('agents',d.get('papers',[]))))} items")
