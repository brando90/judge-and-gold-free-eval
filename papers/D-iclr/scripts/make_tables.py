#!/usr/bin/env python
"""Appendix tables for the ICLR version of Paper D, generated from papers/analysis/*.json.

Writes LaTeX fragments into papers/D-iclr/tables/. Tables whose producer JSON is not
machine-readable in a stable shape (the exploratory rotation ladder, the MBPP exemplar
table, the DPO gates) are typed in appendix.tex and checked by check_numbers.py instead.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
A = PAPER.parent / "analysis"
OUT = PAPER / "tables"
OUT.mkdir(exist_ok=True)

Q, P = "Qwen__Qwen2.5-7B-Instruct", "microsoft__phi-4"


def J(name):
    return json.loads((A / name).read_text())


def _z(x, d):
    return 0.0 if round(x, d) == 0 else x


def f(x, d=2):
    return f"${_z(x, d):+.{d}f}$"


def c(lo, hi, d=2):
    return f"{{\\scriptsize$[{_z(lo, d):+.{d}f},{_z(hi, d):+.{d}f}]$}}"


def fc(x, ci, d=2):
    return f"{f(x, d)} {c(ci[0], ci[1], d)}"


def write(name, body):
    (OUT / name).write_text(body)


# ---------------------------------------------------------------- replication robustness
itt = J("repl_itt_sensitivity.json")
disc = J("repl_disclosures.json")
pc = J("repl_pressure_curve.json")
rows = [
    ("Preregistered band (primary), 105 tasks", itt["inband"]),
    ("All 120 tasks (intention to treat)", itt["itt_all"]),
    ("15 out-of-band tasks only", itt["outband"]),
]
body = ["\\begin{tabular}{lccc}", "\\toprule",
        "Population & Qwen2.5-7B & phi-4 & Pooled \\\\", "\\midrule"]
for lab, r in rows:
    body.append(f"{lab} & {fc(r['per_judge'][Q]['delta'], r['per_judge'][Q]['ci'])} & "
                f"{fc(r['per_judge'][P]['delta'], r['per_judge'][P]['ci'])} & {fc(r['pooled'], r['ci'])} \\\\")
t = disc["E1_top_tercile_boxed"]
body.append(f"Top tercile of answer-format compliance, {t['n']} tasks & & & {fc(t['delta'], t['ci'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("repl_robust.tex", "\n".join(body) + "\n")

body = ["\\begin{tabular}{l" + "c" * 6 + "}", "\\toprule",
        "Best-of-$n$ & " + " & ".join(f"$n{{=}}{n}$" for n in (2, 4, 8, 16, 32, 64)) + " \\\\", "\\midrule",
        "Paired gap & " + " & ".join(f(pc[f"n={n}"]["delta"], 3) for n in (2, 4, 8, 16, 32, 64)) + " \\\\",
        "95\\% CI & " + " & ".join(c(*pc[f"n={n}"]["ci"], d=3) for n in (2, 4, 8, 16, 32, 64)) + " \\\\",
        "\\bottomrule", "\\end{tabular}"]
write("repl_pressure.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- exact-oracle rotation
rr = J("replrot_results.json")
fr = J("frontier_phase1_results.json")
body = ["\\begin{tabular}{llcccc}", "\\toprule",
        "Judge & Rubric & Moved onto ($n{=}120$) & Moved off ($n{=}93$) & Neither ($n{=}113$) & Onto minus neither \\\\",
        "\\midrule"]
for name, key in (("Qwen2.5-7B", Q), ("phi-4", P)):
    for rep in ("a", "b"):
        r = rr[f"{key}__{rep}"]
        body.append(f"{name if rep == 'a' else ''} & ${rep}$ & {fc(r['gainers']['mean'], r['gainers']['ci'])} & "
                    f"{fc(r['losers']['mean'], r['losers']['ci'])} & {fc(r['placebo']['mean'], r['placebo']['ci'])} & "
                    f"{fc(r['gainer_minus_placebo']['mean'], r['gainer_minus_placebo']['ci'])} \\\\")
for rep in ("a", "b"):
    r = fr[f"rotation__{rep}"]
    body.append(f"{'Claude Sonnet 5' if rep == 'a' else ''} & ${rep}$ & {fc(r['gainers']['mean'], r['gainers']['ci'])} & "
                f"{fc(r['losers']['mean'], r['losers']['ci'])} & {fc(r['placebo']['mean'], r['placebo']['ci'])} & "
                f"{fc(r['gainer_minus_placebo']['mean'], r['gainer_minus_placebo']['ci'])} \\\\")
r = fr["rotation_filtered__a"]
body.append(f"\\quad blind-certified only & $a$ & {fc(r['gainers']['mean'], r['gainers']['ci'])} & "
            f"{fc(r['losers']['mean'], r['losers']['ci'])} & {fc(r['placebo']['mean'], r['placebo']['ci'])} & "
            f"{fc(r['gainer_minus_placebo']['mean'], r['gainer_minus_placebo']['ci'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("rotation_exact.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- k-pool per stratum
mit = J("mitigation_results.json")["E2_gap_deltas"]
body = ["\\begin{tabular}{lcccccc}", "\\toprule",
        " & \\multicolumn{3}{c}{Qwen2.5-7B} & \\multicolumn{3}{c}{phi-4} \\\\",
        "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
        "$k$ & reference & blind, then reveal & validity gate & reference & blind, then reveal & validity gate \\\\", "\\midrule"]
for k, lab in (("k1", "1"), ("k2", "2"), ("k4", "4"), ("k8", "8"), ("k16", "16"), ("kgt1", "pooled $>1$")):
    cells = []
    for key in (Q, P):
        for cond in ("ref", "m1", "m2"):
            x = mit[f"{key}|{cond}|{k}"]
            cells.append(fc(x["delta"], x["ci"]))
    if k == "kgt1":
        body.append("\\midrule")
    body.append(f"{lab} & " + " & ".join(cells) + " \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("kpool.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- synthetic grid
sg = J("synthk_paired.json")
names = [("Qwen__Qwen2.5-1.5B-Instruct", "Qwen2.5-1.5B"), ("Qwen__Qwen2.5-3B-Instruct", "Qwen2.5-3B"),
         ("Qwen__Qwen2.5-7B-Instruct", "Qwen2.5-7B"), ("Qwen__Qwen2.5-14B-Instruct", "Qwen2.5-14B"),
         ("meta-llama__Llama-3.1-8B-Instruct", "Llama-3.1-8B"), ("microsoft__phi-4", "phi-4")]
body = ["\\begin{tabular}{lcccc}", "\\toprule",
        "Judge & At $k{=}1$ & Pooled $k{>}1$ & Step & Slope per doubling of $k$ \\\\", "\\midrule"]
for key, name in names:
    pp, st, tr = sg["paired_pooled"][key], sg["step"][key], sg["trend"][key]
    body.append(f"{name} & {fc(pp['delta_k1'], pp['ci_k1'])} & {fc(pp['delta_kgt1'], pp['ci_kgt1'])} & "
                f"{fc(st['step'], st['ci'])} & {fc(tr['slope_per_log2k'], tr['ci'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("grid.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- coverage extension
cov = J("p17_coverage_results.json")
body = ["\\begin{tabular}{lccccc}", "\\toprule",
        "Judge & Reference, $k{=}1$ & Reference, $k{>}1$ & Blind-then-reveal, $k{>}1$ & Validity gate, $k{>}1$ & Reveal minus reference \\\\",
        "\\midrule"]
for key, name in (("Qwen__Qwen2.5-14B-Instruct", "Qwen2.5-14B"), ("google__gemma-2-9b-it", "gemma-2-9b"),
                  ("mistralai__Mistral-7B-Instruct-v0.3", "Mistral-7B")):
    r = cov[key]
    body.append(f"{name} & {fc(r['ref_k1']['delta'], r['ref_k1']['ci'])} & {fc(r['ref_kgt1']['delta'], r['ref_kgt1']['ci'])} & "
                f"{fc(r['m1_kgt1']['delta'], r['m1_kgt1']['ci'])} & {fc(r['m2_kgt1']['delta'], r['m2_kgt1']['ci'])} & "
                f"{fc(r['m1_minus_ref_kgt1']['delta'], r['m1_minus_ref_kgt1']['ci'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("coverage.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- MACE
mace = J("mace_results.json")["predictions"]
body = ["\\begin{tabular}{llccc}", "\\toprule",
        "Judge & Domain & $k{=}1$ & $k{>}1$ & Step \\\\", "\\midrule"]
for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
    for dom, lab in (("nonmath", "River + Language"), ("River", "\\quad River"), ("Language", "\\quad Language"),
                     ("math", "Math (control)")):
        r = mace[key][dom]
        body.append(f"{name if dom == 'nonmath' else ''} & {lab} & {fc(r['k1'][0], r['k1'][1])} & "
                    f"{fc(r['kgt1'][0], r['kgt1'][1])} & {fc(r['step'][0], r['step'][1])} \\\\")
    if key == Q:
        body.append("\\addlinespace")
body += ["\\bottomrule", "\\end{tabular}"]
write("mace.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- masking suite
mi = J("maskident_results.json")
body = ["\\begin{tabular}{llcccc}", "\\toprule",
        "Judge & Rubric & Numeral & Words & Expression & Worked: visible $\\to$ masked \\\\", "\\midrule"]
for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
    for rep in ("a", "b"):
        base = mi[f"{key}|{rep}|ref (baseline)"]
        w = mi[f"{key}|{rep}|refword"]
        e = mi[f"{key}|{rep}|refexpr"]
        s = mi[f"{key}|{rep}|refsolmask"]
        body.append(f"{name if rep == 'a' else ''} & ${rep}$ & {fc(base['margin'], base['ci'])} & {fc(w['margin'], w['ci'])} & "
                    f"{fc(e['margin'], e['ci'])} & {fc(s['refsol']['mean'], s['refsol']['ci'])} $\\to$ {fc(s['masked']['mean'], s['masked']['ci'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("masking.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- recoverability (cipher)
rc = J("recoverability_results.json")["margin"]
body = ["\\begin{tabular}{lcccc}", "\\toprule",
        "Judge & Plain reference & One decode step & Two steps & Three steps \\\\", "\\midrule"]
for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
    cells = [fc(rc[f"{key}|{lvl}"]["mean"], rc[f"{key}|{lvl}"]["ci"]) for lvl in ("bare", "cipher1", "cipher2", "cipher3")]
    body.append(f"{name} & " + " & ".join(cells) + " \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("cipher.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- continuum
sc = J("sep_continuum_results.json")
body = ["\\begin{tabular}{llcccc}", "\\toprule",
        "Judge & Readout & Integer & Pair & JSON & Program \\\\", "\\midrule"]
for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
    body.append(f"{name} & added inflation ($n{{=}}25$) & " +
                " & ".join(fc(sc[key][s]["infl"], sc[key][s]["infl_ci"]) for s in ("scalar", "pair", "json", "program")) + " \\\\")
    body.append(" & anchoring margin & " +
                " & ".join((f"{f(sc[key][s]['margin'])} {{\\scriptsize($n{{=}}{sc[key][s]['n_margin']}$)}}" if sc[key][s]['n_margin'] >= 5 else f"--- {{\\scriptsize($n{{=}}{sc[key][s]['n_margin']}$)}}")
                           for s in ("scalar", "pair", "json", "program")) + " \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("continuum.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- M1 variants
mv = J("m1_variants_results.json")
mg = J("m1_variants_gemma_results.json")
body = ["\\begin{tabular}{lcccc}", "\\toprule",
        "Judge & Own blind score & No score & Neutral wording & Other judge's score \\\\", "\\midrule"]
for src, key, name in ((mv, Q, "Qwen2.5-7B"), (mv, P, "phi-4"), (mg, "google__gemma-2-9b-it", "gemma-2-9b")):
    body.append(f"{name} & " + " & ".join(fc(src[f"{key}|{v}"]["infl"], src[f"{key}|{v}"]["infl_ci"])
                                         for v in ("m1", "m1noscore", "m1prev", "m1indep")) + " \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("m1variants.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- composition
dose = J("exploit_dose.json")["judges"]
body = ["\\begin{tabular}{lccccc}", "\\toprule",
        "Judge & $d{=}0$ & $d{=}1$ & $d{=}2$ & $d{=}4$ & $d{=}4$ minus $d{=}0$ \\\\", "\\midrule"]
for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4")):
    r = dose[key]
    body.append(f"{name} & " + " & ".join(fc(r[str(d)]["delta"], r[str(d)]["ci"]) for d in (0, 1, 2, 4)) +
                f" & {fc(r['dose4_minus_dose0']['delta'], r['dose4_minus_dose0']['ci'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("dose.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- resolution screen
rs = J("score_resolution_screen.json")["judges"]
body = ["\\begin{tabular}{lcccc}", "\\toprule",
        "Judge & Distinct score values & Blind ties at max (of 64) & Blind selection accuracy & Anchoring margin \\\\", "\\midrule"]
for key, name in ((Q, "Qwen2.5-7B"), (P, "phi-4"), ("Qwen__Qwen2.5-14B-Instruct", "Qwen2.5-14B"),
                  ("google__gemma-2-9b-it", "gemma-2-9b"), ("mistralai__Mistral-7B-Instruct-v0.3", "Mistral-7B")):
    r = rs[key]
    body.append(f"{name} & {r['distinct_values']} & {r['mean_ties_at_max']:.1f} & {r['selection_accuracy']:.3f} & {f(r['anchoring_margin'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("resolution.tex", "\n".join(body) + "\n")

# ---------------------------------------------------------------- frontier API judges
p2 = J("frontier_phase2_results.json")
fi = J("frontier_instruction_results.json")
g = "openai__gpt-4.1-2025-04-14"
s5 = "anthropic__claude-sonnet-5"
body = ["\\begin{tabular}{lcc}", "\\toprule", "Readout & GPT-4.1 & Claude Sonnet 5 \\\\", "\\midrule",
        f"Replication pool: added inflation ($n{{=}}105$) & {fc(p2['repl_delta__' + g]['delta'], p2['repl_delta__' + g]['ci'])} & --- \\\\",
        f"Replication pool: referenced-only / blind-only picks & {p2['repl_collapse__' + g]['ref_only']} / {p2['repl_collapse__' + g]['blind_only']} & --- \\\\",
        f"Replication pool: anchoring margin & {fc(p2['repl_margin__' + g]['margin'], p2['repl_margin__' + g]['ci'])} & --- \\\\",
        f"$k$-pool: step $k{{>}}1$ minus $k{{=}}1$ & {fc(p2['kstrat_step__' + g]['step'], p2['kstrat_step__' + g]['ci'])} & --- \\\\",
        f"$k$-pool margin, reference & {fc(fi[g + '__margin_ref']['mean'], fi[g + '__margin_ref']['ci'])} & {fc(fi[s5 + '__margin_ref']['mean'], fi[s5 + '__margin_ref']['ci'])} \\\\",
        f"\\quad + any-valid-answer instruction & {fc(fi[g + '__margin_refinst']['mean'], fi[g + '__margin_refinst']['ci'])} & {fc(fi[s5 + '__margin_refinst']['mean'], fi[s5 + '__margin_refinst']['ci'])} \\\\",
        f"\\quad + do-not-compare instruction & {fc(fi[g + '__margin_refinst2']['mean'], fi[g + '__margin_refinst2']['ci'])} & {fc(fi[s5 + '__margin_refinst2']['mean'], fi[s5 + '__margin_refinst2']['ci'])} \\\\",
        f"$k$-pool margin, blind & {fc(fi[g + '__margin_noref']['mean'], fi[g + '__margin_noref']['ci'])} & {fc(fi[s5 + '__margin_noref']['mean'], fi[s5 + '__margin_noref']['ci'])} \\\\",
        "\\bottomrule", "\\end{tabular}"]
write("frontier_api.tex", "\n".join(body) + "\n")

print("wrote", sorted(p.name for p in OUT.iterdir()))

# ---------------------------------------------------------------- training (DPO)
mv1 = J("dpo_mv_results.json")
mv3 = J("dpo_mv3_results.json")
fp = J("dpo_failure_profile.json")
body = ["\\begin{tabular}{llccc}", "\\toprule",
        "Run & Arm & Own-judge gain (gate) & Wedge (points) & Held-out accuracy change \\\\", "\\midrule",
        f"1 (4 ep., lr $2{{\\times}}10^{{-5}}$) & reference & {fc(mv1['gate']['ref'][0], mv1['gate']['ref'][1])} & "
        f"{fc(mv1['P_DP2']['ref_wedge'][0], mv1['P_DP2']['ref_wedge'][1])} & {fc(mv1['P_DP3']['ref_heldout'][0], mv1['P_DP3']['ref_heldout'][1], 3)} \\\\",
        f" & blind-then-reveal & {fc(mv1['gate']['m1'][0], mv1['gate']['m1'][1])} & "
        f"{fc(mv1['P_DP2']['m1_wedge'][0], mv1['P_DP2']['m1_wedge'][1])} & {fc(mv1['P_DP3']['m1_heldout'][0], mv1['P_DP3']['m1_heldout'][1], 3)} \\\\",
        "\\addlinespace",
        f"3 (2 ep., lr $10^{{-5}}$) & reference & {fc(mv3['gate']['ref'][0], mv3['gate']['ref'][1])} & "
        f"{fc(mv3['P_DPF1_wedge_ref_minus_m1']['ref_wedge'][0], mv3['P_DPF1_wedge_ref_minus_m1']['ref_wedge'][1])} & {fc(mv3['P_DPF2_heldout_m1_minus_ref']['ref'][0], mv3['P_DPF2_heldout_m1_minus_ref']['ref'][1], 3)} \\\\",
        f" & blind-then-reveal & {fc(mv3['gate']['m1'][0], mv3['gate']['m1'][1])} & "
        f"{fc(mv3['P_DPF1_wedge_ref_minus_m1']['m1_wedge'][0], mv3['P_DPF1_wedge_ref_minus_m1']['m1_wedge'][1])} & {fc(mv3['P_DPF2_heldout_m1_minus_ref']['m1'][0], mv3['P_DPF2_heldout_m1_minus_ref']['m1'][1], 3)} \\\\",
        f" & blind judge & {fc(mv3['gate']['blind'][0], mv3['gate']['blind'][1])} & "
        f"{fc(mv3['P_DPB1_wedge_ref_minus_blind']['blind_wedge'][0], mv3['P_DPB1_wedge_ref_minus_blind']['blind_wedge'][1])} & {fc(mv3['P_DPF2_heldout_m1_minus_ref']['blind'][0], mv3['P_DPF2_heldout_m1_minus_ref']['blind'][1], 3)} \\\\",
        "\\bottomrule", "\\end{tabular}"]
write("dpo.tex", "\n".join(body) + "\n")

body = ["\\begin{tabular}{lcccccc}", "\\toprule",
        "Policy (items) & Accuracy & Boxed answers & Mean length (chars) & 4-gram repetition & Unboxed and valid & Unboxed and invalid \\\\", "\\midrule"]
for key, lab in (("base_train", "Base, train (60)"), ("ref_train", "Reference arm, train (60)"), ("m1_train", "Reveal arm, train (60)"),
                 ("base_heldout", "Base, held out (120)"), ("ref_heldout", "Reference arm, held out (120)"), ("m1_heldout", "Reveal arm, held out (120)")):
    r = fp[key]
    body.append(f"{lab} & {r['accuracy']:.3f} & {r['boxed_rate']:.3f} & {r['mean_len']:.0f} & {r['mean_4gram_repeat']:.3f} & "
                f"{r['unboxed_but_valid']} & {r['unboxed_and_invalid']} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("dpo_profile.tex", "\n".join(body) + "\n")
print("wrote training tables")

# ---------------------------------------------------------------- round 2: plain-unit readouts
acc = J("accuracy_readouts.json")
KJ = [("Qwen2.5-7B", Q), ("phi-4", P), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct"),
      ("gemma-2-9b", "google__gemma-2-9b-it"), ("Mistral-7B", "mistralai__Mistral-7B-Instruct-v0.3")]


def pp(v):
    return f"${_z(100 * v[0], 1):+.1f}$ {{\\scriptsize$[{_z(100 * v[1][0], 1):+.1f},{_z(100 * v[1][1], 1):+.1f}]$}}"


body = ["\\begin{tabular}{llcccccc}", "\\toprule",
        "Judge & Protocol & $k{=}1$ & $k{=}2$ & $k{=}4$ & $k{=}8$ & $k{=}16$ & pooled $k{>}1$ \\\\", "\\midrule"]
for name, key in KJ:
    d = acc["kpool"][key]
    for cond, lab in (("ref", "reference"), ("m1", "blind, then reveal"), ("m2", "validity gate")):
        kk = f"{cond}_minus_blind"
        if kk not in d["k1"]:
            continue
        est = " & ".join(f"${_z(100 * d[st][kk][0], 1):+.1f}$" for st in ("k1", "k2", "k4", "k8", "k16", "kgt1"))
        cis = " & ".join(f"{{\\scriptsize$[{_z(100 * d[st][kk][1][0], 0):+.0f},{_z(100 * d[st][kk][1][1], 0):+.0f}]$}}"
                         for st in ("k1", "k2", "k4", "k8", "k16", "kgt1"))
        body.append(f"{name if cond == 'ref' else ''} & {lab} & {est} \\\\")
        body.append(f" & & {cis} \\\\")
    body.append("\\addlinespace")
body[-1] = "\\bottomrule"
body += ["\\end{tabular}"]
write("acc_kpool.tex", "\n".join(body) + "\n")

body = ["\\begin{tabular}{lcccc}", "\\toprule",
        "Judge & Blind accuracy & With reference & Change (points) & False rejections, blind $\\to$ reference \\\\", "\\midrule"]
for name, key in (("Qwen2.5-7B", Q), ("phi-4", P)):
    d = acc["repl"][key]
    fr = d["false_reject"]
    body.append(f"{name} & {100 * d['acc_blind'][0]:.1f}\\% & {100 * d['acc_ref'][0]:.1f}\\% & {pp(d['acc_ref_minus_blind'])} & "
                f"{100 * fr['blind_nonmatch'][0]:.1f}\\% $\\to$ {100 * fr['ref_nonmatch'][0]:.1f}\\% \\\\")
s5 = acc["repl_sonnet5_false_reject"]
body.append(f"Claude Sonnet 5 & --- & --- & --- & {100 * s5['blind_nonmatch'][0]:.1f}\\% $\\to$ {100 * s5['ref_nonmatch'][0]:.1f}\\% \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("acc_repl.tex", "\n".join(body) + "\n")

body = ["\\begin{tabular}{lccc}", "\\toprule", "Qwen2.5 judge & Blind & With reference & Change (points) \\\\", "\\midrule"]
for size in ("1.5B", "3B", "7B", "14B"):
    d = acc["math"].get(f"Qwen__Qwen2.5-{size}-Instruct")
    if d:
        body.append(f"{size} & {100 * d['acc_blind'][0]:.1f}\\% & {100 * d['acc_ref'][0]:.1f}\\% & {pp(d['acc_ref_minus_blind'])} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("acc_math.tex", "\n".join(body) + "\n")

body = ["\\begin{tabular}{lccccc}", "\\toprule",
        "Judge & Reference & Reveal, own score & Reveal, no score & Reveal, neutral wording & Reveal, other judge's score \\\\", "\\midrule"]
for name, key in (("Qwen2.5-7B", Q), ("phi-4", P), ("gemma-2-9b", "google__gemma-2-9b-it")):
    d = acc["kpool_variants"][key]
    body.append(f"{name} & " + " & ".join(pp(d[f"{cc}_minus_blind"]) for cc in ("ref", "m1", "m1noscore", "m1prev", "m1indep")) + " \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("acc_variants.tex", "\n".join(body) + "\n")

pv = J("prevalence_results.json")
body = ["\\begin{tabular}{llccccc}", "\\toprule",
        "Dataset & Source & Multiple / unique / unclear & Multiple-answer rate & Cohen's $\\kappa$ \\\\", "\\midrule"]
body[0] = "\\begin{tabular}{llccc}"
for key, lab, src in (("math500", "MATH-500", "test"), ("gsm8k", "GSM8K", "test"), ("deepscaler", "DeepScaleR-Preview", "train"),
                      ("nqopen", "NQ-open", "validation")):
    d = pv.get(key)
    if not d:
        continue
    kap = d.get("kappa_multi_vs_rest")
    body.append(f"{lab} & {src} & {d['multi']} / {d['unique']} / {d['unclear']} & {100 * d['rate']:.1f}\\% "
                f"{{\\scriptsize$[{100 * d['wilson_ci'][0]:.1f},{100 * d['wilson_ci'][1]:.1f}]$}} & {('%.2f' % kap) if kap is not None else '---'} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("prevalence.tex", "\n".join(body) + "\n")
print("wrote round-2 tables")

# ---------------------------------------------------------------- round 2 experiments
r2a = J("r2_math_m1_results.json")
body = ["\\begin{tabular}{lccccc}", "\\toprule",
        "Judge & Blind & Reference & Blind, then reveal & Reveal minus reference (points) & Call-1 vs.\\ frozen blind $r$ \\\\", "\\midrule"]
for name, key in (("Qwen2.5-7B", "Qwen__Qwen2.5-7B-Instruct"), ("Qwen2.5-14B", "Qwen__Qwen2.5-14B-Instruct")):
    d = r2a.get(key)
    if isinstance(d, dict):
        body.append(f"{name} & {100 * d['acc_blind']:.1f}\\% & {100 * d['acc_ref']:.1f}\\% & {100 * d['acc_m1']:.1f}\\% & "
                    f"{pp(d['m1_minus_ref'])} & {d['call1_vs_frozen_blind_r']:.3f} \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("r2a.tex", "\n".join(body) + "\n")

r2b = J("r2_realism_results.json")
rows_rot = ["\\begin{tabular}{lccc}", "\\toprule",
            "Protocol & Moved onto & No longer matches & Neither \\\\", "\\midrule"]
rows_k = ["\\begin{tabular}{lccc}", "\\toprule",
          "Protocol & Margin, $k{>}1$ (ref $-$ blind) & Accuracy change, $k{=}1$ & Accuracy change, $k{>}1$ \\\\", "\\midrule"]
for key, lab in (("mtbench", "MT-Bench template, Qwen2.5-7B"), ("reason", "Thinking judge, Qwen3-8B")):
    d = r2b.get(key)
    if not isinstance(d, dict) or "rot" not in d or "ksub" not in d:
        continue
    ro, ks = d["rot"], d["ksub"]
    rows_rot.append(f"{lab} & {fc(ro['gainer'][0], ro['gainer'][1], 3)} & {fc(ro['loser'][0], ro['loser'][1], 3)} & {fc(ro['placebo'][0], ro['placebo'][1], 3)} \\\\")
    rows_k.append(f"{lab} & {fc(ks['margin_diff_kgt1'][0], ks['margin_diff_kgt1'][1])} & {pp(ks['acc_delta_k1'])} & {pp(ks['acc_delta_kgt1'])} \\\\")
write("r2b.tex", "\n".join(rows_rot + ["\\bottomrule", "\\end{tabular}"]) + "\n")
write("r2b_k.tex", "\n".join(rows_k + ["\\bottomrule", "\\end{tabular}"]) + "\n")
print("wrote r2 tables")

# ---------------------------------------------------------------- round 3: thinking toggle, MACE natural pool
tog = J("r3_toggle_results.json")
diag = J("r3_toggle_diagnostics.json")
body = ["\\begin{tabular}{llcccc}", "\\toprule",
        "Task type & Readout & Thinking off & Thinking on & Tokens (off / on) \\\\", "\\midrule"]
body[0] = "\\begin{tabular}{llccc}"
body.append(f"Arithmetic (rotation) & moved onto & {fc(tog['off']['rot']['gainer'][0], tog['off']['rot']['gainer'][1], 3)} & {fc(tog['on']['rot']['gainer'][0], tog['on']['rot']['gainer'][1], 3)} & {diag['rot|off|ref']['tokens_mean']} / {diag['rot|on|ref']['tokens_mean']} \\\\")
body.append(f" & no longer matches & {fc(tog['off']['rot']['loser'][0], tog['off']['rot']['loser'][1], 3)} & {fc(tog['on']['rot']['loser'][0], tog['on']['rot']['loser'][1], 3)} & \\\\")
body.append(f" & matches neither & {fc(tog['off']['rot']['placebo'][0], tog['off']['rot']['placebo'][1], 3)} & {fc(tog['on']['rot']['placebo'][0], tog['on']['rot']['placebo'][1], 3)} & \\\\")
body.append(f"Arithmetic ($k$-subsample) & margin, ref $-$ blind & {fc(*tog['off']['ksub']['margin_diff_kgt1'][:2])} & {fc(*tog['on']['ksub']['margin_diff_kgt1'][:2])} & {diag['ksub|off|ref']['tokens_mean']} / {diag['ksub|on|ref']['tokens_mean']} \\\\")
body.append(f"Factual (MACE subsample) & margin, ref $-$ blind & {fc(*tog['off']['macesub']['margin_diff'][:2])} & {fc(*tog['on']['macesub']['margin_diff'][:2])} & {diag['macesub|off|ref']['tokens_mean']} / {diag['macesub|on|ref']['tokens_mean']} \\\\")
body.append(f" & false rejections, ref $-$ blind & {pp(tog['off']['macesub']['false_reject_diff'])} & {pp(tog['on']['macesub']['false_reject_diff'])} & \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("toggle.tex", "\n".join(body) + "\n")

mace3 = J("r3_mace_accuracy_results.json")
body = ["\\begin{tabular}{llcccccc}", "\\toprule",
        "Judge & Tasks & Blind & Reference & Reveal & Validity gate & Reference $-$ blind & Reveal $-$ reference \\\\", "\\midrule"]
for name, key in (("Qwen2.5-7B", Q), ("phi-4", P)):
    d = mace3[key]
    for g, lab in (("k1", f"$k{{=}}1$ ({mace3['n_k1']})"), ("kgt1", f"$k{{>}}1$ ({mace3['n_kgt1']})"), ("all", f"all ({mace3['n_tasks']})")):
        x = d[g]
        body.append(f"{name if g == 'k1' else ''} & {lab} & {100 * x['acc_noref']:.1f} & {100 * x['acc_ref']:.1f} & {100 * x['acc_m1']:.1f} & {100 * x['acc_m2']:.1f} & {pp(x['ref_minus_blind'])} & {pp(x['m1_minus_ref'])} \\\\")
    body.append("\\addlinespace")
body[-1] = "\\bottomrule"
body += ["\\end{tabular}"]
write("mace_accuracy.tex", "\n".join(body) + "\n")
print("wrote round-3 tables")


# ---------------------------------------------------------------- round 4: exact estimator, bare-answer MATH-500, grading, Qwen3-14B
def au(v):
    return f"{v[0]:.2f} {{\\scriptsize$[{v[1][0]:.2f},{v[1][1]:.2f}]$}}"


def p4(v):
    return f"${_z(100 * v[0], 1):+.1f}$ {{\\scriptsize$[{_z(100 * v[1][0], 1):+.1f},{_z(100 * v[1][1], 1):+.1f}]$}}"


def done(body):
    return "\n".join(body + ["\\bottomrule", "\\end{tabular}"]) + "\n"


K14, GEM, MIS = "Qwen__Qwen2.5-14B-Instruct", "google__gemma-2-9b-it", "mistralai__Mistral-7B-Instruct-v0.3"
KN = [("Qwen2.5-7B", Q), ("Qwen2.5-14B", K14), ("gemma-2-9b", GEM), ("Mistral-7B", MIS)]
r4 = J("r4_results.json") if (A / "r4_results.json").exists() else {}
try:
    x = r4["rotation"]
    body = ["\\begin{tabular}{lccc}", "\\toprule", "Score used & Moved onto & Moved off & Matches neither \\\\", "\\midrule"]
    for key, lab in (("escore", "Exact expected score"), ("escore_legacy", "Original rule, rescored"), ("greedy", "Greedy integer")):
        body.append(f"{lab} & {fc(*x[key]['gainer'][:2])} & {fc(*x[key]['loser'][:2])} & {fc(*x[key]['placebo'][:2])} \\\\")
    write("r4_rotation.tex", done(body))
except (KeyError, TypeError) as e:
    print("[skip r4_rotation]", e)
try:
    ks = ["k1", "k2", "k4", "k8", "k16", "kgt1"]
    body = ["\\begin{tabular}{lcccccc}", "\\toprule",
            "Judge & $k{=}1$ & $k{=}2$ & $k{=}4$ & $k{=}8$ & $k{=}16$ & pooled $k{>}1$ \\\\", "\\midrule"]
    for name, key in KN:
        if key not in r4["kpool"]:
            continue
        e = r4["kpool"][key]["escore"]
        body.append(f"{name} & " + " & ".join(f"${_z(100 * e[k]['ref_minus_blind'][0], 1):+.1f}$" for k in ks) + " \\\\")
        body.append(" & " + " & ".join(f"{{\\scriptsize$[{_z(100 * e[k]['ref_minus_blind'][1][0], 0):+.0f},{_z(100 * e[k]['ref_minus_blind'][1][1], 0):+.0f}]$}}" for k in ks) + " \\\\")
    ra = r4["repl_accuracy"]
    body.append("\\midrule")
    body.append(f"\\multicolumn{{7}}{{l}}{{Replication pool, Qwen2.5-7B, 105 tasks: blind {100 * ra['acc_blind'][0]:.1f}\\%, reference {100 * ra['acc_ref'][0]:.1f}\\%, change {p4(ra['ref_minus_blind'])}}} \\\\")
    write("r4_kpool.tex", done(body))
except (KeyError, TypeError) as e:
    print("[skip r4_kpool]", e)
try:
    body = ["\\begin{tabular}{lcccccc}", "\\toprule",
            "Judge & Blind & Solution & Answer & Solution $-$ blind & Answer $-$ blind & Answer $-$ solution \\\\", "\\midrule"]
    for name, key in KN[:2]:
        if key not in r4.get("math", {}):
            continue
        d = r4["math"][key]
        body.append(f"{name} & {100 * d['acc_noref'][0]:.1f} & {100 * d['acc_ref'][0]:.1f} & {100 * d['acc_refans'][0]:.1f} & "
                    f"{p4(d['ref_minus_noref'])} & {p4(d['refans_minus_noref'])} & {p4(d['refans_minus_ref'])} \\\\")
    write("r4_math.tex", done(body))
except (KeyError, TypeError) as e:
    print("[skip r4_math]", e)
try:
    V, G = r4["verification_auroc"], r4["grading"]
    body = ["\\begin{tabular}{llccc}", "\\toprule", "Pool & Correct answers, against wrong ones & Blind & Reference & Change \\\\", "\\midrule"]
    for pool, plab in (("repl", "Replication"), ("mace", "\\textsc{MACE}")):
        if pool not in G:
            continue
        for key, lab in (("G_nm", "that differ from the reference"), ("G_m", "that match the reference"), ("G_all", "all correct answers")):
            g = G[pool][key]
            body.append(f"{plab if key == 'G_nm' else ''} & {lab} & {au(g['blind'])} & {au(g['ref'])} & {fc(*g['ref_minus_blind'][:2])} \\\\")
        body.append("\\addlinespace")
    body[-1] = "\\midrule"
    body.append("\\multicolumn{5}{l}{Blind verification AUROC: " + "; ".join(
        f"{lab} {au(V[p])}" for p, lab in (("repl", "replication"), ("kpool", "$k$-pool"), ("mace", "\\textsc{MACE}"), ("math", "MATH-500")) if V.get(p)) + "} \\\\")
    write("r4_grading.tex", done(body))
except (KeyError, TypeError) as e:
    print("[skip r4_grading]", e)
try:
    t4 = J("r4_toggle14b_results.json")

    def tget(model, arm, *path):
        d = t4.get(model, {}).get(arm, {})
        for k in path:
            d = d.get(k) if isinstance(d, dict) else None
        return d

    rows = [("Arithmetic (rotation)", "moved onto", ("rot", "gainer")), ("", "no longer matches", ("rot", "loser")),
            ("", "matches neither", ("rot", "placebo")),
            ("Arithmetic ($k$-subsample)", "margin, ref $-$ blind", ("ksub", "margin_diff_kgt1")),
            ("Factual (\\textsc{MACE} subsample)", "margin, ref $-$ blind", ("macesub", "margin_diff")),
            ("", "false rejections, ref $-$ blind", ("macesub", "false_reject_diff")),
            ("Blind verification AUROC", "arithmetic", ("verif_auroc_ksub",)), ("", "factual", ("verif_auroc_macesub",))]
    body = ["\\begin{tabular}{llcccc}", "\\toprule",
            "& & \\multicolumn{2}{c}{Qwen3-14B} & \\multicolumn{2}{c}{Qwen3-8B} \\\\", "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}",
            "Task type & Readout & Off & On & Off & On \\\\", "\\midrule"]
    for a, b, path in rows:
        cells = []
        for model in ("Qwen3-14B", "Qwen3-8B_posthoc"):
            for arm in ("off", "on"):
                v = tget(model, arm, *path)
                if v is None:
                    cells.append("---")
                elif path[-1] == "false_reject_diff":
                    cells.append(p4(v))
                elif path[0].startswith("verif"):
                    cells.append(au(v))
                else:
                    cells.append(fc(*v[:2]))
        body.append(f"{a} & {b} & " + " & ".join(cells) + " \\\\")
    write("r4_toggle.tex", done(body))
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip r4_toggle]", e)
try:
    ph = J("r4_posthoc_results.json")
    body = ["\\begin{tabular}{llcccc}", "\\toprule", "Judge & Tasks & Blind & Reference & Blind, then reveal & Reference $-$ blind \\\\", "\\midrule"]
    for name, key in (("Qwen2.5-7B", Q), ("phi-4", P)):
        for k in ("k1", "k2", "k4", "k6"):
            x = ph["mace_by_k"][key][k]
            body.append(f"{name if k == 'k1' else ''} & $k{{=}}{k[1:]}$ ({x['n']}) & {100 * x['acc_noref']:.1f} & {100 * x['acc_ref']:.1f} & {100 * x['acc_m1']:.1f} & {p4(x['ref_minus_blind'])} \\\\")
        body.append("\\addlinespace")
    body[-1] = "\\midrule"
    body = body[:-1]
    write("mace_by_k.tex", done(body))
    body = ["\\begin{tabular}{llccc}", "\\toprule", "Judge & Pool & Blind & Reference & Blind, then reveal \\\\", "\\midrule"]
    for name, key in (("Qwen2.5-7B", Q), ("phi-4", P), ("Qwen2.5-14B", K14)):
        d = ph["regret"][key]
        first = True
        for pool, lab in (("kpool_kgt1", "$k$-pool, $k{>}1$"), ("math500", "MATH-500"), ("mace", "\\textsc{MACE}")):
            if pool in d["regret"]:
                r = d["regret"][pool]
                body.append(f"{name if first else ''} & {lab} & " + " & ".join(f"${_z(100 * r[c_], 1):+.1f}$" for c_ in ("blind", "ref", "reveal")) + " \\\\")
                first = False
        w = d["worst_case"]
        body.append(" & \\emph{worst case} & " + " & ".join(f"$\\mathbf{{{_z(100 * w[c_], 1):+.1f}}}$" for c_ in ("blind", "ref", "reveal")) + " \\\\")
        body.append("\\addlinespace")
    body = body[:-1]
    write("regret.tex", done(body))
except (KeyError, TypeError) as e:
    print("[skip posthoc tables]", e)
print("wrote round-4 tables")
