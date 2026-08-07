# Synthetic Data Expansion Workflow

Multi-turn Verbalized Sampling to grow a small seed corpus into a diverse N-example dataset.

## Execution

1. Read the seed corpus (5-20 examples)
2. Analyze the pattern/distribution
3. Enable extended thinking
4. Generate diverse new examples (N specified by user)
5. Write to JSONL file: resources/synthetic-data/{slug}/output.jsonl

## Use cases

- Training data expansion
- Test set creation
- Eval corpus growth
- Prompt diversity augmentation
