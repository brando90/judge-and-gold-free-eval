## PART 1 — cold read

### (a) 3-sentence summary
The paper argues that giving an LLM judge a single “trusted reference answer” *in multi-valid-answer tasks* makes the judge behave like an answer matcher, which under best-of-n selection inflates reported scores (“inflation”) rather than safeguarding against hacking. It supports this with (i) an externally preregistered replication on programmatically checkable tasks showing substantial extra inflation for referenced vs blind judging, and (ii) a causal “reference rotation” intervention where the *same text* gains up to **+9.5/10** just by switching the reference to match it. It then tests boundary conditions via k-controlled synthetic tasks and proposes a preregistered mitigation: **judge blind first, then reveal the reference**, which largely removes measured inflation at \(k>1\) for two judges, while leaving some residual anchoring in margins.

---

### (b) Scores (1–10) with concrete quotes

#### NOVELTY: **7/10**
What’s new relative to known “reference biases” is the *dynamic* best-of-n inflation story plus a preregistered, oracle-checkable replication and a causal rotation demonstration.
- Dynamic inversion framing: “**under best-of-n selection that inflates the scoreboard instead of protecting it**” (Abstract).
- Causal manipulation of reference: “**re-judged with the reference switched to a different valid answer, the identical text gains up to +9.5 points**” (Abstract / Fig 1 / Sec 3.2).
- Structural mitigation tested: “**have the judge score blind first, and reveal the reference only afterwards. That removes the measured inflation at k>1**” (Abstract; Table 7).

This is plausibly publishable novelty for NeurIPS/ICML *if* the claims stay scoped and the mitigation isn’t oversold.

#### SOUNDNESS: **7/10**
The core replication is fairly clean: external preregistration, exact oracles, cross-family generator-judge pair, frozen code, clear endpoints.
- “**externally preregistered replication… population, estimators, and endpoints frozen before any data existed**” (Abstract; Sec 3.1).
- Exact checker: “**validity is decided by direct arithmetic check**” (Sec 3.1).
- Primary endpoint clearly stated: “**P-R1… pooled… referenced-minus-blind inflation delta… +1.19 [+1.02, +1.36]**” (Sec 3.1, Table 2).

Main soundness weaknesses:
1. The mitigation’s robustness is not established against non-i.i.d. / adaptive optimization: “**optimizers that adapt to the judge rather than sampling independently, remain untested**” (Sec 3.4) and similarly in Limitations.
2. Some key interpretive moves lean on post-hoc analyses (step re-analysis Table 5; per-item linkage rejection; selection-pressure curve Table 9). You *label* them, which is good, but it still limits how hard you can lean on them.

Net: sound enough for a weak accept, but not bulletproof.

#### COMPLETENESS: **6/10**
You cover: replication, causal mechanism, boundary via k-control, multiple judges (some), and mitigations. But there are two conspicuous “missing completeness” holes for a top venue:
- Judge diversity for mitigation is thin: Table 7 uses only **two judges** (Qwen-7B, phi-4), and the paper admits: “**only two judges were run**” (Limitations).
- The key mitigation is not tested against the most relevant threat model (adaptive attacker), explicitly: “**budgets far beyond 64, and optimizers that adapt to the judge… remain untested**” (Sec 3.4), and limitations reiterate this.

Also, the synthetic grid has very small per-cell n (“**4 to 6 items enter each plotted cell**”, Fig 2 caption / Table 4 notes), making some strata-level conclusions fragile.

#### IMPACT: **8/10**
This hits a real evaluation practice. The message is crisp and operationally relevant: “**A reference answer is a lever, not a safeguard**” (Abstract).
If correct, it changes how people design automated evaluations for open-ended / multi-answer tasks and “reward hacking” mitigations. The “blind-then-reveal” protocol is actionable, even if it adds a second judge call: “**The price is one extra judge call per candidate**” (Table 10).

Impact is tempered by scope: “**free-form generation is outside our scope**” (Abstract), and many real benchmarks are not programmatically checkable.

---

### (c) READABILITY verdict (for a new reader)
Readable for an expert, but still heavy and ledger-driven. The abstract is unusually long (12 sentences) but actually fairly informative. The main readability tax is the amount of bookkeeping (bands, populations, endpoints, “registered vs post hoc” qualifiers) embedded directly in the narrative; it is honest, but it makes the paper feel like an audit report more than a clean scientific story.

Two specific readability pain points:
- Definitions are dense and nested: “**Inflation, formally the excess hack gap… against a null built by shuffling judge scores among samples the checker grades identically**” (Sec 2). Accurate, but a first-time reader will still struggle.
- The synthetic grid section mixes “frozen registered estimator” with “post-hoc paired re-analysis” (Sec 3.3) in a way that is easy to misunderstand unless you’re already used to prereg culture.

---

### (d) Five highest-leverage concrete improvements (ranked)

1. **Test blind-then-reveal against an adaptive optimizer / attacker** (even a modest one).
   Right now the central mitigation is evaluated under i.i.d. sampling best-of-n; you explicitly concede the real threat model is untested: “**optimizers that adapt to the judge rather than sampling independently, remain untested**” (Sec 3.4). Add even one adaptive loop (e.g., CMA-ES over prompt variants, rejection sampling with judge feedback, or gradient-free search over discrete edits) to see whether residual margins “reappear” as inflation.

2. **Run the mitigation (Table 7 protocols) on more judge families.**
   You have 6 judges in the grid, but the *mitigation* results are only for Qwen-7B and phi-4. This is currently a general recommendation on very narrow evidence. Add at least 2–4 more judges spanning another family (Llama, GPT-like if possible), *for M1 specifically*.

3. **Tighten and simplify the boundary claim language to avoid “rule” vibes.**
   You mostly do this well in Sec 3.7 (“**directionally rather than as a law**”), but you still have “**Together the two results give a practitioner’s rule**” (Sec 3.7) which reads stronger than what P-S5 and Table 7 support. Replace “rule” with “working heuristic” and foreground the failed k=1 cross-generator leg.

4. **Clarify the inflation metric with a diagram and explicitly label what is randomized and what is conditioned.**
   The worked example helps, but most readers still won’t internalize “shuffle null among samples the checker grades identically” without a small schematic showing: pool → judge scores → selection → report score → truth gain → permutation null → excess hack gap → inflation delta.

5. **Separate “confirmatory claims” from “interesting exploratory extras” more aggressively in prose structure.**
   You say Sections 3.1–3.4 are load-bearing, but then Section 3.2 includes a big post-hoc linkage rejection and simulation. It’s honest, but it’s cognitively central and will distract reviewers. Consider moving the linkage analysis to a clearly-marked subsection or appendix and summarize it briefly in the mainline.

---

### (e) Overall score, accept/reject lean, confidence
**Overall: 7/10 (Weak Accept), confidence: 0.65.**

It’s a strong audit-style paper with an unusually clean preregistered replication and a clear causal mechanism demonstration. The main reason it stays “weak” rather than “clear accept” is that the recommended mitigation is not validated against the most relevant attacker model (adaptive optimization) and is only tested on two judges.

---

## PART 2 — ask audit (v17 asks)

### ASK 1. Adaptive attacker vs blind-then-reveal mitigation
**NOT RESOLVED.**
Evidence: Sec 3.4 explicitly says it’s untested: “**optimizers that adapt to the judge rather than sampling independently, remain untested**.” Also Limitations: “**M1’s harm removal is measured at best-of-64… untested against stronger optimization pressure**.”

### ASK 2. Add 2–4 more judge models across at least two more families for the mitigations
**NOT RESOLVED.**
Evidence: Mitigation experiment judges are only: “**the judges are Qwen2.5-7B-Instruct and phi-4**” (Sec 3.4; Table 7). The grid has more judges (Table 4/5/6), but that does **not** address mitigation generality.

### ASK 3. Make the k=2 step confirmatory or tone it down
**RESOLVED (mostly).**
Evidence: You anchor the step claim on the externally registered k-controlled experiment (not the exploratory grid):
- Abstract: “**on an externally registered pool with exactly k valid answers per item, the k=1-to-k>1 jump in inflation is confirmed for both judges**.”
- Sec 3.4: “**That statistic is the step… and it is +1.45… and +1.18… both excluding zero… The prediction is therefore carried by the registered contrast rather than by reading two columns of Table 7 side by side.**”
Exploratory six-judge grid is clearly demoted: “**post-hoc paired re-analysis**” (Sec 3.3; Table 5 caption).

### ASK 4. Add a worked example making the inflation metric concrete
**RESOLVED.**
Evidence: Setup now includes a concrete item walkthrough:
- “**One replication item… makes the units concrete… referenced judge… best-of-64 pick… a judge gain of 2.84… truth gain of 0.69… Netting each arm against its own shuffle null…**” (Sec 2, Measurements).

### ASK 5. Move load-bearing caveats out of table notes into main text
**PARTIALLY RESOLVED.**
You did move the key comparability issue into prose in Sec 3.4:
- “**it means the inflation numbers here and the +1.19 of Section 3.1 come from populations selected by different rules…**” (Sec 3.4).
and you explicitly discuss band-matching and residual non-comparability both in Table 7 notes and in text.
But you still have multiple load-bearing facts trapped in long Notes blocks (Table 2 notes are doing a lot of work; Table 7 notes contain the registered contrasts and key comparability argument). For a reviewer, it’s *better* than v17, but still too much of the scientific claim is hiding in Notes.

---

## PART 3 — three questions

### (a) Is the linkage retraction handled honestly/coherently, or still soft-pedaled?
Mostly honest and coherent; not perfect.

Good:
- Abstract states the new conclusion plainly: “**an exact item-level pathway… is rejected for both judges**.”
- Sec 3.2 explicitly admits the earlier mistake and why: “**An earlier draft swept the inflation measurement noise as unidentifiable… the split-half estimate shows it is identifiable, supersedes that sweep… The verdict is that an exact per-item linear pathway… is rejected**.”
- Ledger records it: Table 11 “**Linkage power analysis… pathway is rejected and the earlier ‘uninformative’ reading is retracted**.”
- Limitations reiterate: “**An earlier draft called this test uninformative; that reading was wrong and is retracted in Section 3.2 and the ledger.**”

Where it still soft-pedals (subtle):
- You keep a rhetorical “mechanism established causally” thread and then say “**This is a plausible account of why the inversion happens in aggregate**” (Sec 3.2) before the rejection. That’s fine, but it invites a reader to walk away thinking the margin→inflation story is basically right “except noise,” whereas your simulation-based rejection is stronger: it says *the simplest per-item linear story is not just underpowered; it’s inconsistent with the data given your measured noise*.
- “**aggregate correspondence between margins and inflation**” (Sec 3.2) is asserted without a clean quantitative aggregate test (you give per-item correlations, one near-zero, one modest). If you want to say “aggregate correspondence,” define it precisely (e.g., do you mean both are >0 at k>1?).

Net: no obvious dishonesty, but you still rhetorically center anchoring as “the” mechanism while showing your own attempted per-item mechanistic mapping fails.

### (b) Does the worked example make the inflation metric parseable to an outsider?
Partially. It’s a real improvement, but it remains too easy to get lost.

What works:
- You give actual numbers and walk through: pool validity count, mean/spread, selected score, standardized gain, shuffle-null subtraction, then net difference. This is the right kind of example.

What still fails for outsiders:
- You implicitly assume the reader already understands (i) what exactly “truth gain” is numerically (it appears as “0.69” with no explicit formula in the example), and (ii) how the shuffle null is constructed (“shuffling judge scores among samples the checker grades identically”)—still abstract without a schematic.
- The example mixes two different computations: “**+0.97 by this single-pick arithmetic; +1.26 under the committed estimator**.” That is honest, but it undermines the pedagogical goal: a worked example should ideally match the estimator you actually use, even if simplified.

So: better, but I would not bet on a random ICML reviewer fully parsing inflation from this alone.

### (c) Modal outcome prediction at a top-tier venue, and the single addition that most raises it
**Modal outcome: Weak Accept / borderline Accept**, with a meaningful chance of Reject depending on reviewer taste for “audit + prereg + limited scope” papers.

Why it could get rejected:
- Some reviewers will treat “only short-answer with exact oracles; free-form out of scope” as too narrow.
- Others will say the central mitigation recommendation is premature without adaptive attacker testing and without more judge families on the mitigation.

**Single addition that most raises acceptance odds:**  
Run **one adaptive optimization experiment** (even small-scale) explicitly targeting M1 (blind-then-reveal), to test whether residual anchoring margins can be exploited into inflation under adaptive search. This directly addresses the biggest “practical safety” gap and would convert your mitigation from “promising under i.i.d. sampling” into something closer to a robust procedural recommendation.

---

### Final blunt note: what you’re hoping reviewers miss
- The mitigation is sold in Table 10 as the “only one” that “removes measured inflation” and “behaves the same for both judges,” but you also report a nontrivial residual anchoring margin and explicitly admit the real attacker model is untested. That tension is real; some reviewers will call it out as overreach unless you add adaptive tests.
- The six-judge grid is underpowered per cell (4–6 items/cell), and the “reference helps at k=1” story is shaky cross-generator (P-S5 fails) and even in Section 3.4 you admit k=1 “helps” rests on *one judge* and M1 doesn’t preserve that benefit. You did tone it down, but the narrative still leans on the comforting symmetry “unique good / multi bad” more than the data warrants.