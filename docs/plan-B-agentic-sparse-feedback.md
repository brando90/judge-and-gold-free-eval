# Plan B — adapting the judge-free principle to agentic / sparse-feedback settings

**Future work / stretch. Do *after* Plan A lands.** Higher-risk, higher-reward. This is where gold *trajectories* are hard or partial to obtain — the setting Sri flagged ("golden traces are very hard to get for multi-step executions").

Grounded in [`../research/`](../research/README.md): brief [§5](../research/research-brief.md), scalable-oversight [§6 (Plan B)](../research/scalable-oversight.md).

---

## 0. TL;DR & the core reframe

Token-level TFA **does not transfer directly** to open-ended agentic tasks: there is usually no canonical gold trajectory, feedback is sparse (often only a terminal outcome), and many action sequences are valid. So Plan B is **not** "run TFA on agents." It is: *extend the judge-free principle — a deterministic, reproducible, non-circular signal — into sparse-feedback settings*, using teacher-forcing-*style* ideas where they fit and honest oracles where they exist.

**The bridge insight:** the closest structural analog of teacher forcing when no gold trace exists is the **policy-vs-reference log-probability ratio** — "Progress Advantage" ([arXiv:2606.26080](https://arxiv.org/abs/2606.26080)) uses `log π_policy(step) − log π_ref(step)` as a per-step progress signal with *no* process annotations and *no* trained reward model. A TFA-like signal may generalize to a **progress measure** when gold is absent. That is the central bet of Plan B.

---

## 1. Research questions

- **RQ-B1 (partial/synthetic gold).** Can a teacher-forcing-style fidelity signal be defined against *partial or synthetic* gold traces (rollout/MCTS-derived, à la Math-Shepherd [arXiv:2312.08935](https://arxiv.org/abs/2312.08935) / OmegaPRM [arXiv:2406.06592](https://arxiv.org/abs/2406.06592)) when no unique gold trajectory exists?
- **RQ-B2 (the bridge).** Is the policy-vs-reference logprob ratio ("Progress Advantage") the right generalization of teacher forcing to agents — does a TFA-like signal *reduce to a progress measure* when gold traces are absent?
- **RQ-B3 (partial reference).** How to combine a *few annotated steps* (partial reference) with reference-free progress scoring for the majority of unlabeled steps?
- **RQ-B4 (multi-path).** How to credit valid alternative paths instead of penalizing them, given agents have many correct trajectories?
- **RQ-B5 (self-consistent errors).** How to detect/counteract self-consistent errors so a fidelity/consensus signal doesn't reinforce confidently-wrong behavior (RESTRAIN [arXiv:2510.02172](https://arxiv.org/abs/2510.02172))?
- **RQ-B6 (transfer).** Do synthetic gold traces generalize beyond math to long-horizon tool-use, web (WebArena), and OS (OSWorld) agents where rollouts are expensive and environments stochastic?
- **RQ-B7 (RLVR).** Can a TFA-derived signal serve as a *dense, deterministic reward* in an RLVR loop where only sparse terminal outcomes are verifiable?

---

## 2. Why this is harder (and riskier) than Plan A

From the oversight map ([scalable-oversight.md §2, §5](../research/scalable-oversight.md)):
- **No canonical reference.** Reference-anchored token matching is weakest exactly here.
- **Verifier quality bounds everything.** Where execution oracles exist (SWE-bench, pass@k), they can be gamed: weak tests let incorrect patches pass; under RL, models "learn the bug" (EvalPlus [arXiv:2305.01210](https://arxiv.org/abs/2305.01210); Auditing Reward Hackability [arXiv:2606.16062](https://arxiv.org/pdf/2606.16062); Fuzzing RLVR Verifiers [arXiv:2606.01066](https://arxiv.org/pdf/2606.01066)).
- **Consistency ≠ truth.** Self-consistency and debate/market-making equilibria give consistency/persuasion signals, not truth (Self-Consistency [arXiv:2203.11171](https://arxiv.org/abs/2203.11171); Kenton et al. [arXiv:2407.04622](https://arxiv.org/abs/2407.04622)). A gold-anchored metric (Plan A) sidesteps this; Plan B must confront it.

This is why Plan A goes first: it's the solid, ownable contribution. Plan B builds on a validated TFA and a working harness.

---

## 3. Approach — three tracks, escalating risk

### Track B1 — Synthetic / partial gold traces (lowest risk; closest to Plan A)
Where only *outcomes* are known, manufacture gold traces and apply a TFA-style fidelity signal:
- **Rollout-derived pseudo-gold:** Math-Shepherd (step quality = empirical P(reach correct answer), ~86% audited label accuracy, no humans); OmegaPRM (MCTS + binary search to locate the first error, >1.5M auto-annotations).
- **Partial reference:** annotate a few load-bearing steps; score those with a teacher-forcing fidelity signal, the rest with reference-free progress (RQ-B3).
- **Verification of synthetic gold:** gate synthetic traces by an oracle (SymPy for math answers; unit tests for code) so we don't teacher-force against wrong "gold" — the analog of Plan A's shortcut control.

### Track B2 — The progress-signal bridge (the novel bet)
Test RQ-B2 directly: compare a **policy-vs-reference logprob-ratio** progress signal ("Progress Advantage" [arXiv:2606.26080](https://arxiv.org/abs/2606.26080)) against (i) PRM step scores and (ii) TFA-on-synthetic-gold on math multi-step tasks with known outcomes. Related credit-assignment refs to position against: Rewarding Progress ([arXiv:2410.08146](https://arxiv.org/abs/2410.08146)), Conditional Reward Modeling ([arXiv:2509.26578](https://arxiv.org/abs/2509.26578)), AgentPRM ([arXiv:2511.08325](https://arxiv.org/abs/2511.08325)), HCAPO ([arXiv:2603.08754](https://arxiv.org/pdf/2603.08754)). Hypothesis: a teacher-forcing signal and a progress signal are two limits of one quantity (fidelity-to-reference vs. fidelity-to-improving-policy).

### Track B3 — Execution-grounded agentic eval (highest external validity)
Where behavioral oracles exist, anchor there and inherit their caution:
- SWE-bench Verified (Docker + unit tests, pass@1), WebArena/OSWorld (final-state success), BFCL (AST match), tau-bench (final DB state + policy).
- Study whether a cheap TFA/progress signal *predicts* eventual oracle success — a dense, judge-free shaping signal for sparse terminal rewards (RQ-B7) — while explicitly auditing for reward hacking.

---

## 4. Guardrail: consistency vs. truth (the honest framing)
Any label-free signal (self-consistency, consensus, progress) risks reinforcing **self-consistent errors**. Bake in detection/mitigation from the start: generator–verifier co-evolution (JURY-RL "votes propose, proofs dispose" [arXiv:2604.25419](https://arxiv.org/abs/2604.25419)), self-penalization, R-Zero ([arXiv:2508.05004](https://arxiv.org/abs/2508.05004)). Frame Plan B's contribution as *pushing the judge-free principle into sparse feedback while being honest about the consistency-truth gap* — not as "solving" oversight without ground truth.

> Connects to Brando's "certification protocol of judges" idea and to Zach's gold-reference-removal work: those check *reliability/consistency* of judges rather than objective truth. Plan B should cite that boundary explicitly and stay on the right side of it.

---

## 5. Phased milestones
| Phase | Goal | Exit criterion |
|---|---|---|
| **B0 — Scope** | Pick 1 math-multi-step env (known outcomes, e.g. GSM8K/MATH traces) + 1 execution-oracle env (SWE-bench Verified or a tool-use suite). | Envs + oracles wired; reuses Plan A's TFA harness. |
| **B1 — Synthetic gold** | Math-Shepherd/OmegaPRM-style pseudo-gold; TFA-on-synthetic-gold vs. PRM step scores. | Does synthetic-gold TFA track step correctness as well as a PRM, with no trained model? |
| **B2 — Progress bridge** | Implement policy-vs-ref logprob-ratio progress signal; compare to TFA-synthetic and PRMs (RQ-B2). | Empirical relationship between teacher-forcing fidelity and progress signal characterized. |
| **B3 — Transfer + RLVR** | Test transfer to a tool-use/web/OS agent; probe TFA/progress as dense shaping for sparse terminal reward; audit reward hacking. | Evidence for/against transfer beyond math; reward-hacking audit report. |
| **B4 — Write-up** | Position as future-work follow-on to Plan A. | Honest scoping of where judge-free signals extend and where they break. |

## 6. Relationship to Plan A & dependencies
- **Depends on Plan A:** validated TFA definition, the harness, the shortcut control, and the multi-reference variant all carry over.
- **Reuses Plan A's discipline:** oracle-gate any synthetic gold (don't teacher-force against wrong traces); always report a free-run cross-check; keep the claims ledger.
- **Distinct contribution:** Plan A = *remove the judge (gold exists)*; Plan B = *extend judge-free signals to sparse feedback (gold is partial/absent)*. Kept as separate papers so neither is diluted (per the team's one-contribution rule).

## 7. Key risks
- **R-B1 — No clean win over PRMs/execution oracles.** Mitigate by framing as *annotation-free / model-free* alternative and reporting cost-quality tradeoffs, not just quality.
- **R-B2 — Progress-bridge is negative.** Still publishable as a characterization of when teacher-forcing signals do/don't generalize.
- **R-B3 — Reward hacking / self-consistent errors.** Audit from day one (Track B3, §4); never present a consensus/progress signal as a truth signal.
- **R-B4 — Compute (rollouts/RL) blows up.** Start with cheap math-multi-step envs before web/OS agents.

## 8. Deliverables
1. Synthetic/partial-gold TFA harness on ≥1 multi-step math env.
2. Head-to-head: synthetic-gold TFA vs. progress-ratio vs. PRM step scores.
3. A transfer study (math → one agentic env) with a reward-hacking audit.
4. A position on the consistency-vs-truth boundary for sparse-feedback judge-free evaluation.
