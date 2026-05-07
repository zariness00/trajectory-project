# Task 2: Trajectory analysis of top-5 models on mini-SWE-agent v2

## Overview
This report analyzes 2,500 trajectories (500 per model) from the top-5 models on  mini-SWE-agent v2 / SWE-bench Verified, focusing on three axes that pass/fail scores cannot capture: 
- trajectory length
- tool_call usage
- failure modes
The task-1 tool was extended to additionally extract `resolved`, `instance_cost`, and `exit_status` from each trajectory's metadata.

## Methods
Trajectories were downloaded from the Docent public API (500 per collection). 
Messages are counted following the convention "one message = one object in `transcripts[0].messages`, classified by its `role` field". 
Parallel tool_calls inside a single assistant message do not increase the assistant count. 
This matches the Docent UI's "Minimap (N messages)" metric.

## Comparison table

| Model | Resolved | Limits | Median | p95 | Max | Tool/Asst | Total $ | $/Resolved |
|---|---|---|---|---|---|---|---|---|
| claude-4-5-opus-high | 76.8% | 1.4% | 63 | 147 | 222 | 1.14 | $376.95 | $0.98 |
| gemini-3-flash-high | 75.8% | 0.0% | 109 | 181 | 319 | 0.98 | $177.98 | $0.47 |
| minimax-m2-5-high | 75.8% | 0.6% | 105 | 265 | 502 | 0.98 | $36.64 | $0.10 |
| claude-4-6-opus | 75.6% | 1.6% | 49 | 145 | 288 | 1.03 | $275.76 | $0.73 |
| gpt-5-2-codex | 72.8% | 0.0% | 65 | 141 | 251 | 1.02 | $236.78 | $0.65 |

# Key observations

1. Cost for a resolved task varies 10 times. For example, MiniMax costs 0.10 usd, while Claude 4.5 Opus costs 0.98 USD during the similar resolving rate(about 76 percent). 
This is revelaed when the trajectories and metadata are retrieved together. Moreover, pass or fail score is not shown in the leaderboard.
2. The style of reasoning is very different: median length 49-65 for Claude 4.6/GPT 5.2 vs 105-109 for MiniMax/Gemini. There is a ~2× difference. Note that shorter trajectories don't necessarily mean more successful (Claude 4.6 has the shortest median of 49 but not the highest resolve rate). Thus,  Claude models и GPT solve the task in approximately 50-65 steps, whereas Minimax solve the task in 105-109 steps. Meanhwile, the quality stays roughly the same. I believe, this is what the project states that models arrive to one concluding point but with different routes. 
3. Failure modes различны при одинаковом ярлыке "LimitsExceeded": Claude'ы (1.4-1.6%) упираются в cost_limit ($3) при ~60-100 шагах; MiniMax (0.6%) упирается в step_limit (250) при копеечных тратах; Gemini и GPT — 0% LimitsExceeded вообще. Это качественное различие в том, как модели "сдаются", не видимое из агрегатов лидерборда.
4. Использование параллельных tool_calls — стилистическое различие: ratio tool/assistant у Claude 4.5 составляет 1.14, у Claude 4.6 — 1.03, у GPT и Gemini ≈ 1.0, у MiniMax — тоже около 1.0. Это значит, mini-SWE-agent v2 в принципе допускает параллельные вызовы (раз Claude'ы это делают), но другие модели/обвязки выбирают строгий 1:1. Различие архитектурно-стилистическое.
5. И p95 у MiniMax — 265, тоже сильно больше остальных (которые ~145-180). Это значит, что MiniMax "решает" задачи дёшево, но в его 5% худших случаев он гоняет очень долго.
6. Claude 4.5 явно использует параллельные вызовы (на 14% больше tool-сообщений, чем assistant-ходов), а у Gemini и MiniMax ratio даже меньше единицы — это значит у них некоторые assistant-ходы вообще не сопровождаются tool call'ом (видимо, финальные размышления / submission). Это качественное различие в поведении агента, которое не видно по pass rate.

## Key observations

1.  All five models cluster within 4 percentage points of resolve rate (72.8–76.8%), yet the cost per resolved task ranges from \$0.10 (MiniMax) to \$0.98 (Claude 4.5 Opus high).  This is invisible on the leaderboard, which reports only resolve rate.

2. Median trajectory length is 49–65 messages for Claude 4.5/4.6 and GPT-5.2, but 105–109 for  MiniMax and Gemini 3 Flash, meaning roughly 2× longer paths to similar outcomes. Notably, shorter is not better: Claude 4.6 has the shortest median (49) but not the highest resolve rate. 
Models converge to similar answers via very different trajectories, exactly the gap the project sets out to measure.

3. Among Claude trajectories that hit limits (1.4–1.6%), all reach the \$3 cost_limit at only 60–100 steps. 
Among MiniMax's limit-exceeded runs (0.6%), all reach the 250 step_limit while costing 10 cents. 
Gemini and GPT-5.2 never hit either limit (0%). 
The same exit_status label thus represents qualitatively different failures, which is a distinction that requires trajectory-level inspection to recover.

4. MiniMax has a heavier tail. Its p95 trajectory length is 265, which is far above the 141–181 range of the other four models. 
The cheap per-task cost comes with a longer worst-case path, much of which corresponds to step_limit failures.

## Sanity checks
- `mini_version` is identical (2.1.0) across all 500 trajectories of every collection, meaning the agent harness is held constant.
- `step_limit` (250) and `cost_limit` (\$3) are identical in the config of all five models; the comparison is fair.
- `api_calls` from metadata equals the assistant message count, meaning internal consistency.

## Conclusion
Viewed through pass/fail alone, these five models look like one cluster spread over four percentage points. Viewed through trajectories, they separate along four practically meaningful axes: cost, length, failure mode, and parallelism. Each axis carries its own signal for model selection and motivates a richer class of trajectory-level metrics — precisely the direction this project sets out to develop.