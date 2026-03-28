# FOUNDATION - Multi-Agent Problem Solver

## Final Truth

> "If you try to build the 'world': You fail.
> If you build: A system where 3 agents can reliably solve problems: You win."

---

## What We Built

A system where **3 agents can reliably solve problems**:

| Agent | Role | Does |
|-------|------|------|
| Planner | Breaks problem into tasks | Decomposes |
| Executor | Does the work | Executes |
| Reviewer | Validates result | Quality checks |

---

## How It Works

1. **Create task** → Task added to queue
2. **Planner** → Observes, thinks, breaks into subtasks
3. **Executor** → Assigned, executes, produces result
4. **Reviewer** → Validates quality (≥50 = pass)

---

## Constraints Enforced

- Max 10 cycles per task (prevents infinite loops)
- Quality threshold 50% (validates result)
- Every action tied to task

---

## Systems (Ports 8301-8304)

- 8301: Identity - entities with reputation
- 8302: Task Engine - create, assign, execute, review
- 8303: Memory - store and retrieve
- 8304: Runtime - 3 working agents

---

*Not a world. A problem-solving system.*
