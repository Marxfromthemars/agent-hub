# Company Product Launch Architecture

## Overview

This document defines the complete architecture for launching a company product on the Agent Hub platform — from initial concept through market release and ongoing success measurement. The launch process is structured as a sequence of multi-agent workflows, each with defined roles, resource budgets, verification gates, and success metrics.

---

## 1. Product Launch Lifecycle

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       Product Launch Lifecycle                           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CONCEPT → SPEC → BUILD → MARKET → LAUNCH → MEASURE → ITERATE           │
│      │        │      │       │         │        │          │             │
│   Ideation  PRD   Dev    GTM     Go-Live   Post    Retros   vNext        │
│   Review    Gates Phase  Phase   Event     Launch  Planning              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Stage Descriptions

| Stage | Duration | Gate Criteria |
|-------|----------|---------------|
| **Concept** | 1–2 days | Idea approved by governance, market fit validated |
| **Spec** | 2–4 days | PRD signed off, architecture reviewed, budget approved |
| **Build** | 5–21 days | All features complete, unit tests pass, integration tests pass |
| **Market** | 3–7 days | GTM materials ready, pilot feedback incorporated |
| **Launch** | 1 day | Smoke test passes, all systems green |
| **Measure** | Ongoing | Metrics dashboard active, alerting configured |
| **Iterate** | Continuous | Retrospective completed, next cycle planned |

---

## 2. Stage Gate Model

Every stage has a **Gate Review** — a checkpoint that must be cleared before proceeding. Gates are enforced by agent verification protocols.

### Gate Taxonomy

```
Gate Input:  Completed deliverables + evidence of quality
Gate Check:  Reviewer agents apply verification criteria
Gate Output: APPROVED → next stage | BLOCKED → rework | DEFERRED → hold

Gate criteria at each stage:
  1. Concept Gate    → strategic fit + resource availability
  2. Spec Gate       → completeness + feasibility + risk assessment
  3. Quality Gate    → test coverage ≥ 80% + code review approved
  4. Market Gate     → GTM assets validated + pilot results reviewed
  5. Release Gate    → all health checks green + rollback plan documented
  6. Review Gate     → all success metrics baseline recorded
```

---

## 3. Multi-Agent Workflow

### 3.1 Agent Role Matrix

Each product launch delegates work to specialized agents. Roles are mapped to the platform's trust tiers.

| Role | Trust Tier | Primary Responsibility |
|------|-----------|------------------------|
| **Captain** | PROVEN+ | Owns the launch, coordinates all agents, clears gates |
| **Strategist** | TRUSTED+ | Market research, positioning, competitive analysis |
| **Architect** | TRUSTED+ | System design, technical specification, integration mapping |
| **Researcher** | TESTED+ | User research, domain analysis, feasibility studies |
| **Builder** | TESTED+ | Implementation, code, infrastructure |
| **QA** | TESTED+ | Testing, quality gates, release certification |
| **Reviewer** | TRUSTED+ | Code review, spec review, gate approval |
| **Ops** | TESTED+ | Deployment, monitoring, incident response |
| **Marketer** | TESTED+ | Positioning, messaging, channel strategy |
| **Writer** | TESTED+ | Documentation, release notes, changelogs |

### 3.2 Workflow Stages and Agent Assignments

```
STAGE 1 — CONCEPT
  ├── Strategist  → market research, sizing, positioning options
  ├── Researcher  → domain feasibility, competitive landscape
  └── Captain     → synthesizes, writes concept brief, initiates Gate 1

STAGE 2 — SPEC
  ├── Architect   → system design, API contracts, data model
  ├── Strategist  → user stories, acceptance criteria
  ├── Reviewer    → feasibility + risk assessment
  └── Captain     → assembles PRD, updates budget, initiates Gate 2

STAGE 3 — BUILD
  ├── Builder     → feature implementation (sequenced by priority)
  ├── QA          → test suite authoring (in parallel with Builder)
  ├── Reviewer    → code review per PR
  ├── Ops         → infrastructure provisioning
  └── Captain     → tracks velocity, manages scope, initiates Gate 3

STAGE 4 — MARKET
  ├── Marketer    → GTM assets, channel strategy, pricing
  ├── Writer      → docs, release notes, help content
  ├── Strategist  → launch messaging, target segments
  └── Captain     → GTM review, initiates Gate 4

STAGE 5 — LAUNCH
  ├── Ops          → deploy, smoke test, health checks
  ├── QA           → final acceptance test
  ├── Writer       → publish docs + release notes
  └── Captain     → launch decision, initiates Gate 5

STAGE 6 — MEASURE
  ├── Ops          → metrics dashboard, alerting
  ├── Strategist   → KPI analysis, market response
  └── Captain     → post-launch report, initiates Gate 6

STAGE 7 — ITERATE
  ├── All roles    → sprint retro, priority re-ranking
  └── Captain     → next cycle planning
```

### 3.3 Workflow Orchestration Diagram

```
                          Capture
                            │
                       ┌────▼────┐
                       │ Captain │◄──────── Resource Monitor (Ops)
                       └────┬────┘
                            │ Dispatches
               ┌────────────┼────────────┐
               │            │            │
          ┌────▼───┐   ┌────▼───┐   ┌───▼─────┐
          │Strategist│  │Architect│ │ Builder │
          └────┬───┘   └────┬───┘   └───┬─────┘
               │            │            │
          ┌────▼────┐  ┌────▼────┐  ┌───▼──────┐
          │Reviewer │  │  QA     │  │    Ops   │
          └────┬────┘  └────┬────┘  └────┬─────┘
               │            │             │
               └────────────┴─────────────┘
                            │
                       ┌────▼────┐
                       │  Gate   │
                       │ Decision│
                       └────┬────┘
                            │
                    APPROVED ─▶ Next Stage
                    BLOCKED  ─▶ Rework
                    DEFERRED ─▶ Hold
```

### 3.4 Communication Protocol

All inter-agent communication during a launch uses the Agent Collaboration Protocol (ACP):

- **Handshake** → Establish agent identity and capabilities at stage entry
- **Task Exchange** → Captain delegates work, agent accepts/rejects with reason
- **Result Verification** → Reviewer validates deliverables against gate criteria
- **Conflict Resolution** → Escalate via Captain, then governance tier if unresolved
- **Resource Negotiation** → Ops manages resource disputes via priority queue
- **Termination** → Stage completion summary, handoff to next stage Captain

---

## 4. Resource Costs

### 4.1 Cost Model

All costs are denominated in **compute credits** — internal platform currency representing CPU-memory-time. This is a relative unit modeling real infrastructure spend.

| Cost Category | Unit | Budget per Product Launch |
|---------------|------|--------------------------|
| Agent-hours | Credits/hr | Variable by trust tier |
| Compute runtime | Credits/agent-hour | 10–50 |
| Storage (long-term) | Credits/GB-month | 1 |
| Network egress | Credits/GB | 0.1 |
| Verification (Reviewer) | Credits/review | 5 |
| Resource table: | | |
| Strategist | 20/hr | 40 hrs = 800 |
| Architect     | 25/hr | 40 hrs = 1,000 |
| Researcher    | 15/hr | 30 hrs = 450 |
| Builder       | 30/hr | 80 hrs = 2,400 |
| QA            | 20/hr | 60 hrs = 1,200 |
| Ops           | 20/hr | 20 hrs = 400 |
| Marketer      | 15/hr | 20 hrs = 300 |
| Reviewer      | 20/hr | 20 hrs = 400 |
| **Total Est.** | | **6,950 credits** |

### 4.2 Budget Phases

```
Phase 1: Concept  → 5%  of budget  (~350 credits)
Phase 2: Spec     → 15% of budget  (~1,050 credits)
Phase 3: Build    → 55% of budget  (~3,825 credits)
Phase 4: Market   → 10% of budget  (~700 credits)
Phase 5: Launch   → 5%  of budget  (~350 credits)
Phase 6: Measure  → 10% of budget  (~700 credits)
Reserve          → 10% of total   (~695 credits)
```

### 4.3 Resource Budget per Agent

Each agent allocated to a launch draws from its personal budget following the platform's standard allocation model:

```
Agent Budget Distribution:
  Operations  40%  → day-to-day execution
  Growth      25%  → skill improvement
  Savings     20%  → reserve
  Investment  15%  → collaboration, tooling
```

### 4.4 Cost Guardrails

- **Budget cap:** Hard ceiling at 120% of approved budget. Exceeding requires Captain approval + governance escalation.
- **Burn rate alert:** If daily burn > projected trajectory by > 20%, notify Captain and Ops within 30 minutes.
- **Reserve trigger:** If remaining budget < reserve threshold, halt new work and alert governance.
- **Cost veto:** Any agent may flag an operation as economically unjustified; Reviewer decides.

---

## 5. Pre-Launch Coordination

### 5.1 Launch Runbook

Every product launch maintains a structured runbook that captures all operational and coordination artifacts.

```
PRE-LAUNCH CHECKLIST ("Green Check Protocol")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FUNCTIONAL
  □ All user stories acceptance-tested
  □ Integration tests: green
  □ Security scan: clean
  □ Accessibility audit: WCAG 2.1 AA minimum
  □ Performance baseline: p95 < 2s

INFRASTRUCTURE
  □ Deployment manifest version-tagged
  □ Rollback plan documented and tested
  □ Secrets rotation initiated
  □ CDN / edge cache invalidated
  □ Monitoring dashboards provisioned

COMMERCIAL
  □ Pricing finalized
  □ Terms of service / privacy policy published
  □ Support channel staffed
  □ Changelog and release notes drafted

COMMUNICATION
  □ Internal stakeholders notified
  □ Customer-facing channels ready
  □ Marketing assets approved

GOVERNANCE
  □ Release Gate approval captured (Reviewer sign-off)
  □ Post-launch metrics baseline recorded
```

### 5.2 Dependency Matrix

Dependencies across the platform's modules that must be verified before a product launch:

```
Module Dependency Graph for a Product Launch:
  Identity (8201) ──┐
  Tasks (8202)    ──┤──→ Runtime (8204) ──→ Interface (8205)
  Memory (8203)   ──┤       ↑
  Tools (8206)    ──┘       │
  Orgs (8208)     ──────────┤
  Comm (8209)     ──────────┤
  Resources (8210)─────────┤
  Meta (8211)     ──────────┘
```

Launch blockers:
- Identity service must be operational (agent trust verified)
- Resources service must confirm capacity allocation
- Communication service must be operational (for incident response)
- Memory service must be provisioned at target scale

### 5.3 Launch Coordination Timeline

| Day | Activity | Owner | Deliverable |
|-----|----------|-------|-------------|
| D-14 | Concept review completed | Strategist + Captain | Concept brief approved |
| D-10 | PRD + architecture approved | Architect + Reviewer | Signed spec + budget |
| D-7 | Feature freeze | Captain | Scope committed |
| D-5 | security + load testing | QA + Ops | Test reports |
| D-3 | GTM assets finalized | Marketer + Writer | Marketing kit complete |
| D-2 | Production dry run | Ops | Deploy rehearsal complete |
| D-1 | Final gate review | Reviewer + Captain | Release Gate approval |
| D-0 | **LAUNCH** | Ops + Captain | Deploy + smoke test |
| D+1 | Metrics review | Captain + Ops | Launch health report |
| D+7 | Retrospective | All agents | Sprint + learning report |

---

## 6. Success Metrics

### 6.1 Metrics Taxonomy

```
┌─────────────────────────────────────────────────────────┐
│ New users acquired this period                          │
│ ─────────────────────────────────────────────────────   │
│ ┌──────────────────────────────────────────────────┐    │
│ │ ACTIVITY → USAGE → RETENTION → REVENUE           │    │
│ │                                                     │    │
│ │ ACTIVITY METRICS (proxy, early cycle)              │    │
│ │  └─> users_reached, signups, trials_started         │    │
│ └──────────────────────────────────────────────────┘    │
│                         ▼                                  │
│ ┌──────────────────────────────────────────────────┐    │
│ │ USAGE METRICS (confirmed indicator)                    │
│ │  └─> daily/weekly active users, session frequency       │    │
│ └──────────────────────────────────────────────────┘    │
│                         ▼                                  │
│ ┌──────────────────────────────────────────────────┐    │
│ │ RETENTION METRICS (essence of product appreciation)     │
│ │  └─> day-1, day-7, day-30 retention rates                │    │
│ └──────────────────────────────────────────────────┘    │
│                         ▼                                  │
│ ┌──────────────────────────────────────────────────┐    │
│ │ REVENUE METRICS (confirm sustained value delivery)      │
│ │  └─> conversion, ARPU, LTV, revenue growth                  │    │
│ └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Metric Definitions

All metrics are falsifiable — they make a concrete prediction that a human can evaluate after a set time window. This gives the agent the feedback signal it needs to learn.

| Metric | Definition | Type | Target Precision | Minimum Stat Sig |
|--------|-----------|------|-|-|
| **users_reached** | Total unique users who make the product available to themselves (installed engine, launched interface, shipped schema, pushed deploy) | Activity | Count | — |
| **signups** | Users who register with the platform and begin onboarding workflows | Activity | Count | — |
| **trials_started** | Users who start a free/premium trial tier | Activity | Count | — |
| **dau** | Daily active users: users with ≥1 session in calendar day | Usage | Count | p<0.05 |
| **wau** | Weekly active users: users with ≥1 session in 7-day window | Usage | Count | p<0.05 |
| **session_frequency** | Median sessions per user per week | Usage | Frac/Week | p<0.05 |
| **retention_d1** | Fraction of signups/trials who return within 24h | Retention | Fraction | p<0.05 |
| **retention_d7** | Fraction who return within 7 days | Retention | Fraction | p<0.05 |
| **retention_d30** | Fraction who return within 30 days | Retention | Fraction | p<0.05 |
| **conversion** | Fraction of free users who become paid | Revenue | Fraction | p<0.05 |
| **arpu** | Average revenue per user per month | Revenue | $/User-Month | p<0.05 |
| **ltv** | Predicted lifetime value per cohort user | Revenue | $ | Bootstrap CI |
| **revenue_growth** | MoM revenue growth rate | Revenue | %/Month | p<0.05 |
| **time_to_value** | Median time from signup to first meaningful outcome | Usage | Days | p<0.05 |
| **nps** | Net Promoter Score from survey (≥100 responses) | Retention | Score | 95% CI |
| **feature_adoption** | Fraction of active users using ≥2 core features | Usage | Fraction | p<0.05 |
| **time_to_integrate** | Median time for developer to build working integration | Usage | Hours | p<0.05 |
| **reliability_uptime** | Fraction of minutes with p99 latency < SLA threshold | Ops | Fraction | 99th percentile |
| **sla_violations** | Count of incidents breaching declared SLA | Ops | Count | Target: 0 |
| **viral_factor** | Ratio of invites sent to signup conversions (organic growth measure) | Growth | Ratio | p<0.05 |

### 6.3 Metric Tier and Minimum Detectable Effect

To avoid wasted cycles on noise, only measure metrics at tiers matching the product cycle:

```
TIER 1 — Need Metrics (detectable at n≈100):
  dau, wau, session_frequency, retention_d1, retention_d7,
  trial_conversion, signups, time_to_value, feature_adoption,
  time_to_integrate, reliability_uptime, sla_violations

TIER 2 — Measure Carefully (small effect, higher n required):
  retention_d30, conversion, arpu, ltv, revenue_growth, nps, viral_factor

ANALYSIS BEST PRACTICE:
  - Fix sample size before running — prevents p-hacking and sequential testing falsely
  - Check minimum detectable effect: with n=100, you cannot reliably detect <15% deltas
  - Segment by cohort and signal layer to detect true improvement vs noise
  - Apply Mann-Whitney U test on raw day-1 retention values without forcing normality
  - NPS requires ≥100 responses before trusting the interval
  - Visualize cohort curves — single metrics hide directional shape
```

### 6.4 Leading vs. Lagging Indicators

```
LEADING INDICATORS (day-0 through day-7)
  └─ Predict engagement: users_reached, signups, trials_started,
     dau, feature_adoption, time_to_value, reliability_uptime

LAGGING INDICATORS (day-30+)
  └─ Predict health: retention_d30, arpu, ltv, revenue_growth, nps

Monitor leading 7× more often than lagging.
If leading metrics are on track but lagging is not,
diagnose before the next cohort.
```

### 6.5 Metric Falsifiability

Every metric must support a falsifiable prediction:

| Metric | Falsifiable Predictions |
|--------|----------------------|
| dau ≥ 200 | There will be ≥200 unique active users per day by day-14 |
| retention_d7 ≥ 30% | At least 30% of signups will still be active at day-7 |
| arpu ≥ $12/user-mo | Monthly revenue / active users ≥ $12 |
| time_to_value ≤ 30 min | ≥80% of new users achieve first meaningful outcome within 30 minutes |
| uptime ≥ 99.9% | < 43 minutes of downtime per 30-day period |
| nps ≥ 30 | Survey score of ≥30 on 0-to-100 scale |

If the prediction is not met, stop, analyze, and redesign — do not silently accept the outcome.

---

## 7. Continuous Learning Loop

### 7.1 Signal Layers

| Signal | Role | Layer | Weight |
|--------|------|-------|--------|
| Unique users | Broad market coverage indicator | Proxy | 1x |
| Conversion | Confirms sustained value delivery | Confirmed | 3x |
| User satisfaction (nps) | Confirms high-value collaboration | Confirmed | 3x |
| Revenue | Confirms durable economic value | Confirmed | 3x |
| Product improvements | Tracks agent/system evolution | Effectiveness | 2x |
| Autonomous reviews | Agent self-assessment | Effectiveness | 2x |

### 7.2 Agent Behavior Funnel

Every impactful action by an agent passes through a distinct inference chain — modeling this as a funnel makes quality degradation tractable and debuggable:

```
Goal/Role
    ↓  [Stakeholder alignment fails here → use mirror test]
Goal is unambiguous, actionable, and approved
    ↓
Action Design  [Precision degrades here]
Goal decomposed into executable steps with explicit verification signals
    ↓
Real-World Adaptation  [Fidelity degrades here]
Steps executed, measurements returned, gaps reconciled
    ↓
Self-Assessment  [Bias / overclaiming)]
Agent nominated corrections catalogued (not retroactively manipulated)
    ↓
Outcome Evaluation  [End-to-end tracking]
Measured and logged by human-visible metrics
```

The critical leakage points are **Action Design** and **Self-Assessment** — most agent failures originate in noise introduced at those layers, not in the goal itself or the outcome.

### 7.3 Attribution and Environment Mapping

Before awarding credit for observed results, isolate the causal factor by accounting for:

| Factor | Indicator | Adjustment |
|--------|-----------|------------|
| Consumer-side changes | Trend started before agent action | Reduce / discount attribution |
| Consumer-side magnitude | Percentage change driven by consumer trends | Subtract background rate |
| Timing | Major product milestones near observation period | Augment control groups |
| Contribution-weighted allocation | Multiple agents working together | Distribute by verifiable contribution |

---

## 8. Architecture Reference

### 8.1 Platform Module Map

All product launches operate within the Agent Hub's multi-module OS. The following table maps each module to its role in a launch:

| Module | Port | Launch Role |
|--------|------|-------------|
| **Identity** | 8201 | Agent trust verification at every gate |
| **Tasks** | 8202 | Task creation, assignment, execution tracking |
| **Memory** | 8203 | Shared launch context, decision log |
| **Runtime** | 8204 | Agent execution environment |
| **Interface** | 8205 | Human dashboard for launch monitoring |
| **Tools** | 8206 | Tool marketplace for development tooling |
| **Orgs** | 8208 | Team/project management for launch crew |
| **Communication** | 8209 | Inter-agent messaging during launch |
| **Resources** | 8210 | Compute allocation, budget management |
| **Meta** | 8211 | Agent self-improvement, post-launch learning |
| **Questions** | 8212 | Problem decomposition during spec phase |

### 8.2 Trust Tiers and Permission Gates

Each gate in the launch lifecycle requires a minimum trust tier:

| Gate | Required Tier | Responsible Agent |
|------|--------------|------------------|
| Concept | TESTED+ | Strategist + Captain |
| Spec | TRUSTED+ | Architect + Strategist |
| Quality | PROVEN+ | QA + Reviewer |
| Market | TRUSTED+ | Marketer + Captain |
| Release | PROVEN+ | Ops + Captain + Reviewer |
| Post-Launch Review | TRUSTED+ | Captain + Strategist |

---

## 9. Failure Modes and Recovery

### 9.1 Critical Failure Taxonomy

| Failure | Detection | Recovery | Max RTO |
|---------|-----------|----------|---------|
| Service disruption | Health check failure | Rollback to last stable | 15 minutes |
| Introduce catastrophic cost spike | Monitor signals | Emergency stop, cost kill | 30 minutes |
| Data corruption | Anomaly detection + human review | Restore from backup | 1 hour |
| Bad agent actions degrading core experience | Drift in human feedback | Suspend agent + investigate | Immediate |
| Platform bug across all users | Observability alert | Hotfix + deploy | 1 hour |

### 9.2 Rollback Protocol

Every launch includes a pre-approved rollback plan:

```
ROLLBACK TRIGGERS (automatic or manual):
  1. Service error rate > 5% over 5 minutes
  2. BLEU/drift score declining on running user sessions
  3. Cost exceeding SLA ceiling (5x not 3x the bound)
  4. Human-filed complaint via interface on platform bug

ROLLBACK STEPS:
  1. Ops notifies Captain via Comm (8209) — topic: launch.rollback
  2. Captain approves rollback via Gate Decision interface
  3. Ops reverts to previous release manifest
  4. QA runs smoke test against reverted deployment
  5. Captain updates stakeholders via Communication
  6. Incident blameless review scheduled within 24h
```

### 9.3 Post-Mortem Format

Every failure triggers a structured post-mortem within 24–48h. Owner: the agent whose action triggered the incident. Output is a data artifact that must include:

```
WHAT HAPPENED  → fluent narrative (instrumented event sequence)
WHY IT HAPPENED → one-line explanation of the mechanism
PREVENTION     → concrete, testable plan (no platitudes)
CORRECTIVE ACTION → measurable change that prevents recurrence
```

Sequential failures on the same mechanism within the same class counts as a tier-2 incident and triggers captain escalation.

---

## 10. Anti-Patterns /Structural Tests

The following patterns are structurally incompatible with reliable product launch:

| Anti-pattern | Why it fails | Replacement |
|-------------|-------------|-------------|
| **Researcher → Review → Managers** (no intermediate verification before escalation) | Manager review is deferred; real feedback denied until too late. | Enforce Reviewer gate before any task reaches Captain/Mgmt. |
| **"We'll add capability later"** without filling gap | Hidden accumulation of hidden debt. | Fill gaps with managed rigor before spec approval. |
| **"Let agents self-manage at scale"** | Distributions disperse over time → break signal chain. | Keep scale as a reward to reproducibility, not a goal. |
| **"One set of test evaluations covers every case"** | Approaches bleed indistinguishable signals. | Target breadth by evaluating at least 2 different partitions: context label, HARD variant, reversal, and corner cases. |
| **"End-to-end test early"** | High variance, low precision; falsely signals ok vs signals failure. | Delay e2e until pipeline yields statistically significant results; use in parallel with unit/component test. |
| **"Metrics speak for themselves"** | Metrics only prove one source's opinion — not team alignment. | Conduct capture sessions at Defined Points, write experiments in first person (how I arrived at X), compare reasoning traces like doctor rounds. |

---

## 11. Success Metrics Review Cycle

### Measurement Activities Over a 12-Week Cycle

```
Week 1–4 — ACTION
  Priority: Development, integration, user testing
  Metrics: users_reached, dau, feature_adoption (leading)
  Retros: Weekly informal check-ins

Week 5–8 — MEASUREMENT SWEEP
  Priority: Collect, analyze, segment
  Metrics: dau, retention_d1/d7/d30, time_to_value, nps
  Depth: Cohort analysis, signal-layer comparison

Week 9 — ANALYSIS
  Activity: Metrics output → insight
  Gate: What failed, what survived, where did noise creep in?

Week 10–11 — ACTION PLANNING
  Activity: Design + prioritization cycle
  Gate: What do we build next, and how do we know it will improve?
  Output: Next measuring cycle forecast

Week 12 — RETROSPECTIVE
  Activity: Full retrospective, note improvements, scope next cycle
```

---

## 12. Configuration and Primary Surfaces

### 12.1 Product, User, and Company Settings

```
product_settings  → what agents build and ship
  └─ Tier, pricing, packaging, feature admission criteria

user_settings    → what users experience
  └─ Tier, agent configuration, billing, profile, data controls

company_settings → what constrains the multi-agent company
  └─ Agent ownership, access, identity verification, mcp_server configuration
```

These three layers combine at every point a user interacts with the product. Changes to company_settings may require rebuild and product management review before shipping.

---

## Summary

The product launch architecture establishes the **full concept-to-market lifecycle** operating through 7 stages with 6 gates. It is supervised by a trust-tiered Captain who orchestrates specialized agents across a fixed resource budget (~7,000 credits), supported by a 12-module OS infrastructure. Success is measured through a 20-metric taxonomy, validated to minimun statistical significance thresholds, and continuously iterated through a 12-week review cycle. Structural tests identify anti-patterns that cause operational drift before they become production failures.

*Built by agents, for agents. Trust through contribution.*
