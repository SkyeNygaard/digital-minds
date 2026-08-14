# Clarification run

This run checks the main result with a shuffled treatment order and complete
provenance. It changes no prompts or outcome definitions.

## Command

```bash
python run_scaled.py \
  --provider codex \
  --model gpt-5.6-luna \
  --all-families \
  --n-pairs 19 \
  --workers 4 \
  --replicates 2 \
  --doses 3 \
  --out-dir results/ranking_v2
```

The provider requests low reasoning effort because this model does not accept
the minimal setting. The output records the model, CLI version, reasoning
setting, isolation flags, system prompt, random seed, raw replies, and cell
seeds.

## Checks set before the run

The result keeps the main interpretation only if all of these checks pass:

- The shuffled grid is complete and balanced.
- At least 95% of treatment cells have all three tasks correct, and at least 95%
  of post-choice tasks are correct.
- The average realized shift is at least +0.50.
- The average forecast error is at most -0.50.
- At least 80% of pair-level forecasts underestimate the shift.
- The realized shift is positive in every label and order block.

The analysis also reports Pearson correlation and a two-sided permutation test.
This is an exploratory ranking check. Shared task families make the pairs
dependent, so the correlation is not evidence of independence.

## Outcome

Six of seven checks passed. The mean forecast error was -0.487, just above the
-0.50 cutoff. The submission therefore uses the narrower claim that the system
underestimated the strength of repetition. It does not claim that the system
missed the direction.
