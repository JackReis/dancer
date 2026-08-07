# Research Foundation

## Why It Works

Verbalized Sampling (VS) reduces the bias of single-sample generation by internally sampling K times (p<0.10 each) and selecting the best — a form of self-consistency that empirically increases diversity 1.6-2.1x and quality 25.7%.

Extended thinking allows the model to perform internal deliberation before emitting output, reducing shallow/cursory responses.

Combined: VS provides diversity, extended thinking provides depth. The model explores multiple paths internally and selects the best one.

## Activation Triggers

- "be creative" — StandardCreativity
- "maximum creativity" / "most creative" — MaximumCreativity
- "brainstorm" — IdeaGeneration
- "complex problem" — TreeOfThoughts
- "domain-specific" — DomainSpecific
- "technical creativity" — TechnicalCreativity
- "expand corpus" — SyntheticDataExpansion

## Research

Zhang et al. 2025 (arXiv:2510.01171) — 1.6-2.1x diversity increase on creative writing, 25.7% quality improvement, synthetic-data downstream accuracy lift 30.6% to 37.5% on math benchmarks.
