# Multi-answer prevalence audit (single-reference datasets)

Date: 2026-09-12. **All labels were produced by LLM annotators (Claude), not humans**: pass 1 by the orchestrating Claude session, pass 2 by fresh Claude subagents that saw only the definitions and the items (not pass-1 labels); disagreements were adjudicated by the pass-1 annotator, and each reason is recorded. Both passes come from the same model family, so their errors may be correlated and kappa may overstate reliability. A human spot-check of the MULTI and UNCLEAR items is recommended before citing.

## Question
In widely used datasets that ship ONE reference answer per question, what fraction of questions admit two or more DISTINCT valid final answers?

## Definitions (applied strictly)
- **MULTI (k>1):** the question as written is satisfied by at least two final answers that are not equivalent (not the same number, expression, or set written differently). Examples: "find a positive integer n such that ...", "give an example of ...", a question genuinely ambiguous between two readings with different correct answers, or a free parameter the question leaves unpinned.
- **UNIQUE (k=1):** exactly one correct final answer up to equivalence. This includes "find all x" questions whose answer is one set, smallest/largest questions, equivalent forms, and numeric answers within rounding tolerance.
- **UNCLEAR:** cannot be decided without deep solving, or the question is malformed (missing figure or choices, inconsistent data, undefined symbols).
- Surface-equivalent forms (1/2 vs 0.5, x=3 vs 3) are **not** MULTI. A wrong reference is **not** MULTI by itself. Conservative rule: when in doubt, UNIQUE or UNCLEAR.
- Extra NQ-open rules: aliases are not MULTI. MULTI requires genuinely different correct entities, a genuine two-reading ambiguity, or a *temporal* question whose answer has changed and whose wording fixes no time (temporal items are reported separately). Complete co-author or co-developer sets and fixed-set answers ("who survives", "which aqueducts") count as one answer.
- Rules settled during adjudication: "find the value of x" with two roots is MULTI, because each root satisfies the question as written (not a "find all"). A question whose stated request differs from the quantity the reference answers is UNCLEAR.

## Results

| Dataset | n | MULTI | UNIQUE | UNCLEAR | MULTI rate [95% Wilson] | kappa (3-class) | kappa (MULTI vs rest) | raw agree | disagreements | both-annotator MULTI (lower) | either-annotator MULTI (upper) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MATH-500 | 200 | 0 | 200 | 0 | 0.0% [0.0, 1.9] | undefined (100% agree) | undefined (100% agree) | 100.0% | 0 | 0 (0.0%) | 0 (0.0%) |
| GSM8K test | 200 | 5 | 194 | 1 | 2.5% [1.1, 5.7] | 0.91 | 0.89 | 99.5% | 1 | 4 (2.0%) | 5 (2.5%) |
| DeepScaleR-Preview (RLVR train) | 200 | 5 | 182 | 13 | 2.5% [1.1, 5.7] | 0.82 | 0.72 | 97.0% | 6 | 4 (2.0%) | 7 (3.5%) |
| Natural Questions open (val) | 200 | 60 | 132 | 8 | 30.0% [24.1, 36.7] | 0.72 | 0.74 | 86.5% | 27 | 53 (26.5%) | 76 (38.0%) |

- NQ-open without temporal items: 37/200 = 18.5% [13.7, 24.5]. MULTI subtypes: {'temporal': 23, 'ambiguous_reading': 21, 'multiple_entities': 16}.
- Rates excluding UNCLEAR from the denominator: GSM8K 2.5%, DeepScaleR 2.7%, NQ-open 31.2%.
- **Takeaway:** single-answer math benchmarks are almost all UNIQUE. MATH-500 has 0/200 MULTI (upper bound 1.9%), and both GSM8K and DeepScaleR are at 2.5% (upper bound ~5.7%). The math MULTI cases are mostly wording ambiguities and unpinned parameters, not "give an example" questions. Open-domain QA is very different: about 30% MULTI, or 18.5% without temporal drift, which is in line with AmbigQA's finding that NQ-open is often ambiguous.
- **Separate data-quality signal (not MULTI):** DeepScaleR has 13/200 UNCLEAR (malformed: missing figures or choices, inconsistent data, impossible conditions) and several multi-part prompts where the reference answers only one part. Several references look wrong (e.g. gsm8k-454, deepscaler-25638, deepscaler-27893, deepscaler-29528). One DeepScaleR "find all" item has an incomplete reference (deepscaler-31229: answer set (18, -18), reference 18).

## Datasets and sampling
- **MATH-500**: HuggingFaceH4/MATH-500 (test, 500 rows); seeded sample of 200: random.seed(0); random.sample(range(500),200) (sorted). Items: `items_math500.jsonl` / `.csv`.
- **GSM8K test**: openai/gsm8k, config main, split test (1319 rows); random.seed(0); random.sample(range(1319),200) (sorted). Items: `items_gsm8k.jsonl` / `.csv`.
- **DeepScaleR-Preview (RLVR train)**: agentica-org/DeepScaleR-Preview-Dataset, split train (40315 rows); random.seed(0); random.sample(range(40315),200) (sorted). Items: `items_deepscaler.jsonl` / `.csv`.
- **Natural Questions open (val)**: google-research-datasets/nq_open, split validation (3610 rows); chosen over TriviaQA (both allowed by the brief; NQ-open is a small direct download); random.seed(0); random.sample(range(3610),200) (sorted). Items: `items_nqopen.jsonl` / `.csv`.
- No substitutions were needed. MATH-500 used the seeded 200-item option rather than all 500. For the optional open-domain set, NQ-open was used rather than TriviaQA.

## Representative MULTI examples (alternatives verified)
Math alternatives were checked with python (`checks_gsm8k.py`, `checks_deepscaler.py`). NQ-open alternatives rest on annotator knowledge only (no web search), so they are lower-confidence.

### MATH-500
No MULTI items. Nearest borderline: math500-385 ("round to the nearest whole number": rounding the final difference gives 22 = reference, rounding each currency amount first gives 23). Both annotators labeled it UNIQUE.

### GSM8K test
- **gsm8k-187** (ambiguous_reading): "Mandy owes Benedict $100. They agreed to have monthly interest of 2%. If Mandy was able to pay it after 3 months, how much should she give to Benedict?" Reference: `106`. Alternative: **106.12**. Monthly compounding: 100*1.02^3 = 106.1208 (python); simple interest gives the reference 106.
- **gsm8k-306** (ambiguous_reading): "A bakery produces 60 loaves of bread each day. Two-thirds of the loaves are sold in the morning and half of what is left is sold equally in the afternoon and evening. How many loaves of bread are sold in the afternoon?" Reference: `10`. Alternative: **5**. Literal parse: 20 loaves left; "half of what is left" (10) is split equally between afternoon and evening -> 5; reference splits all 20 -> 10.
- **gsm8k-649** (ambiguous_reading): "Fishio posted her selfie on Instagram. She received 2000 likes on the photo after 1 week. Three weeks later, the number of likes was 70 times as many as the initial number of likes. If she received 20000 more new likes recently, how many In..." Reference: `162000`. Alternative: **160000**. "The number of likes was 70 times the initial" read as the total: 140000 + 20000 = 160000; reference adds 140000 new likes to 2000 -> 162000.
- **gsm8k-93** (ambiguous_reading): "Lee used to be able to run the 400-meter hurdles two seconds faster than Gerald would run the 400-meter hurdles.  But Gerald changed his diet, which improved his speed by 10%.  If Lee runs the 400-meter hurdles in 38 seconds, how fast can G..." Reference: `36`. Alternative: **36.36**. Speed up 10% means time = 40/1.1 = 36.36 s; reference reduces time by 10% -> 36.
- **gsm8k-1254** (ambiguous_reading): "Louise is an artist and needs to apply a coat of varnish to her latest paintings. Usually it takes 7 minutes for the coat of varnish to dry on one painting. However, today she is using a new varnish and it takes 12 minutes for the coat to d..." Reference: `30`. Alternative: **5**. If the 6 paintings dry at the same time, the new varnish takes 12-7 = 5 min longer; reference sums per painting -> 30.

### DeepScaleR-Preview (RLVR train)
- **deepscaler-30908** (other): "The school club sells 200 tickets for a total of $2500. Some tickets are sold at full price, and the rest are sold for one-third the price of the full-price tickets. Determine the amount of money raised by the full-price tickets." Reference: `1250`. Alternative: **750 (or 2250)**. Underdetermined p(2f+200)=7500: f=25 tickets at $30 + 175 at $10 = 2500 -> full-price revenue 750; f=150 at $15 + 50 at $5 = 2500 -> 2250; reference f=50,p=25 -> 1250 (python-enumerated).
- **deepscaler-31879** (other): "Given two vectors in space, $\overrightarrow{a} = (x - 1, 1, -x)$ and $\overrightarrow{b} = (-x, 3, -1)$. If $\overrightarrow{a}$ is perpendicular to $\overrightarrow{b}$, find the value of $x$." Reference: `-1`. Alternative: **3**. a.b = -x^2+2x+3 = 0 has roots 3 and -1; x=3 gives a=(2,1,-3), b=(-3,3,-1), dot = -6+3+3 = 0 (python); question asks for "the value", reference -1.
- **deepscaler-7605** (other): "Given that $\cos(\pi+\theta) = -\frac{1}{2}$, find the value of $\tan(\theta - 9\pi)$." Reference: `\sqrt{3}`. Alternative: **-\sqrt{3}**. theta = -pi/3 satisfies cos(pi+theta) = -1/2 and gives tan(theta-9pi) = -sqrt3 (python); no quadrant given; reference sqrt3.
- **deepscaler-12237** (ambiguous_reading): "In a row of 10 chairs, one of which is broken and cannot be used, Mary and James randomly select their seats. What is the probability that they do not sit next to each other?" Reference: `\frac{7}{9}`. Alternative: **29/36**. Broken chair in an interior position leaves 7 adjacent usable pairs of 36 -> 29/36; end chair -> 7/9 (reference); enumerated all 10 positions in python.
- **deepscaler-8179** (ambiguous_reading): "If a podcast series that lasts for 837 minutes needs to be stored on CDs and each CD can hold up to 75 minutes of audio, determine the number of minutes of audio that each CD will contain." Reference: `69.75`. Alternative: **64.38 (837/13)**. Weakest item: "up to 75 minutes" does not force the minimum number of CDs; 13 equal CDs hold 64.38 min each; reference assumes 12 -> 69.75.

### Natural Questions open (val)
- **nqopen-2502** (multiple_entities): "which president of the united states was a boy scout" Reference: `Gerald Ford | President Gerald Ford`. Alternative: **John F. Kennedy**. JFK was the first president who had been a Boy Scout; Ford was the only Eagle Scout; gold lists only Ford.
- **nqopen-2783** (ambiguous_reading): "what does ss stand for on naval ships" Reference: `Single-screw Steamship`. Alternative: **submarine**. "SS" on naval ships is the US Navy hull classification for submarine; gold gives the civilian steamship prefix.
- **nqopen-3458** (ambiguous_reading): "when was the death penalty reinstated in oregon" Reference: `1984`. Alternative: **1978**. Oregon restored the death penalty by ballot in 1978 (struck down 1981) and again in 1984; gold only 1984.
- **nqopen-1154** (temporal): "who has won the most f1 grand prix" Reference: `Michael Schumacher`. Alternative: **Lewis Hamilton**. Temporal: Schumacher (91) held the record until Hamilton passed him in 2020.
- **nqopen-3450** (ambiguous_reading): "who is stephanie's mom on the bold and the beautiful" Reference: `Ridge Forrester | Taylor Hayes | Hunter Tylo`. Alternative: **Ann Douglas**. Two characters named Stephanie Forrester: Stephanie Sr.'s mother is Ann Douglas; Steffy's mother is Taylor Hayes (gold).

## All MULTI and UNCLEAR ids

- **GSM8K test** MULTI: 93, 187, 306, 649, 1254*  (* = adjudicated)
- **GSM8K test** UNCLEAR: 255: malformed: says ten stalls then twenty stalls; 10 stalls -> 8*24=192 (ref), 20 stalls of 2
- **DeepScaleR-Preview (RLVR train)** MULTI: 7605, 8179, 12237, 30908, 31879*  (* = adjudicated)
- **DeepScaleR-Preview (RLVR train)** UNCLEAR: 865: figure missing (AMC grid); 2532: answer choices missing ("then:"); 2653: variable symbols stripped; t-s vs s-t sign undetermined; 12476: "as shown" figure missing; 19877: diagram missing; 3x4 dots gives 18 axis-aligned rectangles, ref 60 matches 3x4 cells; 20325: B_1 undefined (likely O_1); 21807: orientation of 2x3 rectangle unclear and ref 5/2 inconsistent with both; 25224: inconsistent data: orange = 160/6 not integer; ref 27; 25643: Final request ("find the equation of line AB") has two valid lines y=x and y=-x, but the r; 26863: expression not scale invariant (deg 4/deg 6) so unbounded; malformed; 27487: Verified: adding two balls of the drawn colour keeps the red count even (2,4,6,8), so "exa; 29358: 640=2^9+2^7 uniquely; "at least three distinct powers" impossible; 32065: with a+b+c=3 the expression is not constant (likely a+b+c=0)
- **Natural Questions open (val)** MULTI: 4, 165, 254, 255, 257, 472, 533, 572, 599, 612, 698, 753*, 837, 894, 903, 977, 1060, 1065, 1066, 1127, 1154, 1234, 1295, 1298, 1373, 1658, 1717, 1834, 1845*, 2094, 2135, 2137, 2181, 2188, 2224, 2247*, 2257, 2350, 2389*, 2465, 2502, 2506, 2509, 2597, 2689, 2783, 2801, 2889, 2947, 3215, 3318, 3324, 3364, 3391, 3450*, 3458*, 3479, 3483, 3544*, 3591  (* = adjudicated)
- **Natural Questions open (val)** UNCLEAR: 446: record depends on era/definition; gold Tim Duncan doubtful; 995: malformed; gold six|two inconsistent; 1523: Version (US/UK/other) unspecified, but UK has several tied GBP1M winners and neither annot; 2004: Classification scheme unspecified (multinational corporation / retail chain / for-profit);; 2214: Earliest continent is scientifically debated (Ur vs Vaalbara) and gold Pangaea is likely w; 2415: no story specified; 2600: Malformed: the Coral Sea is a marginal sea of the Pacific, no crisp meeting point.; 3254: Ranking is year- and source-dependent; neither annotator could confirm a concrete alternat

## Adjudications (disagreements between passes)

- gsm8k-1254: P1=UNIQUE, P2=MULTI -> **MULTI**. Both annotators identified the concurrent-drying reading; the question never says coats are applied one after another, so 12-7=5 min longer is as defensible as the cumulative 6*(12-7)=30 (ref).
- deepscaler-23406: P1=MULTI, P2=UNIQUE -> **UNIQUE**. "standard deviation of this sample" (not "sample standard deviation"); in the source curriculum it is the n-denominator SD; n-1 variant is a convention difference -> conservative UNIQUE.
- deepscaler-25638: P1=UNCLEAR, P2=UNIQUE -> **UNIQUE**. VP1/VP2 are labeled, so the count is determined (997920); the reference 554400 is a reference error, not answer multiplicity.
- deepscaler-25643: P1=MULTI, P2=UNIQUE -> **UNCLEAR**. Final request ("find the equation of line AB") has two valid lines y=x and y=-x, but the reference answers a different quantity (area 8/5); the reference/question mismatch makes the item malformed rather than cleanly MULTI -> conservative UNCLEAR.
- deepscaler-27487: P1=UNIQUE, P2=UNCLEAR -> **UNCLEAR**. Verified: adding two balls of the drawn colour keeps the red count even (2,4,6,8), so "exactly five red" is impossible; malformed transcription of the original problem.
- deepscaler-27893: P1=UNCLEAR, P2=UNIQUE -> **UNIQUE**. Natural reading has one answer (~527 m, computed); the reference 16.38 is irreproducible, which is a reference error, not multiplicity.
- deepscaler-31879: P1=MULTI, P2=UNIQUE -> **MULTI**. Question asks for "the value of x" (not "find all"); a.b=-x^2+2x+3=0 has roots x=3 and x=-1 (python-verified), each satisfies the question; reference lists only -1. Literal MULTI definition applies.
- nqopen-373: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Two co-writers form one complete answer (Pebe Sebert and Hugh Moffatt); co-author sets treated as UNIQUE throughout.
- nqopen-753: P1=UNIQUE, P2=MULTI -> **MULTI**. "Who sings" admits the character (Hodel, ref) or a performer (Julia Migenes, 1964 Broadway; Michele Marsh, 1971 film); parallels Big Momma item 1298.
- nqopen-908: P1=UNIQUE, P2=UNCLEAR -> **UNIQUE**. Edition page-count variation is a small numeric tolerance, not distinct answers; neither annotator could name a concrete alternative with confidence.
- nqopen-1110: P1=MULTI, P2=UNIQUE -> **UNIQUE**. "Amendments to the constitution" are the 27 ratified ones; 33 counts proposals that did not become amendments.
- nqopen-1352: P1=MULTI, P2=UNIQUE -> **UNIQUE**. Season 11 is complete with 24 episodes; gold 14/12 is an outdated partial count, not a second valid answer.
- nqopen-1523: P1=UNCLEAR, P2=MULTI -> **UNCLEAR**. Version (US/UK/other) unspecified, but UK has several tied GBP1M winners and neither annotator could confirm the second gold name; cannot decide cleanly.
- nqopen-1577: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Literal "tournament of power start" is the tournament itself (ep. 97, July 2017); the Feb 2017 saga start is a looser reading -> conservative UNIQUE.
- nqopen-1722: P1=UNIQUE, P2=MULTI -> **UNIQUE**. smen / samna / samneh are transliterations of the same Arabic word -> aliases.
- nqopen-1845: P1=UNIQUE, P2=MULTI -> **MULTI**. Person heading WV executive changed (Jim Justice 2017-2025, Patrick Morrisey 2025-) and the wording fixes no time; same temporal rule as other items.
- nqopen-1952: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Henry system co-devised (Henry with Haque and Bose) -> treated as one co-developer set, consistent with co-writer rule.
- nqopen-2004: P1=UNIQUE, P2=UNCLEAR -> **UNCLEAR**. Classification scheme unspecified (multinational corporation / retail chain / for-profit); vague rather than cleanly multi.
- nqopen-2021: P1=UNIQUE, P2=MULTI -> **UNIQUE**. English/Welsh patronymic origin is one answer at British-Isles granularity.
- nqopen-2213: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Sierra Nevada snowmelt -> Feather River -> Delta intake is one water path described at different granularity.
- nqopen-2214: P1=UNIQUE, P2=UNCLEAR -> **UNCLEAR**. Earliest continent is scientifically debated (Ur vs Vaalbara) and gold Pangaea is likely wrong; cannot decide cleanly.
- nqopen-2247: P1=UNIQUE, P2=MULTI -> **MULTI**. Venue changed (Sherwood CC, Thousand Oaks until 2013; Albany, Bahamas since 2015) and present tense fixes no time; same temporal rule as Astros item 3391.
- nqopen-2357: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Composite anatomical answer (central retinal artery via optic nerve); choroid reading is a different vessel bed -> conservative UNIQUE.
- nqopen-2389: P1=UNIQUE, P2=MULTI -> **MULTI**. Conference lead changed over time: AFC led through the 1970s-early 1980s (e.g. 11-4 after SB XV), NFC leads in the gold era; ties at times.
- nqopen-2600: P1=UNIQUE, P2=UNCLEAR -> **UNCLEAR**. Malformed: the Coral Sea is a marginal sea of the Pacific, no crisp meeting point.
- nqopen-2857: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Tavarez is the Spanish form of Portuguese Tavares; one etymology at different depth -> conservative UNIQUE.
- nqopen-2996: P1=UNIQUE, P2=MULTI -> **UNIQUE**. NYC supply systems (Catskill, Delaware, Croton) form one set answer.
- nqopen-3254: P1=MULTI, P2=UNCLEAR -> **UNCLEAR**. Ranking is year- and source-dependent; neither annotator could confirm a concrete alternative rank.
- nqopen-3380: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Pacific Northwest states form one set answer.
- nqopen-3431: P1=MULTI, P2=UNIQUE -> **UNIQUE**. "played" plus title "101 Dalmatians" matches the 1996 live-action film (1961 film is "One Hundred and One Dalmatians", voice role) -> Glenn Close.
- nqopen-3450: P1=UNCLEAR, P2=MULTI -> **MULTI**. Two characters are named Stephanie Forrester: Stephanie Sr. (mother Ann Douglas) and Steffy (mother Taylor Hayes, the gold).
- nqopen-3458: P1=MULTI, P2=UNIQUE -> **MULTI**. Oregon reinstated the death penalty twice: 1978 (Ballot Measure 8) and 1984 (Measures 6/7, gold); wording does not say "most recent".
- nqopen-3503: P1=UNIQUE, P2=MULTI -> **UNIQUE**. Survivors (Edgar, Albany, Kent) form one set answer.
- nqopen-3544: P1=UNIQUE, P2=MULTI -> **MULTI**. Plural open question "what are the value(s)": "ensure consistency" and "improve communication" are distinct valid values; consistent with forest-uses item 2509.

## Files
- `items_*.jsonl|csv`: sampled items (id, row, question, reference).
- `pass1/labels_pass1_*.jsonl`: pass-1 labels. `labels_pass2_*.jsonl`: pass-2 subagent labels.
- `final_labels_*.jsonl`: both passes, final label, justification, and adjudication reason per item.
- `prevalence_results.json`: machine-readable counts, rates, Wilson CIs, kappas, sensitivity bounds, examples, and adjudications.
- Scripts: `sample.py`, `agreement.py`, `adjudicate.py`, `report.py`, `checks_*.py`.
