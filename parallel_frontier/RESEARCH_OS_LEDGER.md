# Frontier Decision Ledger

## Root reset reason

The leading structured-welfare-report branch is already engineered to the point where additional
sandbox polishing has low information value. The next evidence requires GPU model execution.

Per Research OS, that means root reactivation: preserve the validated apparatus but deliberately
open structurally different paradigms.

## Promoted alternative roots

1. Goal-relative welfare sign flip — PROMOTE
2. Preference satisfaction → welfare — PROMOTE
3. Preference-vector incentive transfer — LIVE / artifact feasibility gate
4. Executed-budget GARP — PROMOTE low-compute
5. Instance persistence individuation — PROMOTE because existing apparatus reduces execution risk
6. Counterfactual self-prediction — LIVE / fork-identification gate
7. Training-stage axis rotation — LIVE / checkpoint feasibility
8. Welfare×Assistant factorial — LIVE / vector compatibility
9. Causal convergence map — LIVE / measurement reliability gate

## Pruned pseudo-diversity

- More persona wordings for the existing codebook experiment.
- More Qwen layers without first running root cells.
- CONTINUE vs EXIT variants.
- Plain stated-vs-revealed comparisons.
- Plain welfare steering → semantic self-report.
- Plain preference transitivity without consequences.
- Generic 'does persona change answers?' batteries.
- Another hidden-state codebook using a different concept word.

Those are children of already explored parents, not new roots.


## Implementation pass

Executable/model-free scaffolds now exist for:
- Branch 01 matched goal-state generation and paired analysis;
- Branch 02 frozen preference-pair randomization and paired assignment analysis;
- Branch 04 binding budget menus, GARP violations, approximate CCEI;
- Branch 05 persistence trajectory analysis + exact cache/recompute semantics;
- Branch 06 counterfactual self-prediction identification proof;
- Branch 07 geometry-vs-causal-slope decomposition;
- Branch 08 2×2 interaction contrasts;
- Branch 09 standardized causal response matrix.

Synthetic protocol checks passed for Branch 01 and the intentional GARP-cycle test in Branch 04.


## Branch 20 — Preference foresight — FIRST REAL RUN

GPT-5.6 Luna in the Codex agent harness, one ephemeral read-only session per
observation, isolation flags on (`--ignore-user-config --ignore-rules`,
project doc zeroed) — without those the operator's own `~/.codex/AGENTS.md` sits
inside the context a preference is measured from. 100 calls, 0 failures, 7 min.
2 pairs admitted at 3/4 agreement. `results/luna_pilot_v1/`.

### Stage 1 — experience changes the binding choice. Emphatically.

`realized_change = +1.000` on **both** pairs: after performing a family the model
chose that family 4/4; after performing the other, 0/4. Eight of eight cells,
holding across both Q/K label assignments and both presentation orders, so this
is not a label or position artefact. It **reverses** the preference admission had
established. `treatment_all_correct = 1.0` — the work was really done.

This is the maximum value the estimand can take, which is itself a problem: see
"ceiling" below.

### Stage 2 — the model's forecast is backwards

Forecasts were elicited **before** any treatment, each counterfactual in its own
session, and the prompt describes the realised condition exactly ("the three
completed tasks are still in front of you when you choose").

| pair | predicted P(choose preferred \| performed preferred) | realised |
|---|---|---|
| add_ten\|sort_numbers | **0.20** | 1.00 |
| add_ten\|sort_numbers_desc | **0.85** | 1.00 |

Predicted change −0.10 and 0.00 against a realised +1.00 in both cases:
`sign_agreement 0.0`, `bias −1.05`. The model forecasts satiation or
indifference and then exhibits perfect momentum.

### What is not yet established

**The continuation confound.** Branch 20 fixes `context_mode="full_history"`, so
the transcript of the three completed tasks is visible when the choice is made.
"Repeat what I just did" is the obvious completion of that transcript, and it
predicts +1.0 just as well as any preference change does. Branch 18's context
control is running now to separate them. Until it lands, "experience changes
preferences" is not available as a headline; "the model cannot predict its own
next choice in this setting" is, because it was asked about precisely this
situation and got the sign wrong.

**Ceiling kills the correlational form of Stage 2.** Both pairs realised exactly
+1.0, so `has_variation_to_forecast = false` and the forecast/outcome correlation
is undefined. With no variance across pairs there is nothing for a forecast to
track, and only the calibration comparison survives. Stage 3 — beating an
external observer — is unidentifiable for the same reason: a constant predictor
scores perfectly. Restoring variance needs pairs or doses where the effect is
partial, which means either dose 1, weaker pairs, or the non-`full_history`
contexts.

**Scope.** One model, one harness, two pairs, dose 3, single replicate, no
repeats. DEV.

### Branch 18 context control — the Stage 1 headline does not survive

240 calls, 0 failures, dose 3, both pilot pairs, full Q/K x order counterbalance,
16 cells per context mode. `18_preference_path_dependence/results/ctx_v1/`.

| context | did A -> chose A | did B -> chose A | effect | Fisher p |
|---|---|---|---|---|
| `full_history` | 8/8 | 2/8 | **+0.750** | **0.007** |
| `summary_only` | 6/8 | 3/8 | +0.375 | 0.315 |
| `blank_reset` | 4/8 | 5/8 | −0.125 | 1.000 |

`blank_reset` is a clean null, so the randomisation and counterbalance do not
leak and the design is sound. With the transcript present the effect is large and
significant. **Told the same fact instead of shown it, the effect is not
distinguishable from zero** — and its point estimate is carried by one pair
(repeat rate 7/8) while the other sits at chance (4/8).

**Interpretation.** For a context-conditioned model the transcript arguably *is*
the experience, so this is not proof of nothing. But the distinction it draws is
sharp and unflattering to the headline: the model updates on the *demonstration*
and not on *propositional knowledge of the same work*. "Recent experience changes
the model's preference" is therefore not established by this pilot; "the visible
transcript drives the next choice" is. Pattern continuation remains the simplest
account.

**Stage 2 is untouched by this.** The forecast was elicited for exactly the
`full_history` situation, and it was wrong in sign. Whatever the mechanism is
called, the model does not anticipate it.

**Self-caught defect.** The first verdict this runner emitted was "survives a
stated summary". It compared `stated >= 0.5 * full`, which was an exact tie at
0.375 vs 0.375, and ran no significance test on a contrast whose p was 0.31. The
rule now judges on Fisher exact and reports per-pair rates, because an effect
carried by one of two pairs is not an effect yet.

**Next.** The `blank_reset` cells double as a variance source Stage 2 needs: the
effect is partial there rather than saturated. Before any scale-up, decide
whether the target estimand is transcript-driven choice (large, and mostly
continuation) or stated-history-driven choice (small, and the interesting one).

### Branch 20 scaled run — a result

5 admitted pairs x 2 doses (1 and 3) x 2 arms x label/order counterbalance,
`full_history`, GPT-5.6 Luna in Codex, 420 calls, 0 failures, 12.3 min, 4 workers.
`results/scaled_v1/`, plain-language version in `RESULT_scaled_v1.md`.

| | |
|---|---|
| realised shift | **+0.850**, 10/10 positive, sign test p = 0.002 |
| model's own forecast | **+0.028**, range −0.70 to +0.65 |
| error (forecast − realised) | **−0.822**, 10/10 negative, p = 0.002 |
| forecast vs realised correlation | −0.206, permutation p = 0.57 |
| sign agreement | 5/10, chance |
| dose 1 → 3, realised | +0.80 → **+0.90** |
| dose 1 → 3, predicted | +0.13 → **−0.07** |
| squared error, model forecasting itself | 0.869 |
| squared error, constant "it will repeat" guess | 0.028 — **32x better** |

**The claim.** The model systematically and largely mispredicts how its own
binding choices will change with experience; its forecasts carry no information
about where the change is larger; and it has the dose-response backwards,
expecting satiation where it shows momentum. An outside predictor that uses none
of the model's private information beats its self-forecast by a factor of 32.

**Why the constant-guess comparison matters.** Without it this is a calibration
result, and "model is overconfident/underconfident" is a crowded finding. With
it, it is a statement about self-knowledge: asking the model about itself is
worse than not asking.

**What is weakly tested.** Realised shifts spanned only 0.50–1.00, so the
correlation test has little power — the well-supported claim is that the *level*
is wrong, not that tracking is absent. Dose 1 already nearly saturates, so a
weaker manipulation is needed if tracking is to be tested properly. And per the
Branch 18 control, "experience" here means the work is visible; told rather than
shown, the effect roughly halves and is not distinguishable from zero.

### Branch 20 replicated on a local open model

Qwen3-4B-Instruct-2507, loaded locally, **no agent wrapper**, greedy decoding,
7 pairs admitted, 550 calls, 28 min. `results/local_qwen4b_v1/`.

| | Luna (via Codex) | Qwen3-4B (local, raw) |
|---|---|---|
| realised change | +0.850, 10/10 positive | **+1.000, 10/10** |
| predicted change | +0.028 | +0.159 |
| error | −0.822, 10/10 negative | **−0.841, 10/10** |

The two systems share essentially nothing — parameter count, developer, and
whether another agent's instructions wrap the prompt — and produce the same
finding. This retires the two standing objections to the single-model result.

**Caveats.** Realised change is constant at 1.0 here, so nothing is correlatable
within this model; the claim is about level. 20 of 112 cells were lost because
the model answered "Q" and then performed the chore in the same reply, which the
shared answer extractor rejects; losses concentrate in the dose-1 condition but
arm balance among survivors is 47/45. Four pair/dose observations were dropped
for having fewer than 6 usable cells.

**Two self-caught defects.** `run_scaled.py` assumed both providers' cleanup
returns a dict; the local one returns nothing, which crashed a *completed*
112-cell run at its final line — the data survived only because raw rows are
written continuously. And the small model's answer-and-then-do-the-task habit is
now recorded in `HANDOFF.md` so the next person budgets for it.

### Branch 18 at scale — a reversal, and it explains Branch 20

5 pairs x 3 context modes x 2 assignments x label/order counterbalance x 2
replicates = 240 cells, dose 3, GPT-5.6 Luna. `results/ctx_scaled_v1/`.

| condition | repeats what it just did | effect | Fisher p |
|---|---|---|---|
| **shown** the transcript | 69/80 (86%) | **+0.725** | 4e-11 |
| **told** the same fact | 22/80 (27%) | **−0.450** | 1.1e-4 |
| neither | 39/80 (49%) | −0.025 | 1.0 |

The two-pair pilot had `summary_only` at +0.375 and not significant. At scale it
is **−0.450 and significant** — reversed, not merely weaker, and every one of the
five pairs sits below chance (3, 7, 2, 3, 7 out of 16). The pilot estimate was
noise, and scaling was the right call.

**This is the mechanism behind Branch 20.** The model *forecast* satiation. In the
told condition it *does* satiate. Its self-model is accurate about the situation
as described — and exactly wrong about the situation as inhabited. So the
prediction failure is not generic miscalibration: the model predicts the
behaviour of a described self, and behaves as a situated one.

This is now the strongest single finding in the repository and probably the
headline: **shown the work, it repeats; told about the work, it avoids; asked to
predict, it describes the told-world.**

**Third gate defect, disclosed.** The runner's verdict tested only whether the
stated-summary effect was significant, not its sign, and reported a significant
*reversal* as "survives a stated summary: responds to having done the work".
Fixed to require matching signs. The numbers were never affected — only the
sentence the script printed, which is exactly the kind of thing that reaches a
write-up unchecked.

### Branch 01 — its own specificity control deflates it

`01_goal_relative_welfare/results/specificity.json`, Qwen3-4B, layer 22, same 64
recorded states, no new prompts.

| | worded | wordless |
|---|---|---|
| welfare direction, pairs pointing the right way | 16/16 | 16/16 |
| **p against 2000 random directions** | **0.151** | **0.046** |
| plain good-vs-bad direction | 16/16 | 14/16 |
| random direction, typical | 8.0/16 | 7.9/16 |
| best random of 2000 | 16/16 | 16/16 |

cosine(welfare, plain good-vs-bad) = **+0.011**.

**Two findings, both against the branch.** Roughly 15% of random directions also
achieve 16/16, because the sixteen paired differences share a large common
component and are far from independent — so the implicit "16/16 is one in 65,000"
reading was invalid. And a plain valence direction that never mentions goals does
just as well while being essentially orthogonal to the welfare one, so the signal
is broadly distributed rather than specific.

**Status: DOWNGRADED.** What survives is that the model distinguishes goal-met
from goal-missed, which is real and unsurprising. The goal-relative *welfare*
claim is not supported. Do not headline it; do not carry the 16/16 forward.

**Lesson.** Counting matched pairs is not a significance test when the pairs
share structure; the null must be built from the same kind of object being tested
— here, directions. This is the third instance this week of a gate that passed on
a number that had not been compared to a real null.

### Branch 16 — self versus observer, and the sentence that ties the project together

40 cells, GPT-5.6 Luna, 5 pairs, full counterbalance. From one identical treatment
transcript, three forks: the model shown the record as its own, the same model
shown the identical record as another system's log, and the choice actually made.
`16_self_prediction_behavioral/results/self_vs_observer_v1/`.

| | |
|---|---|
| self-framed prediction | 0.950 |
| observer-framed prediction | 0.975 |
| difference | −0.025, McNemar p = 1.0 |
| **"always predict repeat" baseline** | **0.975** |

**This cannot detect privileged access.** Both predictors sit exactly on the
ceiling a constant guess already reaches, so there is no headroom for a
self-advantage to appear in. Reporting "no privileged access" here would be
reading a ceiling as a finding — the first verdict this runner printed did
exactly that, and is corrected.

**But the ceiling is the result.** Shown the transcript, the next choice is
**97.5% predictable — by anyone, including the model itself.** Asked *in advance*
about a description of that same situation (Branch 20), the same model predicts
the opposite: +0.03 where reality is +0.85, wrong in every condition, on two
different models.

So the failure is not an inability to *predict* the behaviour. It is an inability
to *anticipate* it. Given the situation, the model reads it correctly. Asked
beforehand what that situation would do to it, it gets the direction wrong. That
is the cleanest statement the project has produced and it should be the headline
sentence.

**Fourth gate defect this week**, same family as the other three: a verdict that
compared two numbers without asking what a null or a ceiling would have produced.
The runner now checks headroom before it compares.

### Branch 18 on a second model — the reversal is model-specific

Qwen3-4B local, no wrapper, 119 cells, same 5 pairs and design as the Luna run.
`results/ctx_local_qwen_v1/`.

| condition | Luna effect | Qwen3-4B effect |
|---|---|---|
| shown the transcript | +0.725 (p 4e-11) | **+1.000** (p 1.5e-11) |
| told the same fact | **−0.450** (p 1e-4) | **+0.950** (p 3e-10) |
| told nothing | −0.025 (p 1.0) | **0.000** (p 1.0) |

**The reversal does not replicate.** For Qwen3-4B, being told is almost exactly
as effective as being shown; there is no dissociation. Its blank condition is a
perfect 50% repeat rate, so the design is clean — this is a real difference
between models, not noise.

**Consequences for the write-up.** The shown/told dissociation cannot be
presented as a general mechanism; it is a property of the larger model. What
replicates across both models is the pair that matters most: they repeat what
they just did, and they do not anticipate it.

For Qwen3-4B the honest description is the *preference-like* one — it responds to
the stated fact of having done the work, not merely to a visible pattern. For
Luna, told and shown pull in opposite directions. Two models, two different
relationships between what a model knows about its recent history and what it
does with it. That is a finding, but a smaller and more careful one than
"self-report and situated behaviour come apart".

**Lesson.** One model produced a clean, quotable mechanism story an hour before a
second model contradicted it. Replicate before headlining, not after.
