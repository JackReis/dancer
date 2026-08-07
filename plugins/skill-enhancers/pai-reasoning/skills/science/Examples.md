# Science Examples

## Example 1: Quick Diagnosis (Level 1)

```
User: "figure out why Surface time filters show stale items"
→ Quick diagnosis mode
→ Goal: Users see current filtered results, not stale data
→ H1: timestamp format mismatch in D1 — ISO string vs Unix timestamp
→ H2: cache TTL longer than expected
→ H3: filter logic has a race condition
→ Test H1 first: query D1 for actual stored format (30 seconds)
→ Result: ISO string in D1, Unix timestamp expected → CONFIRMED
→ Fix: normalize format at query layer
```

## Example 2: Full Cycle (Level 3)

```
User: "experiment with different prompt structures for better output"
→ Full cycle mode
→ Goal: Improve output quality by 20% (measured by user satisfaction)
→ H1: Chain-of-Thought improves clarity
→ H2: Few-shot examples improve consistency
→ H3: Structured output format improves completeness
→ Design 3 experiments with controlled inputs
→ Run A/B tests measuring satisfaction
→ Analyze: H2 wins, H1 neutral, H3 negative
→ Iterate: Combine H2 with elements from H1
→ Apply: Deploy improved prompts
```
