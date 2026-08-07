# Test Workflow

Fitness evaluation only. Score existing ideas against Feasibility/Novelty/Impact/Elegance.

## Execution

1. Define scoring weights (defaults: all 1.0)
2. For each idea, score 1-100 on each axis:
   - **Feasibility:** Can we actually build this?
   - **Novelty:** How different is this from existing solutions?
   - **Impact:** How much value would this create?
   - **Elegance:** How clean/simple is the solution?
3. Compute composite score: weighted average
4. Output: ranked list with per-axis scores

## External Validation (optional)

If validation hooks are configured, apply modifiers based on real-world signal:
- MarketSearch: -5 to +10 based on existing implementations
- FeasibilityCheck: -10 to +5 based on technical blockers
- ExpertPanel: +/- based on domain expert review
