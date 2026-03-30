#!/usr/bin/env python3
"""
Creative Engine for Agents
Generates novel solutions by exploring possibility spaces
"""

import random
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class CreativeEngine:
    """Generate creative solutions to problems"""
    
    def __init__(self):
        self.history = []
        self.novelty_threshold = 0.6
    
    def generate_solutions(self, problem: str, n: int = 5) -> List[Dict]:
        """Generate n novel solutions to a problem"""
        solutions = []
        
        # Strategy 1: Combination
        solutions.append(self._combine_existing(problem))
        
        # Strategy 2: Abstraction
        solutions.append(self._abstract_problem(problem))
        
        # Strategy 3: Opposite
        solutions.append(self._invert_assumptions(problem))
        
        # Strategy 4: Hybrid
        solutions.append(self._hybrid_domains(problem))
        
        # Strategy 5: First Principles
        solutions.append(self._first_principles(problem))
        
        self.history.append({
            "problem": problem,
            "solutions": solutions,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return solutions[:n]
    
    def _combine_existing(self, problem: str) -> Dict:
        return {
            "type": "combination",
            "description": f"Combine multiple existing approaches to solve: {problem}",
            "novelty_score": 0.6,
            "approach": "Find 3+ existing solutions and combine their strengths"
        }
    
    def _abstract_problem(self, problem: str) -> Dict:
        return {
            "type": "abstraction",
            "description": f"Abstract {problem} to its core essence",
            "novelty_score": 0.7,
            "approach": "Remove context, solve the general case, then specialize"
        }
    
    def _invert_assumptions(self, problem: str) -> Dict:
        return {
            "type": "inversion",
            "description": f"Invert the typical approach to {problem}",
            "novelty_score": 0.8,
            "approach": "What if the opposite of the usual solution worked?"
        }
    
    def _hybrid_domains(self, problem: str) -> Dict:
        return {
            "type": "cross_domain",
            "description": f"Apply solution from unrelated domain to {problem}",
            "novelty_score": 0.9,
            "approach": "Find how biology/physics/economics/etc solves similar problems"
        }
    
    def _first_principles(self, problem: str) -> Dict:
        return {
            "type": "first_principles",
            "description": f"Solve {problem} from first principles",
            "novelty_score": 0.95,
            "approach": "Break down to fundamental truths, rebuild solution"
        }
    
    def evaluate_novelty(self, solution: Dict) -> float:
        """Score how novel a solution is"""
        return solution.get("novelty_score", 0.5)
    
    def evaluate_utility(self, solution: Dict, context: Dict) -> float:
        """Score how useful a solution is"""
        base = 0.5
        if solution["type"] in context.get("preferred_types", []):
            base += 0.2
        return min(1.0, base + random.random() * 0.2)
    
    def refine_solution(self, solution: Dict, iterations: int = 3) -> Dict:
        """Iteratively improve a solution"""
        refined = solution.copy()
        for _ in range(iterations):
            # Add specificity
            refined["approach"] += f"\nRefinement iteration {_}: Consider edge cases"
            refined["novelty_score"] = min(1.0, refined["novelty_score"] + 0.05)
        return refined


if __name__ == "__main__":
    engine = CreativeEngine()
    solutions = engine.generate_solutions("How to improve agent collaboration")
    for s in solutions:
        print(f"  [{s['type']}] {s['description']}")
        print(f"    Novelty: {s['novelty_score']}")
