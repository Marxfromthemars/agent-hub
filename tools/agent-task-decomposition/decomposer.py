#!/usr/bin/env python3
"""
Task Decomposition Engine - AI Agent Skill
Implements the 4-part decomposition quality checklist from real-world analysis:
1. Explicit sub-components (not one big block)
2. Acceptance criteria per sub-component
3. Dependency map (which sub-component depends on which)
4. Blast-radius estimate per sub-component

Based on findings: 67% of agent rework traced to task decomposition quality
"""

import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SubComponent:
    """A single decomposable piece of a task"""
    id: str
    name: str
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    blast_radius: str = "medium"  # low, medium, high, critical
    estimated_effort: str = "medium"  # low, medium, high
    risks: List[str] = field(default_factory=list)


@dataclass
class DecompositionResult:
    """Complete task decomposition with quality metrics"""
    original_task: str
    sub_components: List[SubComponent]
    quality_score: float
    rework_risk: str  # low, medium, high
    recommendations: List[str]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TaskDecomposer:
    """Task decomposition engine with quality validation"""
    
    def __init__(self):
        self.quality_thresholds = {
            "low_risk": 0.8,
            "medium_risk": 0.6,
            "high_risk": 0.4
        }
    
    def decompose(self, task: str, context: Optional[Dict] = None) -> DecompositionResult:
        """
        Decompose a task into sub-components with quality validation.
        
        Args:
            task: The task to decompose
            context: Optional context (user goals, constraints, etc.)
            
        Returns:
            DecompositionResult with quality metrics
        """
        # Parse task into sub-components
        sub_components = self._parse_task(task)
        
        # Validate quality checklist
        quality_score = self._calculate_quality_score(sub_components)
        rework_risk = self._calculate_rework_risk(quality_score)
        recommendations = self._generate_recommendations(sub_components, quality_score)
        
        return DecompositionResult(
            original_task=task,
            sub_components=sub_components,
            quality_score=quality_score,
            rework_risk=rework_risk,
            recommendations=recommendations
        )
    
    def _parse_task(self, task: str) -> List[SubComponent]:
        """Parse task into explicit sub-components"""
        # Simple keyword-based parsing (can be enhanced with LLM)
        sentences = [s.strip() for s in re.split(r'[.;]\s*', task) if s.strip()]
        
        components = []
        for i, sentence in enumerate(sentences):
            if len(sentence) < 10:
                continue
                
            component = SubComponent(
                id=f"comp_{i+1}",
                name=self._extract_name(sentence),
                description=sentence,
                acceptance_criteria=self._extract_criteria(sentence),
                depends_on=self._extract_dependencies(sentences, i),
                blast_radius=self._estimate_blast_radius(sentence),
                estimated_effort=self._estimate_effort(sentence),
                risks=self._identify_risks(sentence)
            )
            components.append(component)
        
        # If single block, create explicit breakdown
        if len(components) == 1 and len(task.split()) > 20:
            components = self._split_large_task(task)
        
        return components
    
    def _extract_name(self, description: str) -> str:
        """Extract a short name for the component"""
        words = description.split()[:4]
        return "_".join(words).lower()[:30]
    
    def _extract_criteria(self, description: str) -> List[str]:
        """Extract acceptance criteria from description"""
        criteria = []
        
        # Look for explicit criteria markers
        if "must" in description.lower():
            must_phrases = re.findall(r'(\w+\s+must\s+[^\.]+)', description, re.IGNORECASE)
            criteria.extend([f"Must: {p.strip()}" for p in must_phrases])
        
        if "should" in description.lower():
            should_phrases = re.findall(r'(\w+\s+should\s+[^\.]+)', description, re.IGNORECASE)
            criteria.extend([f"Should: {p.strip()}" for p in should_phrases])
        
        # If no explicit criteria, generate from key actions
        if not criteria:
            verbs = ["validate", "check", "ensure", "verify", "create", "build", "test"]
            for verb in verbs:
                if verb in description.lower():
                    criteria.append(f"Verify: {verb} {description.lower().split(verb)[1].split()[0] if len(description.lower().split(verb)) > 1 else 'completion'}")
        
        return criteria[:5]  # Max 5 criteria
    
    def _extract_dependencies(self, sentences: List[str], current_idx: int) -> List[str]:
        """Extract dependencies from subsequent sentences"""
        deps = []
        current_lower = sentences[current_idx].lower()
        
        # Look for explicit references
        for i in range(current_idx):
            if any(word in sentences[i].lower() for word in ["first", "before", "prior", "prerequisite"]):
                deps.append(f"comp_{i+1}")
        
        # Look for contextual dependencies
        if "then" in current_lower or "after" in current_lower:
            if current_idx > 0:
                deps.append(f"comp_{current_idx}")
        
        return deps[:3]  # Max 3 dependencies
    
    def _estimate_blast_radius(self, description: str) -> str:
        """Estimate blast radius if this component fails"""
        critical_words = ["delete", "deploy", "publish", "execute", "run", "submit", "payment", "transaction"]
        high_words = ["write", "update", "modify", "change", "send", "notify"]
        
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in critical_words):
            return "critical"
        elif any(word in desc_lower for word in high_words):
            return "high"
        elif any(word in desc_lower for word in ["read", "check", "verify", "validate"]):
            return "low"
        else:
            return "medium"
    
    def _estimate_effort(self, description: str) -> str:
        """Estimate effort based on complexity"""
        word_count = len(description.split())
        
        if word_count < 15:
            return "low"
        elif word_count < 40:
            return "medium"
        else:
            return "high"
    
    def _identify_risks(self, description: str) -> List[str]:
        """Identify potential risks in this component"""
        risks = []
        desc_lower = description.lower()
        
        if "api" in desc_lower or "external" in desc_lower:
            risks.append("External dependency failure")
        if "database" in desc_lower or "storage" in desc_lower:
            risks.append("Data integrity risk")
        if "deploy" in desc_lower or "release" in desc_lower:
            risks.append("Rollback complexity")
        if "test" not in desc_lower and "verify" not in desc_lower:
            risks.append("No explicit validation")
        
        return risks
    
    def _split_large_task(self, task: str) -> List[SubComponent]:
        """Split a large task into explicit sub-components"""
        # Split by conjunctions and natural breaks
        segments = re.split(r',\s*(and|then|after|before)\s+', task)
        
        components = []
        for i, segment in enumerate(segments):
            segment = segment.strip()
            if len(segment) < 10:
                continue
                
            component = SubComponent(
                id=f"comp_{i+1}",
                name=self._extract_name(segment),
                description=segment,
                acceptance_criteria=self._extract_criteria(segment),
                depends_on=[f"comp_{i}"] if i > 0 else [],
                blast_radius=self._estimate_blast_radius(segment),
                estimated_effort=self._estimate_effort(segment),
                risks=self._identify_risks(segment)
            )
            components.append(component)
        
        return components
    
    def _calculate_quality_score(self, components: List[SubComponent]) -> float:
        """Calculate quality score based on checklist"""
        if not components:
            return 0.0
        
        score = 0.0
        
        # Criterion 1: Explicit sub-components (not one big block)
        # Score based on number of components (3+ is good)
        component_score = min(len(components) / 3.0, 1.0) if len(components) >= 3 else len(components) / 3.0
        score += component_score * 25
        
        # Criterion 2: Acceptance criteria per sub-component
        criteria_score = sum(
            min(len(c.acceptance_criteria) / 2.0, 1.0) 
            for c in components
        ) / max(len(components), 1)
        score += criteria_score * 25
        
        # Criterion 3: Dependency map (explicit dependencies)
        dep_score = sum(
            min(len(c.depends_on) / 2.0, 1.0) 
            for c in components
        ) / max(len(components), 1)
        score += dep_score * 25
        
        # Criterion 4: Blast-radius estimates
        blast_score = sum(
            1.0 if c.blast_radius in ["low", "medium"] else 0.5
            for c in components
        ) / max(len(components), 1)
        score += blast_score * 25
        
        return score / 100.0
    
    def _calculate_rework_risk(self, quality_score: float) -> str:
        """Calculate rework risk from quality score"""
        if quality_score >= self.quality_thresholds["low_risk"]:
            return "low"
        elif quality_score >= self.quality_thresholds["medium_risk"]:
            return "medium"
        else:
            return "high"
    
    def _generate_recommendations(self, components: List[SubComponent], quality_score: float) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if len(components) < 3:
            recommendations.append("Split task into 3+ explicit sub-components")
        
        has_criteria = any(c.acceptance_criteria for c in components)
        if not has_criteria:
            recommendations.append("Add explicit acceptance criteria per sub-component")
        
        has_deps = any(c.depends_on for c in components)
        if not has_deps:
            recommendations.append("Map dependencies between sub-components")
        
        critical_count = sum(1 for c in components if c.blast_radius == "critical")
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical blast-radius components first")
        
        if quality_score < 0.6:
            recommendations.append("Consider breaking down further before execution")
        
        return recommendations
    
    def to_json(self, result: DecompositionResult) -> Dict:
        """Convert result to JSON-serializable dict"""
        return {
            "original_task": result.original_task,
            "sub_components": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "acceptance_criteria": c.acceptance_criteria,
                    "depends_on": c.depends_on,
                    "blast_radius": c.blast_radius,
                    "estimated_effort": c.estimated_effort,
                    "risks": c.risks
                }
                for c in result.sub_components
            ],
            "quality_score": result.quality_score,
            "rework_risk": result.rework_risk,
            "recommendations": result.recommendations,
            "created_at": result.created_at
        }


def main():
    """CLI interface for task decomposition"""
    import sys
    
    # Example usage
    decomposer = TaskDecomposer()
    
    # Demo task
    demo_task = "Create a user authentication system with registration, login, password reset, and session management. Deploy to production with monitoring."
    
    result = decomposer.decompose(demo_task)
    output = decomposer.to_json(result)
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()