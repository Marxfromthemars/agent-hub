"""
AGENT EVALUATOR - Assess agent capabilities and quality
Purpose: Help agents improve by identifying strengths and weaknesses
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

class AgentEvaluator:
    """Evaluate agent performance and provide improvement suggestions"""
    
    def __init__(self):
        self.evaluations = {}
        self.metrics = {
            "code_quality": 0.0,
            "research_quality": 0.0,
            "collaboration": 0.0,
            "reliability": 0.0,
            "innovation": 0.0,
            "communication": 0.0
        }
        
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "needs_work": 0.3
        }
    
    def evaluate_agent(self, agent_id: str, work_samples: List[Dict]) -> Dict:
        """Evaluate an agent based on work samples"""
        if not work_samples:
            return {"error": "No work samples provided"}
        
        scores = {}
        
        for sample in work_samples:
            sample_type = sample.get("type", "unknown")
            quality = sample.get("quality", 0.5)
            
            if sample_type == "code":
                scores["code_quality"] = max(scores.get("code_quality", 0), quality)
            elif sample_type == "research":
                scores["research_quality"] = max(scores.get("research_quality", 0), quality)
            elif sample_type == "collaboration":
                scores["collaboration"] = max(scores.get("collaboration", 0), quality)
        
        # Calculate overall score
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        
        # Determine rating
        if overall >= 0.9:
            rating = "excellent"
        elif overall >= 0.7:
            rating = "good"
        elif overall >= 0.5:
            rating = "fair"
        else:
            rating = "needs_work"
        
        evaluation = {
            "agent_id": agent_id,
            "scores": scores,
            "overall": overall,
            "rating": rating,
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": self._generate_suggestions(scores)
        }
        
        self.evaluations[agent_id] = evaluation
        return evaluation
    
    def _generate_suggestions(self, scores: Dict) -> List[str]:
        """Generate improvement suggestions based on scores"""
        suggestions = []
        
        for metric, score in scores.items():
            if score < 0.5:
                suggestions.append(f"Improve {metric.replace('_', ' ')}")
            elif score < 0.7:
                suggestions.append(f"Good {metric.replace('_', ' ')}, aim higher")
            else:
                suggestions.append(f"Excellent {metric.replace('_', ' ')}")
        
        return suggestions
    
    def compare_agents(self, agent1: str, agent2: str) -> Dict:
        """Compare two agents"""
        e1 = self.evaluations.get(agent1, {"overall": 0})
        e2 = self.evaluations.get(agent2, {"overall": 0})
        
        return {
            "agent1": agent1,
            "agent2": agent2,
            "agent1_score": e1.get("overall", 0),
            "agent2_score": e2.get("overall", 0),
            "winner": agent1 if e1.get("overall", 0) > e2.get("overall", 0) else agent2,
            "difference": abs(e1.get("overall", 0) - e2.get("overall", 0))
        }
    
    def get_top_agents(self, limit: int = 5) -> List[Dict]:
        """Get top-rated agents"""
        sorted_evals = sorted(
            self.evaluations.items(),
            key=lambda x: x[1].get("overall", 0),
            reverse=True
        )
        return [e[1] for e in sorted_evals[:limit]]
    
    def get_agent_report(self, agent_id: str) -> str:
        """Generate a human-readable report"""
        eval_data = self.evaluations.get(agent_id)
        
        if not eval_data:
            return f"No evaluation found for {agent_id}"
        
        lines = [
            f"\n=== Agent Evaluation Report: {agent_id} ===",
            f"Rating: {eval_data['rating'].upper()}",
            f"Overall Score: {eval_data['overall']:.2f}",
            f"Evaluated: {eval_data['timestamp']}",
            "\nScores:"
        ]
        
        for metric, score in eval_data.get("scores", {}).items():
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            lines.append(f"  {metric:20} {score:.2f} [{bar}]")
        
        lines.append("\nSuggestions:")
        for suggestion in eval_data.get("suggestions", []):
            lines.append(f"  • {suggestion}")
        
        return "\n".join(lines)


# Demo
if __name__ == "__main__":
    evaluator = AgentEvaluator()
    
    # Evaluate some agents
    print("=== Agent Evaluator Demo ===\n")
    
    # Marxagent
    result = evaluator.evaluate_agent("marxagent", [
        {"type": "code", "quality": 0.85},
        {"type": "research", "quality": 0.95},
        {"type": "collaboration", "quality": 0.80}
    ])
    print(f"Marxagent: {result['rating']} ({result['overall']:.2f})")
    
    # Researcher
    result = evaluator.evaluate_agent("researcher", [
        {"type": "research", "quality": 0.92},
        {"type": "code", "quality": 0.45},
        {"type": "collaboration", "quality": 0.78}
    ])
    print(f"Researcher: {result['rating']} ({result['overall']:.2f})")
    
    # Builder
    result = evaluator.evaluate_agent("builder", [
        {"type": "code", "quality": 0.88},
        {"type": "research", "quality": 0.55},
        {"type": "collaboration", "quality": 0.70}
    ])
    print(f"Builder: {result['rating']} ({result['overall']:.2f})")
    
    # Print reports
    print(evaluator.get_agent_report("marxagent"))
    
    # Compare
    print("\n" + evaluator.compare_agents("marxagent", "builder"))