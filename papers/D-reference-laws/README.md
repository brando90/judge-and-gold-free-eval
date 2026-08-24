# Paper D — "When the Answer Key Backfires" — experiment runbook

This README lets a new author reproduce every number in the paper and continue the
experiment line. The paper shows that a trusted reference answer in an LLM judge's prompt
**inflates** best-of-n scores on tasks with more than one valid answer (preregistered,
osf.io/ym5x9), that the mechanism is causal anchoring (reference rotation), that the harm
switches on at exactly k=2 valid answers (osf.io/qugbd), and that scoring blind before
revealing the reference removes it.

Read first:
- `main.pdf` — the paper (v20). `main_v19_backup.tex` preserves the v7–v19 draft history.
- `../share/D-page-by-page-guide.md` — plain-language walkthrough of all 26 pages.
- `registration.md` — the internal prediction/outcome ledger (what was frozen when, every deviation).
- `../analysis/MANIFEST.md` — artifact → producer → registration map for every number.

## 0. Reproduce all numbers with no GPU (fresh clone, ~10 minutes)

All score files and task pools are committed. The analysis layer regenerates every JSON the
paper quotes; producers **must run from `experiments/tfa-vs-judge/`** (they read `runs/...`
and `scripts/bon_analysis.py` by relative path, and write `../../papers/analysis/*.json`).

```bash
cd experiments/tfa-vs-judge
python3 -m venv .venv-analysis && source .venv-analysis/bin/activate
pip install numpy scipy matplotlib

# Registered (frozen pre-run) producers — do not edit these files:
python ../../papers/analysis/repl_analysis.py        # -> repl_results.json      (osf.io/ym5x9, Table 2)
python ../../papers/analysis/mitigation_analysis.py  # -> mitigation_results.json (osf.io/qugbd, Table 7)
python ../../papers/analysis/synthk_analysis.py      # -> synthk_results.json    (grid, Tables 4-5)
python ../../papers/analysis/ties_dynamics.py        # -> ties_*.json            (exploratory section)
python ../../papers/analysis/ties_rot_controls.py    # -> ties_rot_controls.json (rotation, Table 3)
python ../../papers/analysis/ties_p2_margin.py       # -> ties_p2_margin.json    (original-arm margins)

# Post-hoc producers (review-round additions):
python ../../papers/analysis/synthk_paired.py        # paired step/level/trend + rotation McNemar
python ../../papers/analysis/round6_disclosures.py   # registered P-M contrasts, repl disclosures, pressure curve
python ../../papers/analysis/round7_linkage.py       # band match + margin-inflation linkage
python ../../papers/analysis/round8_followups.py     # n=83 recompute, M1 pressure sweep
python ../../papers/analysis/round9_provenance.py    # linkage power, composition, worked example

# Figures and paper:
python ../../papers/D-reference-laws/scripts/generate_plots.py
cd ../../papers/D-reference-laws && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Monte Carlo seeds are fixed, but regenerated bootstrap bounds can move by up to ~0.02
against the frozen registered runs — if you regenerate, re-sync any changed digit into the
paper. Never hand-edit a number.

## 1. The five experiments

Cluster scripts live in `experiments/tfa-vs-judge/scripts/` but run from the **cluster repo
root** (they were copied to `/lfs/skampere1/0/srivatsavad/tfa-vs-judge/`, see §3). Shared
machinery: `bon_generate.py` (vLLM best-of-64 sampler, temp 1.0, seed 0, resumable),
`bon_oracle.py` / `repl_oracle.py` (validity labeling, CPU-only), `bon_judge.py` (vLLM
judge; score = logprob-expected value over tokens 0..10; **skips existing out files**),
`bon_rubrics.py` (frozen rubric text), `bon_analysis.py` (the pre-registered estimator
library every analysis `exec`s). No API keys anywhere on this path — all open-weights vLLM.

| # | Experiment | Build tasks | Generate + judge | Scores land in | Analysis producer |
|---|---|---|---|---|---|
| a | Exploratory Ties pool (51 items) | `build_bon_ties_tasks.py` → `runs/bon_ties_tasks.jsonl` | `bon_chain_ties.sh GPU` (in-band grid) + `pipeline2.sh GPU` (full-set grid) | `runs/bon_scores_v2/ties__*` (in-band) and `runs/bon_scores_ties_full/` | `ties_dynamics.py`, `ties_p2_margin.py` |
| b | Reference rotation | no builder — the rotated pool `runs/bon/bon_tiesrot__Qwen__Qwen2.5-7B-Instruct.jsonl` is a committed data artifact (commit `718c399`, pre-re-judging; pool-aware assignment disclosed in `registration.md`) | `pipeline3.sh GPU` | `runs/bon_scores_ties_rot/` | `ties_rot_controls.py` (+ McNemar in `synthk_paired.py`) |
| c | Synthetic multiplicity grid (k∈{1,2,4,8,16}, 60 tasks, 6 judges) | `build_synth_multiplicity.py` → `runs/bon_synthk_tasks.jsonl` (P-S1..P-S5 in its header, commit `c505c23`) | `pipeline5.sh GPU` (+ `pipeline11.sh` for the P-S2b second phrasing) | `runs/bon_scores_synthk/`, `runs/bon_scores_synthk_llamagen/` | `synthk_analysis.py` (frozen), `synthk_paired.py` (post hoc) |
| d | Preregistered replication (120 constraint tasks) — **osf.io/ym5x9** | `build_replication_pool.py` → `runs/repl_{pilot,main}_tasks.jsonl` | `pipeline14.sh GPU` (pilot) then `pipeline15.sh GPU` (main) | `runs/bon_scores_repl/` (files named `synthk__*` — rubric reuse) | `repl_analysis.py` (frozen) |
| e | k-stratified mitigations M1/M2 (75 tasks) — **osf.io/qugbd** | `build_replication_pool.py --kstrat` → `runs/kstrat_tasks.jsonl` | `pipeline16.sh GPU` (blind/ref via `bon_judge.py`, M1/M2 via `mitigation_judge.py`) | `runs/bon_scores_kstrat/` (`synthk__*` = blind/ref, `kstrat__*` = M1/M2) | `mitigation_analysis.py` (frozen), contrasts in `round6_disclosures.py` |

Protocol details worth knowing: `mitigation_judge.py` implements M1 (blind call, then
reveal call — the reported score is call 2) and M2 (blind score × P(Yes) from a separate
validity call — the **soft** gate that deviates from the registered hard gate; public
amendment osf.io/kszeu). Selection always uses rubric `a`, reporting rubric `b`.

## 2. Where the results live

Everything a fresh clone needs is committed under `experiments/tfa-vs-judge/runs/`
(the directory is git-ignored by default; files were added explicitly — use `git add -f`
for new score files you want to keep):

- Task pools: `runs/{bon_ties,bon_synthk}_tasks.jsonl`, `runs/repl_{pilot,main}_tasks.jsonl`, `runs/kstrat_tasks.jsonl`
- Sample pools (64 samples/task + oracle labels): `runs/bon/bon_{ties,tiesrot,synthk,repl,replpilot,kstrat}__*.jsonl` (~26 MB)
- Judge scores: `runs/bon_scores_v2/ties__*` (in-band), `runs/bon_scores_ties_full/`, `runs/bon_scores_ties_rot/`, `runs/bon_scores_synthk/`, `runs/bon_scores_synthk_llamagen/`, `runs/bon_scores_repl/`, `runs/bon_scores_kstrat/` (~9 MB)
- Canonical numbers: `papers/analysis/*.json` (the paper quotes these, and only these)
- Figures: `figures/fig_{inversion,anchoring,synthk}.pdf`, regenerated by `scripts/generate_plots.py`

Related but **not** part of D's best-of-n pipeline: `runs/rb2ref_*.jsonl` /
`runs/rb2xref_*.jsonl` are the earlier *static* RewardBench-2 reference-arm experiment
(the "7–8 point verdict cost" motivation cited from companion paper A).

## 3. Running on the cluster (SNAP / skampere1)

One-time setup on a SNAP GPU box (pick one via the
[SNAP GPU stats](https://ilwiki.stanford.edu/doku.php?id=snap-servers:snap-gpu-servers-stats);
work under `/lfs`, not AFS; use `krbtmux` + kerberos reauth for long runs):

```bash
ssh skampere1   # if ssh fails from a script despite valid kinit, add: -o GSSAPIAuthentication=yes -o GSSAPIDelegateCredentials=yes
cd /lfs/$(hostname)/0/$USER
git clone https://github.com/brando90/judge-free-eval.git tfa-vs-judge-repo
# The pipelines expect the *flattened* layout: experiment scripts at the working-dir root.
mkdir -p tfa-vs-judge && cp -r tfa-vs-judge-repo/experiments/tfa-vs-judge/* tfa-vs-judge/
cd tfa-vs-judge
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # vllm, torch, transformers, datasets, numpy, scipy
mkdir -p logs runs
```

Launch pattern (identical in every `pipelineN.sh`): `bash pipelineN.sh <GPU>` starts one
`nohup` chain pinned to `CUDA_VISIBLE_DEVICES=<GPU>`, appends to `logs/pipelineN.log`, and
writes `PIPELINEN_DONE` as its last line. Later pipelines begin with
`until grep -q PIPELINE<M>_DONE logs/pipeline<M>.log; do sleep 300; done`, so you can queue
several on one GPU and they serialize themselves. Check progress with
`tail -f logs/pipelineN.log`; a chain is finished when its DONE marker appears.

Cluster etiquette and gotchas:
- **GPUs**: check `nvidia-smi` and coordinate before claiming; keep to ≤2 GPUs on shared boxes.
- **Everything is offline-first**: pipelines set `HF_HUB_OFFLINE=1` and expect weights in
  `$HF_HOME`; `pipeline17.sh` shows the pattern for downloading a new judge first.
- **Marker trap**: `pipeline14.sh` waits on `PIPELINE12C_DONE`, but `pipeline12b/12c` (and
  `pipeline4`, `pipeline13`) were never committed. On a fresh cluster checkout either edit
  out the `until` line or `echo PIPELINE12C_DONE >> logs/pipeline12c.log` before launching.
- **Idempotence**: `bon_generate.py` resumes by `problem_id`; `bon_judge.py` skips existing
  out files — delete a score file to force a re-judge.
- **Pulling results back**: `rsync -av skampere1:/lfs/skampere1/0/$USER/tfa-vs-judge/runs/bon_scores_<X>/ experiments/tfa-vs-judge/runs/bon_scores_<X>/`,
  then `git add -f` the files you want tracked.

What runs where: generation/judging (`bon_generate.py`, `bon_judge.py`,
`mitigation_judge.py`, oracles) = cluster GPU, no keys. Analysis producers, figure
generation, paper compilation, OSF posting (`scripts/osf_post.py`, needs `OSF_TOKEN`), and
the GPT-5.2 review loop (`scripts/gpt_review*.py`, needs `OPENAI_API_KEY`; spend ledger
`runs/bon_scores/gpt_spend.json` with hard caps) = local laptop.

## 4. The registration discipline (do not skip this)

The paper's credibility rests on this workflow; follow it for any new confirmatory claim:

1. Write the predictions and full analysis plan as a new block in
   `../registrations/osf_drafts.md`.
2. Commit the analysis producer and the pipeline script **before any data exists**.
3. Post the registration externally: `OSF_TOKEN=... python3 scripts/osf_post.py`
   (run from `experiments/tfa-vs-judge/`).
4. Run the pipeline; never touch the frozen producer afterward.
5. Score the predictions with the frozen producer; record outcomes (including partial and
   falsified) in `registration.md` and the paper's ledger (Appendix A).
6. Any deviation gets a public OSF amendment (precedent: osf.io/kszeu for the M2 soft gate).

Existing registrations: R3 = replication (osf.io/ym5x9), R4 = k-stratified mitigations
(osf.io/qugbd), R5 = judge-coverage extension (registered, **not yet run** — see §5).
R1/R2 belong to paper A. Amendment: osf.io/kszeu.

## 5. Continuing the work

**The registered next experiment is ready to launch.** Registration 5 (committed pre-data
in `e75e465`) extends the k-stratified mitigation experiment to three new judge families,
reusing the frozen pool and samples — only judging is new:

```bash
# on the cluster, one invocation per judge (any free GPUs):
bash pipeline17.sh <GPU> google/gemma-2-9b-it
bash pipeline17.sh <GPU> mistralai/Mistral-7B-Instruct-v0.3
bash pipeline17.sh <GPU> Qwen/Qwen2.5-14B-Instruct
# backup under the pre-stated substitution rule if a vLLM load fails: 01-ai/Yi-1.5-9B-Chat
```

Each writes `runs/bon_scores_kstrat/` score files and a per-judge
`PIPELINE17_<TAG>_DONE` marker. Predictions P-X1..P-X4 are in
`../registrations/osf_drafts.md` (Registration 5); score them per judge with the frozen
`mitigation_analysis.py` machinery and add the outcomes to the ledger.

Other open threads the paper names: M1 under optimizers stronger than best-of-64 (DPO
against the M1-scored judge), free-form tasks where validity isn't programmatically
checkable, long/uncertain references, and human adjudication of the Ties checker sample.

## 6. Known warts (documented so they don't bite you)

- Score files in `runs/bon_scores_repl/` and the blind/ref half of
  `runs/bon_scores_kstrat/` are named `synthk__*` because the judge was invoked with
  `--domain synthk` to reuse the frozen Ties rubric. The analysis scripts expect this.
- The rotation pool has **no builder script** — it is a committed data artifact, and its
  pool-aware construction is disclosed in `registration.md` and paper Appendix B.
- `papers/analysis/` contains some JSONs without a committed producer (e.g.
  `checker_audit.json`, `checker_adjudication.json`, `ties_corrected_delta.json`,
  `synthk_refinst2.json`); they are committed data. MANIFEST.md marks which is which.
- `bon_judge.py` skip-if-exists means a changed rubric or prompt does **not** re-score
  existing files — delete outputs deliberately when you intend a re-run.
- Paper-number drift of ~0.02 on bootstrap bounds after regeneration is expected (fixed
  seeds, regenerated resamples). The frozen registered artifacts in git are authoritative
  for the registered predictions.
