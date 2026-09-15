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


STACKED = {"r4_toggle.tex", "score_rules.tex", "protocol_grading.tex", "protocol_selection.tex", "coverage.tex", "acc_variants.tex", "kpool.tex", "dpo.tex"}
_CELL = __import__("re").compile(r"((?:\$[^$&\\]*\$)|(?:[-+]?\d+(?:\.\d+)?))\s+(\{\\scriptsize\$\[[^\]]*\]\$\})")


def write(name, body):
    # Tables that were printing at about 5 pt after shrink-to-fit: put each interval under its value so they fit at full size.
    if name in STACKED:
        body = _CELL.sub(lambda m: "\\begin{tabular}[c]{@{}c@{}}" + m.group(1) + "\\\\" + m.group(2) + "\\end{tabular}", body)
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
body.append(f"\\quad blind-accepted only & $a$ & {fc(r['gainers']['mean'], r['gainers']['ci'])} & "
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
    body.append(" & margin & " +
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
        "Judge & Distinct score values & Blind ties at max (of 64) & Blind selection accuracy & Margin \\\\", "\\midrule"]
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
        f"Replication pool: margin & {fc(p2['repl_margin__' + g]['margin'], p2['repl_margin__' + g]['ci'])} & --- \\\\",
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
        "Run & Arm & Own-judge gain (gate) & Score--accuracy gap (points) & Held-out accuracy change \\\\", "\\midrule",
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
body.append(f"Arithmetic (swap) & moved onto & {fc(tog['off']['rot']['gainer'][0], tog['off']['rot']['gainer'][1], 3)} & {fc(tog['on']['rot']['gainer'][0], tog['on']['rot']['gainer'][1], 3)} & {diag['rot|off|ref']['tokens_mean']} / {diag['rot|on|ref']['tokens_mean']} \\\\")
body.append(f" & moved off & {fc(tog['off']['rot']['loser'][0], tog['off']['rot']['loser'][1], 3)} & {fc(tog['on']['rot']['loser'][0], tog['on']['rot']['loser'][1], 3)} & \\\\")
body.append(f" & matches neither & {fc(tog['off']['rot']['placebo'][0], tog['off']['rot']['placebo'][1], 3)} & {fc(tog['on']['rot']['placebo'][0], tog['on']['rot']['placebo'][1], 3)} & \\\\")
body.append(f"Arithmetic ($k$-subsample) & added margin & {fc(*tog['off']['ksub']['margin_diff_kgt1'][:2])} & {fc(*tog['on']['ksub']['margin_diff_kgt1'][:2])} & {diag['ksub|off|ref']['tokens_mean']} / {diag['ksub|on|ref']['tokens_mean']} \\\\")
body.append(f"Factual (MACE subsample) & added margin & {fc(*tog['off']['macesub']['margin_diff'][:2])} & {fc(*tog['on']['macesub']['margin_diff'][:2])} & {diag['macesub|off|ref']['tokens_mean']} / {diag['macesub|on|ref']['tokens_mean']} \\\\")
body.append(f" & false rejections, ref $-$ blind & {pp(tog['off']['macesub']['false_reject_diff'])} & {pp(tog['on']['macesub']['false_reject_diff'])} & \\\\")
body += ["\\bottomrule", "\\end{tabular}"]
write("toggle.tex", "\n".join(body) + "\n")

mace3 = J("r3_mace_accuracy_results.json")
body = ["\\begin{tabular}{llcccccc}", "\\toprule",
        "Judge & Tasks & Blind & Reference & Blind, then reveal & Validity gate & Reference $-$ blind & Reveal $-$ reference \\\\", "\\midrule"]
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


def stk(top, bottom):  # value above its interval in one cell
    return f"\\begin{{tabular}}[c]{{@{{}}c@{{}}}}{top}\\\\{bottom}\\end{{tabular}}"


def fs(v, d=2):
    return stk(f(v[0], d), c(v[1][0], v[1][1], d))


def p4s(v):
    return stk(f"${_z(100 * v[0], 1):+.1f}$", f"{{\\scriptsize$[{_z(100 * v[1][0], 1):+.1f},{_z(100 * v[1][1], 1):+.1f}]$}}")


K14, GEM, MIS = "Qwen__Qwen2.5-14B-Instruct", "google__gemma-2-9b-it", "mistralai__Mistral-7B-Instruct-v0.3"
KN = [("Qwen2.5-7B", Q), ("Qwen2.5-14B", K14), ("gemma-2-9b", GEM), ("Mistral-7B", MIS)]
r4 = J("r4_results.json") if (A / "r4_results.json").exists() else {}
try:
    x = r4["rotation"]
    body = ["\\begin{tabular}{lccc}", "\\toprule", "Score used & Moved onto & Moved off & Matches neither \\\\", "\\midrule"]
    for key, lab in (("escore", "Exact scorer"), ("escore_legacy", "Original scorer, rescored"), ("greedy", "Greedy integer")):
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
            body.append(f"{plab + ', Qwen2.5-7B' if key == 'G_nm' else ''} & {lab} ({g['ref_minus_blind'][2]} tasks) & {au(g['blind'])} & {au(g['ref'])} & {fc(*g['ref_minus_blind'][:2])} \\\\")
        body.append("\\addlinespace")
    r4p_ = J("r4_posthoc_results.json").get("grading_other_judges", {}).get("microsoft__phi-4", {})
    for pool, plab in (("repl", "Replication"), ("mace", "\\textsc{MACE}")):
        gg = r4p_.get(f"grading_{pool}")
        if not gg:
            continue
        for key, lab in (("G_nm", "that differ from the reference"), ("G_all", "all correct answers")):
            g = gg[key]
            body.append(f"{plab + ', phi-4' if key == 'G_nm' else ''} & {lab} ({g['ref_minus_blind'][2]} tasks) & {au(g['blind'])} & {au(g['ref'])} & {fc(*g['ref_minus_blind'][:2])} \\\\")
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

    rows = [("Arithmetic (swap)", "moved onto", ("rot", "gainer")), ("", "moved off", ("rot", "loser")),
            ("", "matches neither", ("rot", "placebo")),
            ("Arithmetic ($k$-subsample)", "added margin", ("ksub", "margin_diff_kgt1")),
            ("Factual (\\textsc{MACE} subsample)", "added margin", ("macesub", "margin_diff")),
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


# ---------------------------------------------------------------- round 5: numbers quoted in the main text
try:
    r5p, r4p = J("r5_posthoc_results.json"), J("r4_posthoc_results.json")
    HDR = "Quantity & Value (95\\% CI) \\\\"
    body = ["\\begin{longtable}{L{8.2cm}L{5.0cm}}",
            "\\caption{Numbers quoted in the main text that are not in other tables, grouped by topic. Exact scorer for Qwen2.5-7B unless stated; phi-4 uses the original scorer, which is exact for its tokenizer. Post hoc unless the main text marks them otherwise.}\\label{tab:main-numbers} \\\\",
            "\\toprule", HDR, "\\midrule", "\\endfirsthead",
            "\\multicolumn{2}{l}{\\small\\emph{\\cref{tab:main-numbers}, continued}} \\\\", "\\toprule", HDR, "\\midrule", "\\endhead",
            "\\bottomrule", "\\endfoot"]
    sec = lambda t: body.append(f"\\multicolumn{{2}}{{L{{13.2cm}}}}{{\\emph{{{t}}}}} \\\\")
    sec("Swap, Qwen2.5-7B, exact scorer, correct answers scored at least $t$ blind")
    for key, lab in (("gainer_ge7", "Moved onto, $t=7$"), ("gainer_ge9", "Moved onto, $t=9$"), ("loser_ge7", "Moved off, $t=7$"), ("loser_ge9", "Moved off, $t=9$")):
        v = r5p["blind_accepted"][key]
        body.append(f"{lab} & {fc(*v['change'][:2])} ({100 * v['share_kept']:.0f}\\% kept) \\\\")
    sec("False rejections of correct non-matching answers, replication pool, Qwen2.5-7B, exact scorer")
    fr = r4["repl_false_reject"]
    for key, lab in (("le3", "Scored 3 or below"), ("posthoc_le5", "Scored 5 or below (post hoc)")):
        x = fr[key]
        body.append(f"{lab}: blind {100 * x['blind'][0]:.1f}\\%, reference {100 * x['ref'][0]:.1f}\\% & change {p4(x['diff'])} \\\\")
    sec("\\textup{\\textsc{MACE}}, Qwen2.5-7B exact scorer; phi-4 original scorer")
    mq = r4p["mace_exact_q7"]
    for k_, lab in (("k1", "$k{=}1$"), ("kgt1", "$k{>}1$"), ("all", "all")):
        body.append(f"Selection accuracy change, Qwen2.5-7B, {lab} ({mq[k_]['n']} tasks) & {p4(mq[k_]['ref_minus_blind'])} \\\\")
    for jn in ("Qwen2.5-7B", "phi-4"):
        for k_, lab in (("k1", "$k{=}1$"), ("kgt1", "$k{>}1$")):
            g = r5p["mace_grading_by_k"][jn][k_]["G_all"]["ref_minus_blind"]
            body.append(f"Overall AUROC change, {jn}, {lab} & {fc(*g[:2])} \\\\")
    sec("Split-half Spearman $\\rho$ between blind AUROC and the reference's change in AUROC (split 0; mean over 20 splits)")
    for jn in ("Qwen2.5-7B", "phi-4"):
        for pool, lab in (("repl", "replication"), ("kpool", "$k$-pool"), ("mace", "\\textsc{MACE}"), ("mace_kgt1", "\\textsc{MACE}, $k{>}1$"), ("pooled", "all three pools")):
            x = r5p["split_half"][jn][pool]
            body.append(f"{jn}, {lab} ({x['n_tasks']} tasks) & ${_z(x['rho_split0'], 2):+.2f}$ {c(*x['rho_split0_ci'])}; mean ${_z(x['rho_mean_20'], 2):+.2f}$ \\\\")
    sec("$k$-pool selection accuracy change (points): $k{=}1$, $k{>}1$, and the step between them")
    for jn, v in r5p["kpool_step"].items():
        st = v["step"]
        body.append(f"{jn} & ${_z(100 * v['k1'][0], 1):+.1f}$, ${_z(100 * v['kgt1'][0], 1):+.1f}$; step ${_z(100 * st[0], 1):+.1f}$ {{\\scriptsize$[{_z(100 * st[1][0], 1):+.1f},{_z(100 * st[1][1], 1):+.1f}]$}} \\\\")
    r6 = J("r6_posthoc_results.json")
    sec("What best-of-64 picks on the $k$-pool: correct / wrong containing the reference's answer text / other wrong (\\%, blind $\\to$ reference)")
    for jn in ("Qwen2.5-7B", "phi-4", "Qwen2.5-14B", "gemma-2-9b", "Mistral-7B"):
        for k_, lab in (("k1", "$k{=}1$"), ("kgt1", "$k{>}1$")):
            pk = r6["picks"][jn][k_]
            trip = lambda c_: "/".join(f"{100 * pk[c_][x][0]:.0f}" for x in ("correct", "lure", "other_wrong"))
            body.append(f"{jn}, {lab} ({pk['n_tasks']} tasks) & {trip('noref')} $\\to$ {trip('ref')} \\\\")
    sec("$k$-pool overall AUROC change with the reference, $k{=}1$ and $k{>}1$")
    for jn in ("Qwen2.5-7B", "phi-4", "Qwen2.5-14B", "gemma-2-9b", "Mistral-7B"):
        a_ = r6["kpool_overall_auroc"][jn]
        body.append(f"{jn} & {fc(*a_['k1']['ref_minus_blind'][:2])}; {fc(*a_['kgt1']['ref_minus_blind'][:2])} \\\\")
    sec("Power to separate blind AUROC on the replication pool from \\textup{\\textsc{MACE}} (Qwen2.5-7B; share of 400 draws)")
    pw = r5p["power_rep_vs_mace"]
    for m_ in (16, 64):
        body.append(f"{m_} candidates per task: 10, 20, 40 tasks & {pw[f'm{m_}_n10']:.2f}, {pw[f'm{m_}_n20']:.2f}, {pw[f'm{m_}_n40']:.2f} \\\\")
    r12 = J("r12_checks.json")
    sec("Best-of-64 accuracy change by whether a correct candidate matches the reference (any-format labels, points; exact scorer for Qwen2.5)")
    for key, lab in (("kpool|Qwen2.5-7B", "$k$-pool, $k{>}1$, Qwen2.5-7B"), ("kpool|phi-4", "$k$-pool, $k{>}1$, phi-4"),
                     ("kpool|Qwen2.5-14B", "$k$-pool, $k{>}1$, Qwen2.5-14B"), ("kpool|gemma-2-9b", "$k$-pool, $k{>}1$, gemma-2-9b"),
                     ("repl|Qwen2.5-7B", "Replication, Qwen2.5-7B"), ("repl|phi-4", "Replication, phi-4")):
        x = r12["selection_by_match_presence"][key]
        w_, wo = x["matching_correct_present"], x["no_matching_correct"]
        body.append(f"{lab}: with a matching correct candidate ({w_[2]} tasks); without one ({wo[2]} tasks) & {p4(w_)}; {p4(wo)} \\\\")
    s9 = J("r9_sonnet_item_level.json")
    sec("Sonnet~5 (API), correct answers that differ from the reference and were scored 7 or above blind")
    for pool, lab in (("mace", "\\textsc{MACE}, $k{>}1$"), ("repl", "Replication"), ("kpool", "$k$-pool, $k{>}1$")):
        a_, b_ = s9[pool], r12["sonnet_blind_ten"][pool]
        sh = a_["share_scored_le3_with_reference"]
        body.append(f"{lab}: tasks with such answers; answers; share scored 3 or below with the reference & {a_['tasks']}; {a_['answers']}; {100 * sh[0]:.1f}\\% {c(100 * sh[1][0], 100 * sh[1][1], 1)} \\\\")
        body.append(f"{lab}: answers scored 10 blind; share of them scored 3 or below with the reference & {b_['scored_10_blind']}; {100 * b_['share_of_10s_scored_le3_with_reference']:.1f}\\% \\\\")
    r15 = J("r15_checks.json")
    sec("Sonnet~5 (API), correct answers scored 10 blind: share scored 3 or below with the reference, differing from it against matching it")
    for pool, lab in (("mace", "\\textsc{MACE}, $k{>}1$"), ("repl", "Replication"), ("kpool", "$k$-pool, $k{>}1$")):
        nm_, m_ = r15[pool]["nonmatch"], r15[pool]["match"]
        body.append(f"{lab} & {100 * nm_['share_of_10s_scored_le3_with_reference']:.1f}\\% of {nm_['scored_10_blind']}; {100 * m_['share_of_10s_scored_le3_with_reference']:.1f}\\% of {m_['scored_10_blind']} \\\\")
    # the command-line noise floor (r16d) was superseded by the same-interface second blind call (R20-A, tables/r20_retest.tex)
    wt = J("r19_sonnet_wrong_tens.json")
    sec("Sonnet~5 (API) subsamples: share of wrong and correct answers scored 10 blind")
    for pool, lab in (("mace", "\\textsc{MACE}, $k{>}1$"), ("repl", "Replication"), ("kpool", "$k$-pool, $k{>}1$")):
        w_, c_ = wt[pool]["wrong"], wt[pool]["correct"]
        body.append(f"{lab}: wrong answers; correct answers & {100 * w_['share_blind_10']:.1f}\\% of {w_['n']}; {100 * c_['share_blind_10']:.1f}\\% of {c_['n']} \\\\")
    write("main_numbers.tex", "\n".join(body + ["\\end{longtable}"]) + "\n")
    print("wrote main_numbers.tex")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip main_numbers]", e)


# ---------------------------------------------------------------- round 7: false rejections by judge and task type; robustness numbers
def pp1(v):
    return "---" if v is None else f"${_z(100 * v[0], 1):+.1f}$ {{\\scriptsize$[{_z(100 * v[1][0], 1):+.1f},{_z(100 * v[1][1], 1):+.1f}]$}}"


try:
    r7, r7b = J("r7_posthoc_results.json"), J("r7b_posthoc_results.json")
    acc_ = J("accuracy_readouts.json")
    tog3, t14_, r5s_ = J("r3_toggle_results.json"), J("r4_toggle14b_results.json"), J("r5_sonnet_mace_results.json")
    fr7 = r7["false_reject_change"]
    s5 = acc_["repl_sonnet5_false_reject"]
    s5_arith = f"${_z(100 * (s5['ref_nonmatch'][0] - s5['blind_nonmatch'][0]), 1):+.1f}$"
    body = ["\\begin{tabular}{lcccc}", "\\toprule",
            " & \\multicolumn{2}{c}{Arithmetic} & \\multicolumn{2}{c}{Factual (\\textsc{MACE})} \\\\", "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}",
            "Judge & No thinking & Thinking & No thinking & Thinking \\\\", "\\midrule",
            f"Qwen2.5-7B & {pp1(r4['repl_false_reject']['le3']['diff'])} & --- & {pp1(fr7['Qwen2.5-7B|factual|score'])} & --- \\\\",
            f"phi-4 & {pp1(acc_['repl'][P]['false_reject_diff_nonmatch'])} & --- & {pp1(fr7['phi-4|factual|score'])} & --- \\\\",
            f"Qwen3-8B & {pp1(fr7['Qwen3-8B|arithmetic|thinking off'])} & {pp1(fr7['Qwen3-8B|arithmetic|thinking on'])} & {pp1(tog3['off']['macesub']['false_reject_diff'])} & {pp1(tog3['on']['macesub']['false_reject_diff'])} \\\\",
            f"Qwen3-14B & {pp1(fr7['Qwen3-14B|arithmetic|thinking off'])} & {pp1(fr7['Qwen3-14B|arithmetic|thinking on'])} & {pp1(t14_['Qwen3-14B']['off']['macesub']['false_reject_diff'])} & {pp1(t14_['Qwen3-14B']['on']['macesub']['false_reject_diff'])} \\\\",
            f"Sonnet~5 & {s5_arith} & --- & {pp1(r5s_['fast']['false_reject_diff'])} & {pp1(r5s_['think']['false_reject_diff'])} \\\\"]
    write("false_reject.tex", done(body))

    body = ["\\begin{tabular}{L{8.4cm}L{4.8cm}}", "\\toprule", "Quantity & Value (95\\% CI) \\\\", "\\midrule"]
    sec = lambda t: body.append(f"\\multicolumn{{2}}{{l}}{{\\emph{{{t}}}}} \\\\")
    sec("Wrong candidates whose text contains the reference's answer (look-alikes)")
    for pool, lab in (("replication", "Replication pool"), ("kpool", "$k$-pool")):
        x = r7b["lure_character"][pool]
        body.append(f"{lab}: share of wrong candidates; share of those with no \\texttt{{\\textbackslash boxed\\{{\\}}}} answer & {100 * x['lure_share_of_wrong']:.1f}\\%; {100 * x['lure_no_box'] / x['lure']:.1f}\\% \\\\")
    body.append(f"\\textsc{{MACE}} River and Language: share of wrong candidates & {100 * r7b['mace_lures']['lure_share_of_wrong']:.1f}\\% \\\\")
    sec("$k$-pool accuracy change with look-alikes removed (points): $k{=}1$; $k{>}1$; step")
    for jn, v in r7["lures_removed"].items():
        st = v["step_lures_removed"]
        body.append(f"{jn} & {pp1(v['k1']['lures_removed'])}; {pp1(v['kgt1']['lures_removed'])}; step ${_z(100 * st[0], 1):+.1f}$ {{\\scriptsize$[{_z(100 * st[1][0], 1):+.1f},{_z(100 * st[1][1], 1):+.1f}]$}} \\\\")
    sec("Replication pool with look-alikes removed: AUROC change (non-matching, all); accuracy change (points)")
    for jn, v in r7b["replication_lures_removed"].items():
        body.append(f"{jn} & {fc(*v['G_nm_change'][:2])}, {fc(*v['G_all_change'][:2])}; {pp1(v['accuracy_change'])} \\\\")
    body.append(f"\\textsc{{MACE}}, Qwen2.5-7B, non-matching AUROC change with look-alikes removed & {fc(*r7b['mace_lures']['G_nm_change_lures_removed_qwen'][:2])} \\\\")
    sec("GPT-4.1 on the $k$-pool: accuracy change (points) and mean candidates tied at the maximum, blind / reference")
    g4 = r7["gpt41_kpool_accuracy"]
    for k_, lab in (("k1", "$k{=}1$"), ("kgt1", "$k{>}1$")):
        body.append(f"GPT-4.1, {lab} & {pp1(g4[k_]['ref_minus_blind'])}; ties {g4[k_]['mean_tied_at_max_blind']} / {g4[k_]['mean_tied_at_max_ref']} \\\\")
    cov_ = r7["frontier_coverage"]["sonnet_repl"]
    body.append(f"Sonnet~5 score files, replication pool: correct answers scored; wrong answers scored & {cov_['correct_scored']} of {cov_['correct_total']}; {cov_['wrong_scored']} of {cov_['wrong_total']} \\\\")
    sec("Sonnet~5 (API) mean score of correct answers, replication pool, blind $\\to$ reference")
    ss = acc_["repl_sonnet5_scores"]
    for key, lab in (("match", "Matching the reference"), ("nonmatch", "Differing from the reference")):
        b_, r_ = ss["noref"][key], ss["ref"][key]
        body.append(f"{lab} & {b_[0]:.2f} {c(*b_[1])} $\\to$ {r_[0]:.2f} {c(*r_[1])} \\\\")
    write("round7_numbers.tex", done(body))

    rules = [("reference", "Reference"), ("mean", "Mean"), ("min", "Min"), ("max", "Max"), ("blind_then_ref_tiebreak", "Blind, reference breaks ties"), ("blind_then_reveal", "Blind, then reveal")]
    cols = [("kpool_kgt1", "Qwen2.5-7B", "$k$-pool, 7B"), ("kpool_kgt1", "phi-4", "$k$-pool, phi-4"), ("kpool_kgt1", "Qwen2.5-14B", "$k$-pool, 14B"),
            ("kpool_kgt1", "gemma-2-9b", "$k$-pool, gemma"), ("mace_all", "Qwen2.5-7B", "\\textsc{MACE}, 7B"), ("mace_all", "phi-4", "\\textsc{MACE}, phi-4"),
            ("math", "Qwen2.5-7B", "MATH, 7B"), ("math", "Qwen2.5-14B", "MATH, 14B")]
    body = ["\\begin{tabular}{l" + "c" * len(cols) + "}", "\\toprule", "Rule & " + " & ".join(cl for _, _, cl in cols) + " \\\\", "\\midrule"]
    for key, lab in rules:
        cells = []
        for pool, jn, _ in cols:
            v = (r7b["math_rules"].get(jn, {}) if pool == "math" else r7["score_rules"].get(pool, {}).get(jn, {})).get(key)
            cells.append("---" if v is None else f"${_z(100 * v[0], 1):+.1f}$")
        body.append(f"{lab} & " + " & ".join(cells) + " \\\\")
    write("score_rules.tex", done(body))
    print("wrote round-7 tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-7 tables]", repr(e))


# ---------------------------------------------------------------- round 8: labelings, Sonnet 5 with wrong answers, Table 1 with per-cell labels
def au2(v):
    return "---" if v is None else fc(*v[:2])


def lvl(v):
    return "---" if v is None else f"{v[0]:.2f} {{\\scriptsize$[{v[1][0]:.2f},{v[1][1]:.2f}]$}}"


try:
    L8 = J("r8_lenient_results.json")
    lab8 = J("r8_lenient_labels.json")
    HOWL = [("strict", "Registered"), ("lenient", "Any format"), ("model", "Model-read"), ("boxed_only", "Boxed only")]
    POOLJ = [("repl|all", "Replication", ["Qwen2.5-7B", "phi-4", "GPT-4.1"]),
             ("kpool|k1", "$k$-pool, $k{=}1$", ["Qwen2.5-7B", "Qwen2.5-14B", "gemma-2-9b", "phi-4", "Mistral-7B", "GPT-4.1"]),
             ("kpool|kgt1", "$k$-pool, $k{>}1$", ["Qwen2.5-7B", "Qwen2.5-14B", "gemma-2-9b", "phi-4", "Mistral-7B", "GPT-4.1"])]
    for key, fname, fmt, pools in (("acc", "labelings_acc.tex", pp1, POOLJ), ("G_nm", "labelings_gnm.tex", au2, [POOLJ[0], POOLJ[2]]),
                                   ("FR", "labelings_fr.tex", pp1, [POOLJ[0], POOLJ[2]])):
        body = ["\\begin{tabular}{ll" + "c" * len(HOWL) + "}", "\\toprule", "Pool & Judge & " + " & ".join(h for _, h in HOWL) + " \\\\", "\\midrule"]
        for pool, plab, js in pools:
            for i, jn in enumerate(js):
                d = L8["pools"].get(pool, {}).get(jn, {})
                body.append(f"{plab if i == 0 else ''} & {jn} & " + " & ".join(fmt(d.get(h, {}).get(key)) for h, _ in HOWL) + " \\\\")
            body.append("\\addlinespace")
        write(fname, done(body[:-1]))
    body = ["\\begin{tabular}{L{7.6cm}L{5.4cm}}", "\\toprule", "Quantity & Value \\\\", "\\midrule"]
    for pool, plab in (("repl", "Replication pool"), ("kpool", "$k$-pool")):
        x = lab8[pool]
        body.append(f"{plab}: samples; with a \\texttt{{\\textbackslash boxed\\{{\\}}}} answer & {x['samples']}; {x['boxed']} ({100 * x['boxed'] / x['samples']:.1f}\\%) \\\\")
        body.append(f"{plab}: correct under the registered checker; in any format & {x['strict_correct']}; {x['lenient_correct']} "
                    f"(+{x['flip_to_correct_unboxed']} unboxed, +{x['flip_to_correct_boxed']} boxed) \\\\")
    for pool, plab in (("repl", "Replication pool"), ("kpool", "$k$-pool")):
        a_ = L8["rule_vs_model_agreement_unboxed"].get(pool)
        if a_:
            body.append(f"{plab}, unboxed replies: rule and model labels agree; correct by rule / by model & {100 * a_['agreement']:.1f}\\%; {a_['rule_correct']} / {a_['model_correct']} \\\\")
    for jn, hows in L8["rules_kpool_kgt1"].items():
        v = hows.get("lenient", {})
        body.append(f"$k$-pool, $k{{>}}1$, any format, {jn}: accuracy change for reference; max rule; blind, then reveal (points) & "
                    f"{pp1(v.get('reference'))}; {pp1(v.get('max'))}; {pp1(v.get('blind_then_reveal'))} \\\\")
    write("labelings_numbers.tex", done(body))
    print("wrote round-8 labeling tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-8 labeling tables]", repr(e))

try:
    ir, ik = J("r9_inflation_relabeled.json"), J("r9_inflation_relabeled_kpool.json")
    LABS = [("strict", "Registered"), ("lenient", "Any format"), ("model", "Model-read")]
    body = ["\\begin{tabular}{ll" + "c" * len(LABS) + "}", "\\toprule", "Endpoint & Judge & " + " & ".join(l_ for _, l_ in LABS) + " \\\\", "\\midrule"]
    cell = lambda x: fc(x["delta"], x["ci"])
    for jn, key in (("Qwen2.5-7B", Q), ("phi-4", P), ("Pooled", "pooled")):
        body.append(f"{'Replication, 105 tasks' if jn == 'Qwen2.5-7B' else ''} & {jn} & " + " & ".join(cell(ir[f'registered_band|{h}'][key]) for h, _ in LABS) + " \\\\")
    body.append(" & Pooled, band recomputed & --- & " + " & ".join(cell(ir[f'band_under_labeling|{h}']['pooled']) for h in ("lenient", "model")) + " \\\\")
    body.append("\\addlinespace")
    for cond, clab in (("ref", "reference"), ("m1", "blind, then reveal")):
        for kname, klab in (("k1", "$k{=}1$"), ("kgt1", "$k{>}1$")):
            for jn, key in (("Qwen2.5-7B", Q), ("phi-4", P)):
                first = jn == "Qwen2.5-7B"
                body.append(f"{f'$k$-pool, {clab}, {klab}' if first else ''} & {jn} & " + " & ".join(cell(ik[f'{h}|{key}|{cond}|{kname}']) for h, _ in LABS) + " \\\\")
    write("inflation_relabeled.tex", done(body))
    print("wrote inflation_relabeled.tex")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip inflation_relabeled]", repr(e))

try:
    S8 = J("r8_sonnet_results.json")
    cols = [("repl", "lenient", "Replication"), ("repl", "strict", "Repl., registered"), ("mace", "oracle", "\\textsc{MACE}, $k{>}1$"),
            ("kpool", "lenient", "$k$-pool, $k{>}1$")]
    have = [(p_, h, l_) for p_, h, l_ in cols if isinstance(S8["pools"].get(p_), dict) and h in S8["pools"][p_] and not S8["pools"][p_][h].get("status")]
    if have:
        body = ["\\begin{tabular}{l" + "c" * len(have) + "}", "\\toprule", "Readout & " + " & ".join(l_ for _, _, l_ in have) + " \\\\", "\\midrule"]
        g = lambda p_, h, k: S8["pools"][p_][h].get(k)
        rowsS = [("Tasks with all 32 calls scored", lambda p_, h: str(g(p_, h, "tasks_all_calls_scored"))),
                 ("AUROC, non-matching vs.\\ wrong: blind", lambda p_, h: lvl(g(p_, h, "G_nm_blind"))),
                 ("\\quad with the reference", lambda p_, h: lvl(g(p_, h, "G_nm_ref"))),
                 ("\\quad change", lambda p_, h: au2(g(p_, h, "G_nm"))),
                 ("AUROC, all correct vs.\\ wrong: change", lambda p_, h: au2(g(p_, h, "G_all"))),
                 ("False rejections, change (points)", lambda p_, h: pp1(g(p_, h, "FR"))),
                 ("Margin, change (points of 10)", lambda p_, h: au2(g(p_, h, "margin"))),
                 ("Best-of-16 accuracy, change (points)", lambda p_, h: pp1(g(p_, h, "acc"))),
                 ("Max rule accuracy, change (points)", lambda p_, h: pp1(g(p_, h, "acc_max_rule")))]
        for lab_, fn in rowsS:
            body.append(f"{lab_} & " + " & ".join(fn(p_, h) for p_, h, _ in have) + " \\\\")
        write("sonnet_r8.tex", done(body))
        print("wrote sonnet_r8.tex")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip sonnet_r8]", repr(e))

try:
    r7, acc_, r4 = J("r7_posthoc_results.json"), J("accuracy_readouts.json"), J("r4_results.json")
    tog3, t14_, r5s_ = J("r3_toggle_results.json"), J("r4_toggle14b_results.json"), J("r5_sonnet_mace_results.json")
    try:
        S8 = J("r8_sonnet_results.json")
    except FileNotFoundError:
        S8 = None
    fr7 = r7["false_reject_change"]
    s8fr = None
    if S8 and isinstance(S8["pools"].get("repl"), dict) and not S8["pools"]["repl"]["lenient"].get("status"):
        s8fr = S8["pools"]["repl"]["lenient"]["FR"]
    s8mace = None
    if S8 and isinstance(S8["pools"].get("mace"), dict) and not S8["pools"]["mace"]["oracle"].get("status"):
        s8mace = S8["pools"]["mace"]["oracle"]["FR"]
    PRE, PH = "\\pre", "\\ph"
    cell = lambda v, t: "---" if v is None else pp1(v) + t
    NA, NR = "n/a", "not run"
    T1 = [("Qwen2.5-7B", (r4["repl_false_reject"]["le3"]["diff"], PRE, "replication, exact scorer"), (None, NA),
           (fr7["Qwen2.5-7B|factual|score"], PH, "\\textsc{MACE} $k{>}1$, exact scorer"), (None, NA)),
          ("phi-4", (acc_["repl"][P]["false_reject_diff_nonmatch"], PH, "replication"), (None, NA),
           (fr7["phi-4|factual|score"], PH, "\\textsc{MACE} $k{>}1$"), (None, NA)),
          ("Qwen3-8B", (fr7["Qwen3-8B|arithmetic|thinking off"], PH, "swap subsample"), (fr7["Qwen3-8B|arithmetic|thinking on"], PH, "swap subsample"),
           (tog3["off"]["macesub"]["false_reject_diff"], PRE, "MACE subsample, thinking toggle"), (tog3["on"]["macesub"]["false_reject_diff"], PRE, "MACE subsample, thinking toggle")),
          ("Qwen3-14B", (fr7["Qwen3-14B|arithmetic|thinking off"], PH, "swap subsample"), (fr7["Qwen3-14B|arithmetic|thinking on"], PH, "swap subsample"),
           (t14_["Qwen3-14B"]["off"]["macesub"]["false_reject_diff"], PRE, "MACE subsample, thinking toggle"), (t14_["Qwen3-14B"]["on"]["macesub"]["false_reject_diff"], PRE, "MACE subsample, thinking toggle")),
          ("Sonnet~5, API", (s8fr, PRE, "replication subsamples with wrong answers, any-format labels, API"), (None, NR),
           (s8mace, PRE, "MACE subsamples with wrong answers, API"), (None, NR)),
          ("Sonnet~5, CLI", (None, NR), (None, NR),
           (r5s_["fast"]["false_reject_diff"], PRE, "MACE, one answer of each kind, CLI"), (r5s_["think"]["false_reject_diff"], PRE, "MACE, one answer of each kind, CLI"))]
    body = ["\\begin{tabular}{lcccc}", "\\toprule",
            " & \\multicolumn{2}{c}{Arithmetic (constructed)} & \\multicolumn{2}{c}{Factual (\\textsc{MACE})} \\\\", "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}",
            "Judge & Thinking off & Thinking on & Thinking off & Thinking on \\\\", "\\midrule"]
    src = ["\\begin{tabular}{llL{6.2cm}}", "\\toprule", "Judge & Cell & Value (95\\% CI), source \\\\", "\\midrule"]
    names = ["arithmetic, thinking off", "arithmetic, thinking on", "factual, thinking off", "factual, thinking on"]
    for jn, *cells in T1:
        out = []
        for nm_, c_ in zip(names, cells):
            if c_[0] is None:
                out.append(c_[1] if len(c_) == 2 else "\\pending{pending}")
                if len(c_) == 3:
                    src.append(f"{jn} & {nm_} & pending \\\\")
                continue
            out.append(cell(c_[0], c_[1]))
            src.append(f"{jn} & {nm_} & {pp1(c_[0])}; {c_[2]}{'' if len(c_[0]) < 3 else f' ({c_[0][2]} tasks)'} \\\\")
        body.append(f"{jn} & " + " & ".join(out) + " \\\\")
    write("false_reject.tex", done(body))
    write("false_reject_sources.tex", done(src))
    print("wrote Table 1 and sources")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip Table 1 round 8]", repr(e))


# ---------------------------------------------------------------- round 16: how the protocols grade, and selection intervals
try:
    pg = J("r16_protocol_grading.json")
    body = ["\\begin{tabular}{llccc}", "\\toprule", "Pool & Judge & Reference & Max rule & Blind, then reveal \\\\", "\\midrule"]
    for pool, plab, gk in (("kpool", "$k$-pool, $k{>}1$", "grading_any_format"), ("mace", "\\textsc{MACE}, $k{>}1$", "grading")):
        first = True
        for jn, d in pg[pool].items():
            g = d[gk]
            body.append(f"{plab if first else ''} & {jn} & " + " & ".join(fc(*g[f'{k}_minus_blind'][:2]) for k in ("reference", "max_rule", "reveal")) + " \\\\")
            first = False
        body.append("\\addlinespace")
    body = body[:-1]
    ub = J("r16b_unique_answer_grading.json")
    body.append("\\midrule")
    for pool, plab in (("mace_k1", "\\textsc{MACE}, $k{=}1$ (all correct)"), ("math500", "MATH-500 (all correct)")):
        first = True
        for jn, g in ub[pool].items():
            body.append(f"{plab if first else ''} & {jn} & " + " & ".join(fc(*g[f'{k}_minus_blind'][:2]) for k in ("reference", "max_rule", "reveal")) + " \\\\")
            first = False
    write("protocol_grading.tex", done(body))
    body = ["\\begin{tabular}{llcc}", "\\toprule", "Pool & Judge & Max rule $-$ reference & Blind, then reveal $-$ reference \\\\", "\\midrule"]
    for jn, d in pg["math500"].items():
        s_ = d["selection"]
        body.append(f"MATH-500 & {jn} & {p4(s_['max_rule_minus_reference'])} & {p4(s_['reveal_minus_reference'])} \\\\")
    body.append("\\addlinespace")
    first = True
    for jn, d in pg["kpool"].items():
        s_ = d["selection_any_format"]
        body.append(f"{'$k$-pool, $k{>}1$, any format' if first else ''} & {jn} & {p4(s_['max_rule_minus_reference'])} & {p4(s_['reveal_minus_reference'])} \\\\")
        first = False
    write("protocol_selection.tex", done(body))
    print("wrote protocol tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip protocol tables]", e)


# ---------------------------------------------------------------- round 17: protocols under the exact scorer; Sonnet 5 noise floor
try:
    ex = J("r16c_protocols_exact.json")
    body = ["\\begin{tabular}{llcccccc}", "\\toprule",
            " & & \\multicolumn{3}{c}{Best-of-64 accuracy (points)} & \\multicolumn{3}{c}{Grading AUROC} \\\\", "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}",
            "Pool & Judge & Reference & Max rule & Max $-$ reference & Reference & Max rule & Max $-$ reference \\\\", "\\midrule"]
    first = True
    for jn, d in ex["kpool"].items():
        a_, g_ = d["accuracy"], d["grading"]
        body.append(f"{'$k$-pool, $k{>}1$, any format' if first else ''} & {jn} & {p4s(a_['reference_minus_blind'])} & {p4s(a_['max_rule_minus_blind'])} & {p4s(a_['max_rule_minus_reference'])} & {fs(g_['reference_minus_blind'])} & {fs(g_['max_rule_minus_blind'])} & {fs(g_['max_rule_minus_reference'])} \\\\")
        first = False
    body.append("\\addlinespace")
    first = True
    for jn, d in ex["mace"].items():
        a_, g_ = d["accuracy_natural_mix"], d["grading_kgt1"]
        lab_ = "\\textsc{MACE} (accuracy: natural mix; AUROC: $k{>}1$)" if first else ""
        body.append(f"{lab_} & {jn} & {p4s(a_['reference_minus_blind'])} & {p4s(a_['max_rule_minus_blind'])} & {p4s(a_['max_rule_minus_reference'])} & {fs(g_['reference_minus_blind'])} & {fs(g_['max_rule_minus_blind'])} & {fs(g_['max_rule_minus_reference'])} \\\\")
        first = False
    for jn, d in ex["mace"].items():  # multi-answer accuracy, the values Table 2 quotes (round-24 review M5)
        a_ = d["accuracy_kgt1"]
        body.append(f"\\textsc{{MACE}} $k{{>}}1$, accuracy & {jn} & {p4s(a_['reference_minus_blind'])} & {p4s(a_['max_rule_minus_blind'])} & {p4s(a_['max_rule_minus_reference'])} & --- & --- & --- \\\\")
    for jn, d in ex["mace"].items():
        g_ = d["grading_k1_all_correct"]
        body.append(f"\\textsc{{MACE}} $k{{=}}1$, all correct & {jn} & --- & --- & --- & {fs(g_['reference_minus_blind'])} & {fs(g_['max_rule_minus_blind'])} & {fs(g_['max_rule_minus_reference'])} \\\\")
    body.append("\\addlinespace")
    for jn, d in ex["math500"].items():
        for cond, lab in (("refans", "final answer"), ("ref", "solution")):
            a_, g_ = d[cond]["accuracy"], d[cond]["grading_all_correct"]
            body.append(f"MATH-500, {lab} & {jn} & {p4s(a_['reference_minus_blind'])} & {p4s(a_['max_rule_minus_blind'])} & {p4s(a_['max_rule_minus_reference'])} & {fs(g_['reference_minus_blind'])} & {fs(g_['max_rule_minus_blind'])} & {fs(g_['max_rule_minus_reference'])} \\\\")
    write("protocol_exact.tex", done(body))
    print("wrote protocol_exact.tex")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip protocol_exact]", e)


# ---------------------------------------------------------------- round 20: acceptance across judges, API-judge safeguards, benchmark scores
try:
    RA = {"Sonnet 5": J("r20a_sonnet_retest.json"), "Opus 5": J("r20a_opus_retest.json")}
    PL = (("mace", "\\textsc{MACE}, $k{>}1$"), ("repl", "Replication"), ("kpool", "$k$-pool, $k{>}1$"), ("pooled", "Pooled"))

    def cnt(k, n):
        return f"{k} ({100 * k / n:.1f}\\%)" if n else "---"

    body = ["\\begin{tabular}{llrrrrrr}", "\\toprule",
            " & & \\multicolumn{3}{c}{Differ from the reference} & \\multicolumn{3}{c}{Match the reference} \\\\",
            "\\cmidrule(lr){3-5}\\cmidrule(lr){6-8}",
            "Judge & Pool & Blind 10 & Ref.\\ $\\leq 3$ & Retest $\\leq 3$ & Blind 10 & Ref.\\ $\\leq 3$ & Retest $\\leq 3$ \\\\",
            "\\midrule"]
    for jn, d in RA.items():
        first = True
        for pool, lab in PL:
            nm, m = d[pool]["nonmatch"], d[pool]["match"]
            body.append(f"{jn if first else ''} & {lab} & {nm['n']} & {cnt(nm['referenced_le3'], nm['n'])} & {cnt(nm['retest_le3'], nm['n'])} & "
                        f"{m['n']} & {cnt(m['referenced_le3'], m['n'])} & {cnt(m['retest_le3'], m['n'])} \\\\")
            first = False
        body.append("\\addlinespace")
    both = {g: [sum(RA[j]["pooled"][g][k] for j in RA) for k in ("n", "referenced_le3", "retest_le3")] for g in ("nonmatch", "match")}
    body.append(f"Both judges & Pooled & {both['nonmatch'][0]} & {cnt(both['nonmatch'][1], both['nonmatch'][0])} & {cnt(both['nonmatch'][2], both['nonmatch'][0])} & "
                f"{both['match'][0]} & {cnt(both['match'][1], both['match'][0])} & {cnt(both['match'][2], both['match'][0])} \\\\")
    mb = {g: [sum(RA[j]["mace"][g][k] for j in RA) for k in ("n", "referenced_le3", "retest_le3")] for g in ("nonmatch", "match")}
    body.append(f"Both judges & \\textsc{{MACE}}, $k{{>}}1$ & {mb['nonmatch'][0]} & {cnt(mb['nonmatch'][1], mb['nonmatch'][0])} & {cnt(mb['nonmatch'][2], mb['nonmatch'][0])} & "
                f"{mb['match'][0]} & {cnt(mb['match'][1], mb['match'][0])} & {cnt(mb['match'][2], mb['match'][0])} \\\\")
    write("r20_retest.tex", done(body))

    md, qf = J("r20d_matched_acceptance.json"), J("r20f_qwen3_acceptance.json")
    body = ["\\begin{tabular}{llrrrr}", "\\toprule",
            " & & & & \\multicolumn{2}{c}{Accepted: $n$; share $\\leq 3$ with ref.} \\\\", "\\cmidrule(lr){5-6}",
            "Judge & Pool & Threshold & Wrong accepted & Differ & Match \\\\", "\\midrule"]
    PN = {"repl": "Replication", "kpool": "$k$-pool, $k{>}1$"}
    for key, x in md.items():
        if "|" not in key:
            continue
        pool, jn = key.split("|")
        body.append(f"{jn} & {PN[pool]} & {x['threshold']:.2f} & {100 * x['wrong_pass_rate']:.1f}\\% of {x['wrong_n']} & "
                    f"{x['nonmatch']['n']}; {100 * x['nonmatch']['share_le3_with_reference']:.1f}\\% & {x['match']['n']}; {100 * x['match']['share_le3_with_reference']:.1f}\\% \\\\")
    body.append("\\addlinespace")
    ma = J("r21a_mace_acceptance.json")
    for jn in ("Qwen2.5-7B", "phi-4"):
        x = ma[f"{jn}|target3"]
        body.append(f"{jn} & \\textsc{{MACE}}, $k{{>}}1$ & {x['threshold']:.2f} & {100 * x['wrong_pass_rate']:.1f}\\% of {x['wrong_n']} & "
                    f"{x['nonmatch']['n']}; {100 * x['nonmatch']['share_le3_with_reference']:.1f}\\% & {x['match']['n']}; {100 * x['match']['share_le3_with_reference']:.1f}\\% \\\\")
    body.append("\\addlinespace")
    for key, x in qf.items():
        jn, arm = key.split("|")
        body.append(f"{jn}, {arm} & \\textsc{{MACE}} subsample & 10 & {100 * x['wrong_blind_10_share']:.1f}\\% of {x['wrong_n']} & "
                    f"{x['nonmatch']['scored_10_blind']}; {100 * x['nonmatch']['share_le3_with_reference']:.1f}\\% & {x['match']['scored_10_blind']}; {100 * x['match']['share_le3_with_reference']:.1f}\\% \\\\")
    write("r20_matched_acceptance.tex", done(body))

    sg = J("r20g_frontier_safeguards.json")

    def g_(x, k):  # three decimals: an interval such as [-0.105, -0.004] must not print as reaching zero
        return fs(x[k], d=3) if x.get(k) else "not run"

    def p_(x, k):
        return p4s(x[k]) if x.get(k) else "not run"

    body = ["\\begin{tabular}{llccccc}", "\\toprule",
            " & & \\multicolumn{3}{c}{Grading AUROC, change against blind} & \\multicolumn{2}{c}{False rejections, change against blind (points)} \\\\",
            "\\cmidrule(lr){3-5}\\cmidrule(lr){6-7}",
            "Judge & Pool & Reference & Sentence & Max rule & Reference & Sentence \\\\", "\\midrule"]
    for jn in ("Sonnet 5", "Opus 5"):
        first = True
        for pool, lab in PL[:3]:
            x = sg.get(f"{jn}|{pool}")
            if not x:
                continue
            body.append(f"{jn if first else ''} & {lab} & {g_(x, 'G_nm_ref_minus_blind')} & {g_(x, 'G_nm_inst_minus_blind')} & {g_(x, 'G_nm_max_minus_blind')} & "
                        f"{p_(x, 'FR_ref_minus_blind')} & {p_(x, 'FR_inst_minus_blind')} \\\\")
            first = False
        body.append("\\addlinespace")
    body = body[:-1] + ["\\midrule", " & & \\multicolumn{2}{c}{Sentence $-$ reference} & Max $-$ reference & \\multicolumn{2}{c}{Sentence $-$ reference} \\\\", "\\midrule"]
    for jn in ("Sonnet 5", "Opus 5"):
        first = True
        for pool, lab in PL[:3]:
            x = sg.get(f"{jn}|{pool}")
            if not x:
                continue
            body.append(f"{jn if first else ''} & {lab} & \\multicolumn{{2}}{{c}}{{{g_(x, 'G_nm_inst_minus_ref')}}} & {g_(x, 'G_nm_max_minus_ref')} & "
                        f"\\multicolumn{{2}}{{c}}{{{p_(x, 'FR_inst_minus_ref')}}} \\\\")
            first = False
    write("r20_safeguards.tex", done(body))

    lb, lm = J("r20c_leaderboard.json"), sg["leaderboard_max_rule"]
    GN = {"meta-llama__Llama-3.1-8B-Instruct": "Llama-3.1-8B-Instruct", "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
          "claude-sonnet-5": "Claude Sonnet 5", "claude-opus-5": "Claude Opus 5"}
    body = ["\\begin{tabular}{lrrrrrrr}", "\\toprule",
            " & \\multicolumn{4}{c}{Accuracy (\\%)} & & & \\\\", "\\cmidrule(lr){2-5}",
            "Model & List & Blind & Ref. & Max & Ref.\\ $-$ list & Differ & $\\leq 3$: blind; ref. \\\\",
            "\\midrule"]
    for gk, name in GN.items():
        x = lb["generators"][gk]
        body.append(f"{name} & {100 * x['accuracy_answer_list'][0]:.1f} & {100 * x['accuracy_blind'][0]:.1f} & {100 * x['accuracy_referenced'][0]:.1f} & "
                    f"{100 * lm[gk]['accuracy_max_rule'][0]:.1f} & {p4s(x['undercount_referenced_minus_list'])} & {x['correct_nonmatching']} of {x['correct']} & "
                    f"{100 * x['false_rejection_nonmatch_blind']:.1f}\\%; {100 * x['false_rejection_nonmatch_ref']:.1f}\\% \\\\")
    po = lb["pooled"]
    body += ["\\midrule",
             f"Pooled $-$ list & --- & {p4s(po['blind_minus_list'])} & {p4s(po['undercount_referenced_minus_list'])} & {p4s(lm['pooled_max_minus_list'])} & & & "
             f"{100 * po['false_rejection_nonmatch_blind']:.1f}\\%; {100 * po['false_rejection_nonmatch_ref']:.1f}\\% \\\\"]
    write("r20_leaderboard.tex", done(body))

    be = J("r20e_benchmark_open_judges.json")
    body = ["\\begin{tabular}{lrrrrr}", "\\toprule",
            "Judge & List (\\%) & Blind (\\%) & Ref.\\ (\\%) & Ref.\\ $-$ list & Differing credited: blind; ref. \\\\", "\\midrule"]
    for jn, x in be["judges"].items():
        body.append(f"{jn} & {100 * x['accuracy_answer_list'][0]:.1f} & {100 * x['accuracy_blind'][0]:.1f} & {100 * x['accuracy_referenced'][0]:.1f} & "
                    f"{p4s(x['referenced_minus_list'])} & {100 * x['nonmatching_credited_blind']:.1f}\\%; {100 * x['nonmatching_credited_referenced']:.1f}\\% \\\\")
    write("r20_benchmark_open.tex", done(body))

    GR = {"Sonnet 5": ("r21c_leaderboard_sonnet_t5.json", "r20c_leaderboard.json", "r21c_leaderboard_sonnet_t10.json", "r20g"),
          "Opus 5": ("r21a_leaderboard_opus_t5.json", "r21a_leaderboard_opus.json", "r21a_leaderboard_opus_t10.json", "r21a_maxrule_opus.json"),
          "Haiku 4.5": ("r21a_leaderboard_haiku_t5.json", "r21a_leaderboard_haiku.json", "r21a_leaderboard_haiku_t10.json", "r21a_maxrule_haiku.json")}
    body = ["\\begin{tabular}{lrcccc}", "\\toprule", "Grader & Threshold & Blind $-$ list & Ref.\\ $-$ list & Max $-$ list & $\\leq 3$: blind; ref. \\\\", "\\midrule"]
    for gn, (f5, f7, f10, fm) in GR.items():
        first = True
        for th, fn in ((5, f5), (7, f7), (10, f10)):
            if not (A / fn).exists():
                continue
            po = J(fn)["pooled"]
            mxl = "---"
            if th == 7:
                mxl = p4s(sg["leaderboard_max_rule"]["pooled_max_minus_list"]) if fm == "r20g" else (p4s(J(fm)["pooled_max_minus_list"]) if (A / fm).exists() else "---")
            body.append(f"{gn if first else ''} & {th} & {p4s(po['blind_minus_list'])} & {p4s(po['undercount_referenced_minus_list'])} & {mxl} & "
                        f"{100 * po['false_rejection_nonmatch_blind']:.1f}\\%; {100 * po['false_rejection_nonmatch_ref']:.1f}\\% \\\\")
            first = False
        if not first:
            body.append("\\addlinespace")
    if body[-1] == "\\addlinespace":
        body = body[:-1]
    write("r21_graders.tex", done(body))
    print("wrote round-20 tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-20 tables]", repr(e))


# ---------------------------------------------------------------- round 22: second reference draw; rejection by blind score
try:
    GRD = (("Sonnet 5", "r22b_redraw_sonnet.json"), ("Opus 5", "r22b_redraw_opus.json"), ("Haiku 4.5", "r22b_redraw_haiku.json"))
    body = ["\\begin{tabular}{lrccccc}", "\\toprule",
            " & & \\multicolumn{3}{c}{Referenced $-$ list (points)} & \\multicolumn{2}{c}{Credited (\\%), draw 1 $\\to$ 2 ($n$)} \\\\",
            "\\cmidrule(lr){3-5}\\cmidrule(lr){6-7}",
            "Grader & $n$ & Draw 1 & Draw 2 & Change & Stop matching & Start matching \\\\", "\\midrule"]
    models = ["\\begin{tabular}{llrrrc}", "\\toprule", "Grader & Model & List & Ref., draw 1 & Ref., draw 2 & Draw 2 $-$ draw 1 \\\\", "\\midrule"]
    GNm = {"meta-llama__Llama-3.1-8B-Instruct": "Llama-3.1-8B", "claude-haiku-4-5-20251001": "Haiku 4.5", "claude-sonnet-5": "Sonnet 5", "claude-opus-5": "Opus 5"}
    for gn, fn in GRD:
        if not (A / fn).exists():
            continue
        d = J(fn)
        po = d["pooled"]
        body.append(f"{gn} & {d['questions']} & {p4s(po['draw1_minus_list'])} & {p4s(po['draw2_minus_list'])} & {p4s(po['draw2_minus_draw1'])} & "
                    f"{100 * po['losers_credited_draw1'][0]:.0f} $\\to$ {100 * po['losers_credited_draw2'][0]:.0f} ({po['losers_credited_draw1'][2]}) & "
                    f"{100 * po['gainers_credited_draw1'][0]:.0f} $\\to$ {100 * po['gainers_credited_draw2'][0]:.0f} ({po['gainers_credited_draw1'][2]}) \\\\")
        first = True
        for gk, v in d["generators"].items():
            models.append(f"{gn if first else ''} & {GNm[gk]} & {100 * v['accuracy_answer_list'][0]:.1f} & {100 * v['accuracy_ref_draw1'][0]:.1f} & "
                          f"{100 * v['accuracy_ref_draw2'][0]:.1f} & {p4(v['draw2_minus_draw1'])} \\\\")
            first = False
        models.append("\\addlinespace")
    write("r22_redraw.tex", done(body))
    write("r22_redraw_models.tex", done(models[:-1]))
    rk = J("r22d_ranking_intervals.json")
    body = ["\\begin{tabular}{lcccc}", "\\toprule", "Grader & Answer list & Blind & Reference, draw 1 & Reference, draw 2 \\\\", "\\midrule"]
    for gn, fn in GRD:
        d2 = J(fn)["haiku_minus_llama"] if (A / fn).exists() else None
        body.append(f"{gn} & {p4s(rk[gn]['answer_list'])} & {p4s(rk[gn]['blind'])} & {p4s(rk[gn]['reference'])} & {p4s(d2['ref_draw2']) if d2 else '---'} \\\\")
    write("r22_haiku_llama.tex", done(body))
    bins = J("r22c_acceptance_bins.json")
    PNm = {"mace": "\\textsc{MACE}", "repl": "Replication", "kpool": "$k$-pool"}

    def cell(b, g):
        x = b[g]
        return "---" if x["share_le3_with_reference"] is None else f"{100 * x['share_le3_with_reference']:.0f} ({x['n']})"

    for kind, name, hdr in (("open", "r22_bins_open.tex", ["$<5$", "5--7", "7--9", "9--9.6", "9.6--9.8", "$\\geq 9.8$"]),
                            ("api", "r22_bins_api.tex", ["$\\leq 6$", "7--8", "9", "10"])):
        keys = [k for k in bins if (k.split("|")[1] in ("Sonnet 5", "Opus 5")) == (kind == "api")]
        body = ["\\begin{tabular}{ll" + "r" * len(hdr) + "}", "\\toprule", "Judge and pool & Answers & " + " & ".join(hdr) + " \\\\", "\\midrule"]
        for k in keys:
            pn, jn = k.split("|")
            body.append(f"{jn}, {PNm[pn]} & differ & " + " & ".join(cell(b, "nonmatch") for b in bins[k]) + " \\\\")
            body.append(" & match & " + " & ".join(cell(b, "match") for b in bins[k]) + " \\\\")
        write(name, done(body))
    print("wrote round-22 tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-22 tables]", repr(e))


# ---------------------------------------------------------------- round 23: same-reference regrade
try:
    RG = (("Sonnet 5", "r23a_regrade_sonnet.json"), ("Opus 5", "r23a_regrade_opus.json"), ("Haiku 4.5", "r23a_regrade_haiku.json"))
    body = ["\\begin{tabular}{lrcccccc}", "\\toprule",
            " & & \\multicolumn{2}{c}{Pooled accuracy change} & \\multicolumn{2}{c}{Credited (\\%): first $\\to$ regrade $\\to$ draw 2} & \\multicolumn{2}{c}{Haiku $-$ Llama gap change} \\\\",
            "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\\cmidrule(lr){7-8}",
            "Grader & $n$ & Regrade & Draw 2 & Stop matching & Start matching & Regrade & Draw 2 \\\\", "\\midrule"]
    for gn, fn in RG:
        if not (A / fn).exists():
            continue
        d = J(fn)
        po, hl = d["pooled"], d["haiku_minus_llama"]

        def trip(k):
            return f"{100 * po[k + '_credited_original'][0]:.0f} $\\to$ {100 * po[k + '_credited_regrade'][0]:.0f} $\\to$ {100 * po[k + '_credited_draw2'][0]:.0f}"

        body.append(f"{gn} & {d['questions']} & {p4s(po['same_draw_change'])} & {p4s(po['between_draw_change'])} & {trip('stop')} & {trip('start')} & "
                    f"{p4s(hl['same_draw_change'])} & {p4s(hl['between_draw_change'])} \\\\")
    write("r23_regrade.tex", done(body))
    print("wrote round-23 table")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-23 table]", repr(e))


# ---------------------------------------------------------------- round 24 (v2): standard graders and fixes
try:
    CELLS = (("s41", "SimpleQA grader", "GPT-4.1"), ("h41", "BrowseComp judge", "GPT-4.1"), ("h03", "HLE judge", "o3-mini"),
             ("sS5", "SimpleQA grader", "Sonnet~5"), ("hS5", "HLE judge", "Sonnet~5"))
    body = ["\\begin{tabular}{llcccccc}", "\\toprule",
            " & & \\multicolumn{2}{c}{Accuracy minus list (points)} & \\multicolumn{2}{c}{Differing correct credited (\\%)} & \\multicolumn{2}{c}{Wrong credited (\\%)} \\\\",
            "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\\cmidrule(lr){7-8}",
            "Prompt & Judge & One reference & Full list & One ref. & Full list & One ref. & Full list \\\\", "\\midrule"]
    for cell, prompt, judge in CELLS:
        po = J(f"r24a_{cell}.json")["pooled"]
        body.append(f"{prompt} & {judge} & {p4s(po['ref_minus_list'])} & {p4s(po['reflist_minus_list'])} & "
                    f"{100 * po['nonmatch_correct_credited_ref'][0]:.1f} & {100 * po['nonmatch_correct_credited_reflist'][0]:.1f} & "
                    f"{100 * po['wrong_credited_ref'][0]:.1f} & {100 * po['wrong_credited_reflist'][0]:.1f} \\\\")
    write("r24_standard.tex", done(body))
    body = ["\\begin{tabular}{lcccccc}", "\\toprule",
            " & \\multicolumn{3}{c}{Grading AUROC} & \\multicolumn{3}{c}{Change against blind} \\\\",
            "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
            "Judge & Blind & One ref. & Full list & One ref. & Full list & False rejections, full list (pp) \\\\", "\\midrule"]
    for j, lab in (("sonnet", "Sonnet~5"), ("opus", "Opus~5"), ("gpt41", "GPT-4.1")):
        d = J(f"r24c_{j}.json")
        body.append(f"{lab} & {d['G_blind'][0]:.3f} & {d['G_ref'][0]:.3f} & {d['G_reflist'][0]:.3f} & {fs(d['G_ref_minus_blind'], 3)} & "
                    f"{fs(d['G_reflist_minus_blind'], 3)} & {p4s(d['FR_reflist_minus_blind'])} \\\\")
    d = J("r24d_think_sentence.json")
    body += ["\\midrule", "\\multicolumn{7}{@{}l}{\\emph{Sonnet~5, when the answers are not listed: change against blind}}\\\\",
             " & \\multicolumn{3}{l}{Setting} & AUROC & & False rejections (pp) \\\\"]
    for key, lab in (("sentence_alone", "Full-credit sentence"), ("thinking_alone", "Adaptive thinking"), ("combined", "Thinking and the sentence")):
        body.append(f" & \\multicolumn{{3}}{{l}}{{{lab}}} & {fs(d[key]['G_change'], 3)} & & {p4s(d[key]['FR_change'])} \\\\")
    write("r24_fix.tex", done(body))
    b = J("r24b_gpt41.json")
    body = ["\\begin{tabular}{lcccc}", "\\toprule", "Model & Answer list & Blind & One reference & Second reference \\\\", "\\midrule"]
    GEN = (("meta-llama__Llama-3.1-8B-Instruct", "Llama-3.1-8B"), ("claude-haiku-4-5-20251001", "Haiku~4.5"), ("claude-sonnet-5", "Sonnet~5"), ("claude-opus-5", "Opus~5"))
    for key, lab in GEN:
        g = b["generators"][key]
        body.append(f"{lab} & {100 * g['list'][0]:.1f} & {100 * g['blind'][0]:.1f} & {100 * g['ref'][0]:.1f} & --- \\\\")
    body.append(f"Pooled, minus list & & {p4s(b['pooled']['blind_minus_list'])} & {p4s(b['pooled']['ref_minus_list'])} & {p4s(b['redraw']['draw2_minus_list'])} \\\\")
    write("r24_gpt41.tex", done(body))
    print("wrote round-24 tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-24 tables]", repr(e))


# ---------------------------------------------------------------- round 25 (v2): judges that reason before deciding
try:
    body = ["\\begin{tabular}{llccccc}", "\\toprule",
            " & & \\multicolumn{2}{c}{Accuracy minus list (points)} & \\multicolumn{3}{c}{Credited (\\%): blind $\\to$ reference} \\\\",
            "\\cmidrule(lr){3-4}\\cmidrule(lr){5-7}",
            "Judge type & Judge & Blind & Reference & Differing correct & Matching correct & Wrong \\\\", "\\midrule"]
    for tpl, tl in (("cot", "Chain of thought"), ("verify", "Verify first"), ("solve", "Solve first")):
        for j, jl in (("gpt41", "GPT-4.1"), ("sonnet", "Sonnet~5")):
            po = J(f"r25_{tpl}_{j}.json")["pooled"]
            arrow = lambda k: f"{100 * po[k + '_credited_blind'][0]:.1f} $\\to$ {100 * po[k + '_credited_ref'][0]:.1f}"
            body.append(f"{tl if j == 'gpt41' else ''} & {jl} & {p4s(po['blind_minus_list'])} & {p4s(po['ref_minus_list'])} & "
                        f"{arrow('nonmatch_correct')} & {arrow('match_correct')} & {arrow('wrong')} \\\\")
    write("r25_types.tex", done(body))
    print("wrote round-25 table")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-25 table]", repr(e))


# ---------------------------------------------------------------- v2 prevalence audit (papers/analysis/prevalence_v2)
try:
    PV = json.loads((A / "prevalence_v2" / "prevalence_v2_results.json").read_text())
    body = ["\\begin{tabular}{lrrrrcccc}", "\\toprule",
            "Dataset & $n$ & Several & Unique & Unclear & Several (\\%) & $\\kappa$ & Both (\\%) & Either (\\%) \\\\", "\\midrule"]
    for key, lab in (("simpleqa", "SimpleQA"), ("browsecomp", "BrowseComp"), ("hle", "HLE (text, exact answer)"), ("triviaqa", "TriviaQA"),
                     ("webinstruct", "WebInstruct-verified (RL)")):
        d = PV[key]
        r = d["multi_rate"]
        k = d["agreement_passA_vs_passB"]["kappa_multi_vs_rest"]
        both = d["both_annotators_multi_lower"]
        either = d["either_annotator_multi_upper"]
        fmt = lambda x: "---" if x is None else f"{100 * (x['rate'] if isinstance(x, dict) else x / d['n']):.1f}"
        body.append(f"{lab} & {d['n']} & {d['multi']} & {d['unique']} & {d['unclear']} & {100 * r['rate']:.1f} {{\\scriptsize$[{100 * r['wilson_ci95'][0]:.1f},{100 * r['wilson_ci95'][1]:.1f}]$}} & "
                    f"{'---' if k is None else f'{k:.2f}'} & {fmt(both)} & {fmt(either)} \\\\")
    write("prevalence_v2.tex", done(body))
    print("wrote prevalence v2 table")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip prevalence v2 table]", repr(e))


# ---------------------------------------------------------------- round 26 (v2): instruction against reasoning, false acceptance, RL verifiers
try:
    JN = (("gpt41", "GPT-4.1"), ("sonnet", "Sonnet~5"))
    body = ["\\begin{tabular}{llcccc}", "\\toprule",
            "Judge & Prompt & Condition & Accuracy minus list (points) & Differing correct credited (\\%) & Wrong credited (\\%) \\\\", "\\midrule"]
    for j, jl in JN:
        d = J(f"r26a_{j}.json")["conditions"]
        for key, lab, cond in (("direct|noref", "Direct yes/no", "blind"), ("direct|ref", "Direct yes/no", "reference"),
                               ("hle|ref", "HLE judge, verbatim", "reference"), ("hle_edit|ref", "HLE judge, match clause removed", "reference")):
            x = d[key]
            body.append(f"{jl if key == 'direct|noref' else ''} & {lab} & {cond} & {p4s(x['minus_list'])} & {100 * x['nonmatch_credited'][0]:.1f} & {100 * x['wrong_credited'][0]:.1f} \\\\")
        body.append("\\addlinespace")
    body[-1] = "\\bottomrule"
    write("r26_instruction.tex", "\n".join(body + ["\\end{tabular}"]) + "\n")
    body = ["\\begin{tabular}{llcccc}", "\\toprule",
            "Judge & Prompt & AUROC, blind $\\to$ reference & AUROC change & False rejections change (pp) & False acceptances change (pp) \\\\", "\\midrule"]
    for j, jl in JN:
        d = J(f"r26b_{j}.json")
        for t, tl in (("direct", "Direct yes/no"), ("verify", "Verify first"), ("solve", "Solve first")):
            lv, ch = d["levels"], d["changes"][t]
            body.append(f"{jl if t == 'direct' else ''} & {tl} & {lv[t + '|noref']['G'][0]:.3f} $\\to$ {lv[t + '|ref']['G'][0]:.3f} & {fs(ch['G'], 3)} & {p4s(ch['FR'])} & {p4s(ch['FA'])} \\\\")
        h = d["changes"]["hle_edit_minus_hle"]
        body.append(f" & HLE edited minus verbatim & {d['levels']['hle|ref']['G'][0]:.3f} $\\to$ {d['levels']['hle_edit|ref']['G'][0]:.3f} & {fs(h['G'], 3)} & {p4s(h['FR'])} & {p4s(h['FA'])} \\\\")
        body.append("\\addlinespace")
    body[-1] = "\\bottomrule"
    write("r26_subsample.tex", "\n".join(body + ["\\end{tabular}"]) + "\n")
    body = ["\\begin{tabular}{lcccccc}", "\\toprule",
            " & \\multicolumn{2}{c}{Accuracy minus list (points)} & \\multicolumn{2}{c}{Differing correct credited (\\%)} & \\multicolumn{2}{c}{Wrong credited (\\%)} \\\\",
            "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}",
            "Verifier & One reference & Full list & One ref. & Full list & One ref. & Full list \\\\", "\\midrule"]
    for v, vl in (("general", "General-Reasoner verifier (1.5B)"), ("compass", "CompassVerifier-3B")):
        d = J(f"r26c_{v}.json")["conditions"]
        r, l = d["v|ref"], d["v|reflist"]
        body.append(f"{vl} & {p4s(r['minus_list'])} & {p4s(l['minus_list'])} & {100 * r['nonmatch_credited'][0]:.1f} & {100 * l['nonmatch_credited'][0]:.1f} & "
                    f"{100 * r['wrong_credited'][0]:.1f} & {100 * l['wrong_credited'][0]:.1f} \\\\")
    write("r26_verifiers.tex", done(body))
    print("wrote round-26 tables")
except (KeyError, TypeError, FileNotFoundError) as e:
    print("[skip round-26 tables]", repr(e))
