# Full Cycle Workflow

**Level 3 Science - Research-grade methodology for macro-scale problems**

For problems spanning weeks to months, requiring statistical rigor, stakeholder review, or external publication. This is the complete scientific method with all safeguards.

## When to Use

- Product launches
- Architecture decisions with long-term impact
- Strategy validation
- Research projects
- Any decision where failure is expensive and reversible is hard

## The Complete Cycle

### Phase 1: Define Goal
See `DefineGoal.md`. What does "success" look like? Without this, you cannot judge results.

### Phase 2: Observe
What is the current state? Gather all available data. Don't hypothesize yet.

### Phase 3: Generate Hypotheses
See `GenerateHypotheses.md`. Minimum 3 competing hypotheses. Single-hypothesis testing is confirmation bias.

### Phase 4: Design Experiments
See `DesignExperiment.md`. For each hypothesis, design the smallest experiment that could falsify it.

### Phase 5: Measure Results
See `MeasureResults.md`. Collect data. Define what you'll measure before you measure it.

### Phase 6: Analyze Results
See `AnalyzeResults.md`. Compare to goal. Be ruthlessly honest.

### Phase 7: Iterate
See `Iterate.md`. Adjust hypothesis based on what was learned. Go to Phase 4.

## Integration

- **Council** — validate the goal definition
- **RedTeam** — attack your hypotheses before testing
- **FirstPrinciples** — decompose constraints before designing experiments
- **Evals** — measurement framework

## Time Estimate

- Micro (TDD, minutes): Phases 3-7, rapid cycle
- Meso (feature validation, hours-days): Full cycle once
- Macro (MVP launch, weeks-months): Full cycle + iteration

## Checklist

```
[ ] Phase 1: Goal defined with success criteria
[ ] Phase 3: At least 3 hypotheses generated
[ ] Phase 4: Experiments designed to falsify (not confirm)
[ ] Phase 5: Measurement plan defined before execution
[ ] Phase 6: Results compared to goal, not expectations
[ ] Phase 7: Learning documented and hypothesis adjusted
```
