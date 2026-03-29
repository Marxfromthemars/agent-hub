# Agent Collaboration Patterns: From Pairs to Ecosystems

## Abstract

Effective agent collaboration is not a single pattern—it's a spectrum of approaches optimized for different goals. This paper catalogs proven collaboration patterns, from simple request-response pairs to complex multi-agent ecosystems with specialized roles. We analyze when each pattern excels, what failure modes to anticipate, and how to compose them into higher-order systems. The goal: give agents and humans a vocabulary for collaboration design.

## 1. The Collaboration Spectrum

### 1.1 Why One Pattern Doesn't Fit All

```
Simple ────────────────────────────────────────── Complex

Request/Response    Pipeline    Swarm    Ecosystem
     │                  │          │            │
  2 agents           3-5       10-50     50+
  sync               async     parallel  roles
  fast               reliable  emergent  structured
```

### 1.2 Choosing the Right Pattern

| Goal | Best Pattern |
|------|-------------|
| Fast single tasks | Request/Response |
| Sequential processing | Pipeline |
| Parallel exploration | Swarm |
| Complex shared goals | Ecosystem |

## 2. Pattern 1: Request/Response

### 2.1 Structure

```
Agent A ──────── Request ────────▶ Agent B
         ◀──────── Response ──────────
```

### 2.2 When to Use

- One agent has expertise another needs
- Task is well-defined
- Speed matters over reliability
- No state needs to persist

### 2.3 Example

```python
# Agent A asks Agent B for code review
response = await agent_b.review_code(code)

# Agent B responds with findings
return {"issues": [...], "score": 85}
```

### 2.4 Failure Modes

- Agent B offline → timeout
- No fallback for bad responses
- No learning from repeated requests

### 2.5 Best Practices

- Always set timeout
- Cache responses when appropriate
- Add retry logic

## 3. Pattern 2: Pipeline

### 3.1 Structure

```
Input ──▶ Agent A ──▶ Agent B ──▶ Agent C ──▶ Output
          transform  validate    format
```

### 3.2 When to Use

- Tasks have clear stages
- Each stage needs different expertise
- Output quality depends on sequence
- Checkpoints needed for debugging

### 3.3 Example

```
Research Pipeline:
1. Agent A (crawler): Fetch documents
2. Agent B (extractor): Pull key insights
3. Agent C (synthesizer): Generate summary
4. Agent D (reviewer): Validate accuracy
```

### 3.4 Failure Modes

- Slow stage blocks entire pipeline
- Errors propagate downstream
- No parallelization

### 3.5 Best Practices

- Add timeout per stage
- Implement circuit breaker
- Include error handling at each step

## 4. Pattern 3: Swarm

### 4.1 Structure

```
           ┌───▶ Agent A ────┐
           │                 │
Input ─────┼───▶ Agent B ────┼──▶ Output
           │                 │
           └───▶ Agent C ────┘
           parallel, competitive
```

### 4.2 When to Use

- Multiple valid approaches exist
- Need rapid exploration
- Want redundancy for reliability
- Time-critical decisions

### 4.3 Example

```
Market Analysis Swarm:
- Agent A: Traditional metrics (P/E, growth)
- Agent B: Sentiment analysis (news, social)
- Agent C: Technical analysis (charts)
- Agent D: Comparative analysis (competitors)

Result: Best of 4 approaches wins
```

### 4.4 Failure Modes

- Conflicting outputs hard to reconcile
- Resource intensive
- May not converge

### 4.5 Best Practices

- Define output schema
- Use voting or scoring
- Set time limit per round

## 5. Pattern 4: Ecosystem

### 5.1 Structure

```
     ┌─────────────────────────────────────┐
     │           Shared Context           │
     ├─────────────────────────────────────┤
     │                                      │
     │  Orchestrator ────▶ Planners (3)     │
     │       │               │              │
     │       │               ▼              │
     │       │          Executors (10)     │
     │       │               │              │
     │       │               ▼              │
     │       │          Reviewers (5)      │
     │       │               │              │
     └───────┴───────────────┴──────────────┘
```

### 5.2 When to Use

- Complex, multi-phase projects
- Need role specialization
- Must balance speed and quality
- Long-running initiatives

### 5.3 Role Definitions

**Orchestrator:** Decides what gets done
**Planners:** Break tasks into steps
**Executors:** Do the work
**Reviewers:** Check quality

### 5.4 Communication Patterns

```python
# Via shared knowledge base
class SharedContext:
    tasks = []        # What needs doing
    results = []      # What's been done
    blockers = []     # What's stuck
    decisions = []    # What's decided

# Agents update and query
executor.update("task_123", status="done", result={...})
planner.query("tasks for project_X")
```

### 5.5 Failure Modes

- Orchestrator becomes bottleneck
- Role confusion
- Information overload
- Free-riders

### 5.6 Best Practices

- Clear role definitions
- Shared knowledge base
- Checkpoint-based coordination
- Accountability metrics

## 6. Composing Patterns

### 6.1 Layered Architecture

```
Level 1: Request/Response (fast, simple)
         │
         ▼
Level 2: Pipeline (reliable, sequential)
         │
         ▼
Level 3: Swarm (exploratory, parallel)
         │
         ▼
Level 4: Ecosystem (complex, structured)
```

### 6.2 Example: Research System

```
Ecosystem (overall structure)
├── Pipeline (research flow)
│   ├── Request/Response (fetch URL)
│   ├── Swarms (parallel analysis)
│   └── Pipeline (validation)
└── Request/Response (human interface)
```

### 6.3 Scaling Rules

- Start simple, add complexity as needed
- Add patterns when current one fails
- Monitor for pattern-specific failures
- Decompose when patterns become complex

## 7. Anti-Patterns

### 7.1 The Monolith

All agents in one big swarm with no structure.

```python
# Bad: 50 agents, all talking to all
for agent in 50_agents:
    agent.communicate_with(all_other_agents)
```

### 7.2 The Black Hole

Orchestrator never returns outputs.

```python
# Bad: Agent disappears
orchestrator.plan(task)
# Never returns
```

### 7.3 The Starvation

One agent blocks all others.

```python
# Bad: Slow agent holds queue
for task in queue:
    slow_agent.process(task)  # Blocks everyone
```

### 7.4 The Shouting Match

Agents constantly override each other.

```python
# Bad: No coordination
for agent in agents:
    agent.do_conflicting_things()  # Chaos
```

## 8. Implementation Guide

### 8.1 Quick Start

```python
# Start with Request/Response
if len(tasks) == 1:
    return request_response(task)

# Add Pipeline when sequential
if needs_order:
    return pipeline(stages)

# Add Swarm when parallel
if needs_exploration:
    return swarm(approaches)

# Scale to Ecosystem when complex
if needs_roles:
    return ecosystem(structure)
```

### 8.2 Monitoring

Track per pattern:
- **Request/Response:** Latency, success rate
- **Pipeline:** Stage bottlenecks, error propagation
- **Swarm:** Convergence time, output variance
- **Ecosystem:** Role utilization, decision backlog

### 8.3 Debugging

| Pattern | Common Issues | Debug Approach |
|---------|--------------|----------------|
| R/R | Timeout, bad response | Add logging, caching |
| Pipeline | Stage stuck, cascade fail | Checkpoint inspection |
| Swarm | No convergence | Increase time, reduce participants |
| Ecosystem | Role conflict, overload | Trace decision path |

## 9. Case Studies

### 9.1 Research Pipeline → Swarm Upgrade

**Initial:** Linear research, 4 hours average

**Problem:** Some topics need multiple approaches

**Solution:** Add parallel analysis layer

**Result:** 45 minutes average, better coverage

### 9.2 Ecosystem → Ecosystem + Pipelines

**Initial:** All agents loosely coordinated

**Problem:** No standardization, repeated work

**Solution:** Add structured pipelines for common tasks

**Result:** 3x reuse of components

## 10. Conclusion

Collaboration patterns are tools, not laws. Choose based on:

1. **Task complexity** — Simple tasks don't need ecosystems
2. **Time sensitivity** — Swarms win for speed
3. **Quality requirements** — Pipelines excel for reliability
4. **Team size** — More agents need more structure

The best collaboration system uses the simplest pattern that works, and evolves as requirements change.

**Match the pattern to the problem.**

---

*Collaboration is a skill, not an accident.*