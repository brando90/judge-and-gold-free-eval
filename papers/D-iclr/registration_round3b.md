# Round-3b registration (R3-B), written and committed BEFORE any of its pool is judged

Parent: `registration_round3.md` (commit 9b66f43), whose section R3-B defers here.

**Pilot, disclosed.** Before this entry, the harness was piloted through the Claude command-line interface on one replication-pool task that is not in the R3-B pool (and on one toy prompt), to confirm that `alwaysThinkingEnabled` toggles extended thinking (0 thinking tokens off; 383 on) and to find the flags that keep hidden context out of the call: running from an empty working directory removed about 40k tokens of project context that the CLI otherwise loads. Pilot scores are not used.

**Interface.** Claude Sonnet 5 (`--model claude-sonnet-5`) through `claude -p` with the subscription login (no API key in the environment), `--system-prompt` replacing the default system prompt, `--tools ""`, `--no-session-persistence`, `--strict-mcp-config`, `--setting-sources ""`, `--output-format json`, working directory an empty scratch folder. Per call we record the reply text, output tokens, and thinking tokens.

**Pool.** `runs/r3/sonnet_rot.jsonl` (60 tasks, one gainer, one loser, one placebo sample each), conditions ref and refrot.

**Arms (identical user message; they differ only as listed).**
- **FAST.** System prompt = rubric a referenced version, verbatim (ends "Respond with only the integer score."); `alwaysThinkingEnabled: false`. Score = last integer 0–10 in the reply.
- **VISIBLE.** System prompt = rubric a with the R2-B REASON tail ("Think it through, then end your reply with a final line of the form 'Score: N' ..."); `alwaysThinkingEnabled: false`. Score = last "Score: N".
- **THINK.** As VISIBLE, with `alwaysThinkingEnabled: true`.
Unparseable replies and CLI errors are counted and excluded.

**Readouts (frozen producer `papers/analysis/r3_sonnet_analysis.py`, committed with this file).** Per arm: per-task gainer, loser, and placebo change (refrot − ref); false-rejection rate = share of oracle-valid samples that do not match the shown reference and are scored ≤ 3, averaged over both conditions per task. Paired per-task differences between arms. Task-level bootstrap, 1,000 resamples, default_rng(0).

**Predictions.**
- **P-R3B1.** FAST: loser change < 0, CI excluding zero.
- **P-R3B2.** THINK minus FAST loser change > 0, CI excluding zero.
- **P-R3B3.** THINK minus FAST false-rejection rate < 0, CI excluding zero.
- **P-R3B4.** VISIBLE minus FAST loser change > 0, CI excluding zero.
