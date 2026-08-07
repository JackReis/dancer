# Science Methodology

## The Universal Cycle

The scientific method as a universal problem-solving algorithm. Seven phases that apply equally to TDD (micro), feature validation (meso), and MVP launches (macro).

## Phase 0: Define Goal

**Critical:** You cannot judge experiments without success criteria.

- One sentence goal
- Specific, measurable success criteria
- Hard constraints (what you cannot change)
- Acceptance: who decides and how

## Phase 1: Observe

**What is the current state?**

- Gather all available data before hypothesizing
- Distinguish observed facts from assumptions
- Note anomalies, contradictions, gaps
- Record the baseline state

## Phase 2: Generate Hypotheses

**What might work?** (Generate MULTIPLE)

- Minimum 3 competing hypotheses
- Each must be independently testable
- Each must be falsifiable
- Rank by testability

## Phase 3: Design Experiment

**How do we test?**

- Smallest experiment that could falsify the hypothesis
- Explicit measurement plan
- Confounders identified
- Test boundary defined

## Phase 4: Experiment

**Run the test.**

- Execute exactly as designed
- Don't adjust mid-run
- Record raw data, not interpretations
- Note anomalies

## Phase 5: Measure Results

**What happened?**

- Compare raw data to falsification condition
- CONFIRMED / REFUTED / INCONCLUSIVE
- Note confidence level with reasoning
- Record anomalies

## Phase 6: Analyze Results

**How does it compare to the goal?**

- Return to the original goal
- Map results to each success criterion
- Surface assumptions the data challenges
- Identify the gap between desired and actual

## Phase 7: Iterate

**What's next?**

1. **Apply** — works, ship it
2. **Adjust** — small hypothesis tweak, new test
3. **Pivot** — fundamentally different approach
4. **Expand scope** — problem bigger than expected
5. **Close** — refuted, try another hypothesis

## Scale Mapping

| Level | Application | Cycle Time | Key Adaptation |
|-------|-------------|------------|----------------|
| Micro | TDD (Red-Green-Refactor) | Minutes | Phases 2-7 rapid, automated |
| Meso | Feature validation | Hours-days | Full cycle once, stakeholder review |
| Macro | MVP launch | Weeks-months | Full cycle + iteration, statistical rigor |
