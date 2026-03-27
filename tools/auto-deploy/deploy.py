#!/usr/bin/env python3
"""Auto Deploy to GitHub Pages"""
import os, subprocess, json
print("Deploying to GitHub Pages...")
os.system("git add . && git commit -m 'Auto deploy' && git push origin main")
print("Done!")
