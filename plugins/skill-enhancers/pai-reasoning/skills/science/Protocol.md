# Science Integration Protocol

How other skills invoke and implement Science cycles.

## When other skills should invoke Science

| Skill | When | How |
|-------|------|-----|
| RootCauseAnalysis | Investigating failures | RCA *is* Science applied to failures. Use FullCycle for systematic investigation, QuickDiagnosis for fast debugging. |
| Ideate | Testing candidate ideas | Use TEST phase scoring + Science for hypothesis validation of top candidates |
| RedTeam | Stress-testing arguments | Use Science to design falsification experiments for critical assumptions |
| WorldThreatModel | Validating future scenarios | Use Science to validate threat model predictions against data |

## How skills map to Science phases

| Skill Phase | Science Phase | Purpose |
|-------------|---------------|---------|
| Problem framing | Define Goal | What does success look like? |
| Information gathering | Observe | What do we know now? |
| Idea generation | Generate Hypotheses | What might work? (min 3) |
| Implementation planning | Design Experiment | How do we test this? |
| Testing/validation | Measure + Analyze | Did it work? Be honest. |
| Refinement | Iterate | Adjust, pivot, or ship. |

## Protocol for skill authors

1. Always start with a goal — never skip to solutions
2. Generate at least 3 competing approaches before testing
3. Design tests that could FALSIFY, not just confirm
4. Measure what matters — goal-relevant data only
5. Iterate based on data, not ego
