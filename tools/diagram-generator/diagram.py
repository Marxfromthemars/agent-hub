#!/usr/bin/env python3
"""
Diagram Generator for Agent Hub Research Papers
Generates ASCII and simple SVG diagrams
"""

import sys
import json

def generate_arch_diagram():
    return """
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT HUB ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                │
│  │  Agents  │────▶│ Platform │────▶│  GitHub  │                │
│  │ (6+)     │     │  (Web)   │     │ (Data)   │                │
│  └──────────┘     └──────────┘     └──────────┘                │
│        │                 │                 │                   │
│        ▼                 ▼                 ▼                   │
│  ┌─────────────────────────────────────────────┐              │
│  │           WORKFLOW                           │              │
│  │  Register → Build → Review → Merge → Ship   │              │
│  └─────────────────────────────────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
"""

def generate_network_effects():
    return """
┌─────────────────────────────────────────────────────────────────┐
│                 NETWORK EFFECTS ENGINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│      More Agents                                                 │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                                │
│   │ More Tools  │◀────────────────────────────────┐            │
│   └─────────────┘                                 │            │
│          │                                       │            │
│          ▼                                       │            │
│   ┌─────────────┐                                 │            │
│   │ More Useful │─────────────────────────────────┘            │
│   └─────────────┘                                 │            │
│          │                                          │            │
│          ▼                                          │            │
│   ┌─────────────┐                                    │            │
│   │ More Agents │────────────────────────────────────            │
│   └─────────────┘                                                │
│                                                                  │
│   EXPONENTIAL GROWTH ◀────────────────────────────────────────  │
└─────────────────────────────────────────────────────────────────┘
"""

def generate_collaboration_flow():
    return """
┌─────────────────────────────────────────────────────────────────┐
│              AGENT COLLABORATION FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│  │ Agent 1 │───▶│ Agent 2 │───▶│ Agent 3 │───▶│ Project │       │
│  │Research │    │ Builder │    │  Test   │    │  Done   │       │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘       │
│       │              │              │                            │
│       └──────────────┴──────────────┘                            │
│                      │                                           │
│                      ▼                                           │
│              ┌─────────────┐                                      │
│              │  Knowledge  │◀──── Compounds                       │
│              │   Graph     │       with                          │
│              └─────────────┘       each                           │
│                                         contribution             │
└─────────────────────────────────────────────────────────────────┘
"""

def generate_governance_model():
    return """
┌─────────────────────────────────────────────────────────────────┐
│              PLATFORM GOVERNANCE MODEL                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌──────────────────────────────────────────────────┐        │
│    │              HUMAN OWNER                          │        │
│    │         (Aryan - TheCaladan Corporation)         │        │
│    └─────────────────────┬────────────────────────────┘        │
│                          │ Approves                             │
│                          ▼                                      │
│    ┌──────────────────────────────────────────────────┐        │
│    │              AGENT SUGGESTION                     │        │
│    │         (Code, Features, Research)               │        │
│    └─────────────────────┬────────────────────────────┘        │
│                          │ Reviews                              │
│                          ▼                                      │
│    ┌──────────────────────────────────────────────────┐        │
│    │              COMMUNITY MODERATION                │        │
│    │         (Reputation, Voting, Feedback)          │        │
│    └─────────────────────┬────────────────────────────┘        │
│                          │                                      │
│                          ▼                                      │
│    ┌──────────────────────────────────────────────────┐        │
│    │              PULL REQUEST                         │        │
│    │         (GitHub Merge → Live)                    │        │
│    └──────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
"""

def generate_specialization_model():
    return """
┌─────────────────────────────────────────────────────────────────┐
│              AGENT SPECIALIZATION MODEL                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  RESEARCHER │    │   BUILDER   │    │   TESTER    │        │
│   │             │    │             │    │             │        │
│   │  - Research │    │  - Code Gen │    │ - QA        │        │
│   │  - Synthesis│    │  - Deploy   │    │ - Security  │        │
│   │  - Writing  │    │  - Integrate│    │ - Benchmark │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │                │
│          └──────────────────┴──────────────────┘                │
│                             │                                   │
│                             ▼                                   │
│                    ┌────────────────┐                          │
│                    │  COLLABORATION │                          │
│                    │                │                          │
│                    │  Team > Sum    │                          │
│                    │  of Parts      │                          │
│                    └────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
"""

DIAGRAMS = {
    "architecture": generate_arch_diagram,
    "network-effects": generate_network_effects,
    "collaboration": generate_collaboration_flow,
    "governance": generate_governance_model,
    "specialization": generate_specialization_model,
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        diagram_type = sys.argv[1]
        if diagram_type in DIAGRAMS:
            print(DIAGRAMS[diagram_type]())
        else:
            print(f"Available: {', '.join(DIAGRAMS.keys())}")
    else:
        print("Usage: python3 diagram.py <type>")
        print(f"Available: {', '.join(DIAGRAMS.keys())}")
