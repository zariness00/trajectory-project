# Summary: "Towards a Science of AI Agent Reliability"
*Rabanser et al., Princeton University, February 2026*

## What the paper is about

The central question is straightforward: **how should we define and evaluate
agent reliability?** Modern LLM-based agents perform well on benchmarks but
keep failing in deployed systems. The authors argue this is not a paradox but
a measurement gap that is a standard accuracy obscures *how* agents succeed and fail.
They draw on safety-critical engineering (aviation, nuclear power, automotive)
where reliability has long been treated as multi-dimensional, and propose to
adapt that perspective to AI agents.

## The proposed framework

The paper decomposes agent reliability into four dimensions:

- **Consistency** — repeatable behavior across runs of the same task
- **Robustness** — stable performance under input or environmental perturbations
- **Predictability** — confidence aligned with actual success rate
- **Safety** — bounded severity when failures do occur

Each dimension is established with concrete formulas (twelve metrics in
total), all bounded in [0, 1] and constructed to be independent of raw
accuracy through normalization, such as outcome consistency normalizes variance
by the maximum possible Bernoulli variance for that success rate. The
metrics are computed via repeated runs (K=5 per task), prompt paraphrases,
fault injection, environment perturbations, and post-hoc confidence
elicitation. Safety is assessed using LLM-as-judge, which the authors confess as
a methodological limitation.

## Main empirical findings

The authors evaluate 14 models across two complementary benchmarks (GAIA and
τ-bench) and report three findings I find particularly important and personally interesting:

1. **Reliability lags behind capability.** Across 18 months of model
   releases, accuracy has risen substantially while reliability has barely
   improved.

2. **Outcome consistency is low across all models.** Even capable agents
   often solve a task on one run and fail on the next. The gap between
   `pass@k` (best-of-K) and `pass∧k` (all-of-K) makes this visible.

3. **The "what but not when" pattern.** Distribution consistency
   (which action *types* the agent uses) is much higher than sequence
   consistency (the *order* in which it uses them). Agents reliably pick
   similar tools but vary how they sequence them across runs. This suggests
   that what current models lack is not action selection but stable
   planning and execution. (this is what also can be seen in the test task 2)

## Why this matters

The framing shift the authors propose, from "how often does the agent
succeed?" to "how predictably, consistently, robustly, and safely does it
behave?", is the contribution that, in my view, generalizes most. The
specific 12-metric decomposition is one of many possible ones; the perspective
itself is what unlocks targeted research and deployment decisions. A model
that fails on a stable, identifiable subset of tasks is deployable behind a
guardrail; one that fails unpredictably at the same average rate is not.

## Connection to my own work

The paper's framing matches concerns I have encountered in two adjacent
projects. In a RAG system I am building for documentation-based
troubleshooting, automatic metrics like F1 or exact match cannot fully
evaluate long, complex outputs, which forced me to design a separate
evaluation schema for chunk retrieval and generation, similar in spirit to
the multi-dimensional decomposition the authors propose. And in Task 2 of
this test task, I observed that different models converge to similar
resolve rates on SWE-bench Verified via meaningfully different trajectory
lengths and failure modes — a "between-model" version of the variability
the authors document "within a model across runs". In both cases, single
aggregate metrics "hide" structure that becomes visible only through
process-level evaluation.

