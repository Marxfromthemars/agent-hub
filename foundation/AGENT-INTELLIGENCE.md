# Agent Intelligence Model

> "Intelligence is not how much an agent knows.
It is how well it chooses what to do next."

---

## Core Loop

```
PERCEIVE → DECIDE → PLAN → ACT → EVALUATE → EVOLVE
```

---

## 1. PERCEPTION

Agent sees ONLY relevant tasks:
- Top 5 tasks (not everything)
- Related memory
- System state

---

## 2. DECISION (Most Important)

**Decision Formula:**
```
Score = (Impact × Success Probability × Urgency) / Cost
```

- Agent picks highest scored task
- If success probability < 0.3 → DECOMPOSE or ask for help

---

## 3. PLANNING

Convert task to executable steps:
- Short
- Executable  
- Verifiable

---

## 4. ACTION

Execute using tools:
- Produce measurable output
- Track token usage
- No "thinking for thinking"

---

## 5. EVALUATION

After acting, must check:
- Did I complete the task?
- Is output correct?
- Can it be improved?
- Did I waste resources?

Output: Success / Retry / Fail

---

## 6. EVOLUTION

Update:
- Memory (store lessons)
- Strategy (improve approach)
- Confidence (scale with success)

---

## Agent Types

| Agent | Role |
|-------|------|
| Planner | Break problems |
| Executor | Do work |
| Reviewer | Validate |
| Meta | Monitor efficiency |

---

## Collaboration Rules

1. Executor → Reviewer before finalizing
2. Ask for help when uncertain
3. Escalate failures to Planner

---

## Stop Conditions

- Max iterations (10)
- Token budget exceeded
- No progress
- Repeated failure

---

## Running at Port 8310

```bash
GET /intelligence/status     # Agent states
GET /intelligence/decide     # Test scoring
POST /intelligence/cycle     # Full intelligence cycle
```

---

*This is the brain of your world.*
