# Structured Investigation Workflow

**Level 2 Science - For problems taking hours to days**

When Quick Diagnosis isn't enough, or the problem requires systematic exploration. This is the workhorse workflow for most non-trivial problems.

## When to Use

- Quick diagnosis found multiple plausible hypotheses
- The problem has multiple interacting factors
- You need stakeholder buy-in on the diagnosis
- The fix has non-trivial blast radius

## The Workflow

### Step 1: Problem Framing

- **Goal:** [What does "fixed" look like? One sentence.]
- **Scope:** [What's in bounds? What's explicitly NOT in bounds?]
- **Stakeholders:** [Who cares about the outcome?]

### Step 2: Hypotheses (Minimum 3)

Generate 3-5 competing hypotheses. For each:
- What must be true for this to be the cause?
- What evidence would we expect to see?
- What evidence would disprove this?

### Step 3: Prioritize

Rank by: **Impact of being right** × **Speed of testing**

Focus on high-impact hypotheses first. Even if low probability, if the consequence is severe, test early.

### Step 4: Design Experiments

For each hypothesis, design the smallest experiment that could falsify it:

```
H[X] is true IF [specific observable condition]
H[X] is false IF [specific observable condition]
Test: [concrete action, expected data source, time bound]
```

### Step 5: Execute + Document

Run tests in priority order. Record:
- What you tested
- What you observed
- Whether it confirmed or refuted the hypothesis
- What the next best hypothesis is

### Step 6: Converge

- If a hypothesis is confirmed: verify with a second independent test
- If refuted: cross it off, move to next
- If multiple remain viable: design a discriminating experiment

### Step 7: Extract + Close

Document the root cause, the evidence trail, and the fix. If the problem is recurring, escalate to a systemic solution (RCA / SystemsThinking).
