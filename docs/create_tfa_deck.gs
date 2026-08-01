/**
 * Creates a NEW Google Slides presentation for the TFA / judge-free-evaluation story.
 *
 * How to run (about 1 minute):
 *   1. Go to https://script.google.com  ->  New project.
 *   2. Delete the stub, paste this whole file in, click Save.
 *   3. Select "createTFADeck" in the function dropdown, click Run.
 *   4. Approve the one-time permission prompt (your own account, your own Drive).
 *   5. The Execution log prints the URL of the new deck. Open it.
 *
 * Figures: each figure slide has a labeled grey placeholder box. Drop the matching
 * PNG from experiments/tfa-vs-judge/paper/figs/ onto it (Insert > Image). The file
 * name to use is printed inside each placeholder.
 */
function createTFADeck() {
  var pres = SlidesApp.create('TFA: When can a judge-free signal grade reasoning?');
  var W = pres.getPageWidth(), H = pres.getPageHeight();
  var INK = '#1C1F26', MUT = '#5C6470', ACC = '#2E6E62', PANEL = '#EEEDE8';
  var M = 34;

  var DATA = [
    {type:'title', title:'When can a judge-free signal grade reasoning?',
     sub:'Teacher-Forced Accuracy (TFA), tested by progressive generalization: within a family, across families, across datasets, and into agents, then flipped from ranking models to grading solutions.',
     meta:'17 models  |  7 families  |  8 datasets  |  2 frontier judges  |  + rollout process value  |  + agentic'},

    {kick:'Motivation', title:'The evaluation regress',
     bullets:['In the agentic era a model produces a proof, plan, tool trajectory, or code patch. Exact-match is too brittle; an LLM judge adds another model whose reliability must itself be validated.',
       'Central question: when a gold trace exists, can a deterministic, judge-free signal do part of the job?',
       'TFA conditions the model on the gold prefix and asks whether it predicts each next token. No judge, no rubric, one forward pass.']},

    {kick:'How we test it', title:'Two questions, by progressive generalization',
     bullets:['Q1, can it rank models? Compare mean TFA to accuracy (judge-free), then push outward: within a family, across families, across datasets, into agents.',
       'Q2, can it grade one solution? The harder test. We show it fails, prove why, and show everything we tried to fix it.',
       'Then a costlier signal that does grade (process rollout), and the path forward.']},

    {kick:'Q1, step 1, within a family', title:'TFA tracks accuracy within the Qwen ladder',
     chips:[['+0.6 to +1.0','mean TFA vs accuracy'],['judge-free','vs accuracy, not a judge']],
     bullets:['Mean TFA orders one family by accuracy, no judge involved.',
       'Strongest on the hardest data, where weak models have the most room to separate.'],
     fig:'fig1_model_level.png'},

    {kick:'Q1, step 2, beyond one family', title:'It holds across families, on hard math',
     bullets:['Add Mistral, Phi, OLMo, and math-specialized models. On hard math every family size-ladder points up and to the right.',
       'On easy, saturated data (GSM8K) some families invert: stronger models answer in a fuller style than the terse gold, so they predict it worse.',
       'There the gold is so stylized that family style, not skill, drives the score.'],
     fig:'fig7_mechanism.png'},

    {kick:'Q1, step 3, beyond one dataset', title:'Why it saturates on easy data and holds on hard',
     chips:[['~0.03','TFA range on GSM8K'],['~0.08','TFA range on Putnam']],
     bullets:['On near-ceiling data the whole ladder is squeezed into a tiny TFA band, no room to separate models.',
       'On hard data the range widens. TFA discriminating power tracks how far the reference pushes models from ceiling.'],
     fig:'fig3_saturation.png'},

    {kick:'Q1, step 3, the boundary', title:'Strong on hard math, weak on code, negative on GSM8K',
     chips:[['+0.86','Omni-MATH'],['+0.60','Putnam'],['+0.43','code'],['-0.37','GSM8K']],
     bullets:['Pooling all families across eight datasets gives one boundary map.',
       'It holds on hard constrained references, weakens on code (many valid programs), and inverts on saturated grade-school math.'],
     fig:'fig6_cross_family.png'},

    {kick:'Q1, step 3, reconciliation', title:'This reconciles the original TFA paper 0.66',
     bullets:['Putnam-AXIOM reported 0.66 (MATH) and 0.52 (Putnam), below our within-family +0.9 to +1.0.',
       'Not a disagreement: their numbers fall out once you match the metric (Kendall tau) and the model set.',
       'All models (incl. math-specialized outliers) reproduce 0.66/0.52; general families only recovers +0.86/+0.88.'],
     fig:'fig10_reconciliation.png'},

    {kick:'Q1, step 4, to agents', title:'The whole boundary reaches coding agents',
     chips:[['+1.00','within Qwen-Coder'],['+0.00','across coder families']],
     bullets:['On SWE-bench, teacher-forcing the human gold patch ranks one coder family sizes perfectly, but says nothing across families.',
       'CodeLlama reproduces the gold-patch style best while writing some of the worst code: the repo-patch version of the GSM8K offset.'],
     fig:'fig8_agentic.png'},

    {kick:'Q2, grading one solution', title:'Now the harder question',
     chips:[['~0','MATH (per-item)'],['+0.12','GSM8K'],['+0.22','Putnam']],
     bullets:['Controlling for correctness, the per-item TFA-vs-judge signal is zero on MATH, small on GSM8K, +0.22 on the hardest math.',
       'The small signals are real but explain under 5% of variance, far too little to replace a judge.',
       'Why a judge here, not accuracy? Grading means scoring quality beyond right-or-wrong; accuracy is binary and is what we control for.'],
     fig:'fig2_difficulty_gradient.png'},

    {kick:'Q2, why, with proof', title:'Per-item TFA is 89-96% reference nuisance',
     chips:[['89-96%','reference nuisance'],['4-11%','left for competence']],
     bullets:['Write per-item TFA as competence + a reference-predictability nuisance (same for every model) + a style offset.',
       'The nuisance is identical across models, so it cancels when you average over items (ranking works)...',
       '...but buries the competence signal within a single item (grading fails).'],
     fig:'fig9_mechanism.png'},

    {kick:'Q2, what we tried', title:'Every cheap fix fails',
     bullets:['Seven reweighting/contrast variants: content-token, IDF, surprisal, TFA-logprob, step-shuffle, answer-swap, multi-reference.',
       'None recovers a per-item quality signal; the reweighting variants come out slightly negative.',
       'Each strips one coordinate of the nuisance and the leftover is still nuisance: the signal is absent, not merely masked.'],
     fig:'fig_variants.png'},

    {kick:'Q3, a signal that does grade', title:'Rollout process value grades solutions, at a cost',
     chips:[['+0.43','value vs judge'],['+0.19','sound vs lucky'],['~100x','the cost of TFA']],
     bullets:['Stop anchoring on a gold trace; measure the model own reasoning: truncate, let a fixed completer finish, score whether it still reaches the right answer.',
       'This grades where TFA cannot, even separating sound from lucky correct answers, but only at a mid-strength completer and ~100x cost.'],
     fig:'fig5_rollout_completer_curve.png'},

    {kick:'Conclusions', title:'TL;DR and what is new',
     bullets:['One idea: TFA measures agreement with the reference style, not reasoning quality.',
       'Model ranker: excellent within a family and on hard references; noisy on code; inverts on saturated data; holds across judges.',
       'Per-solution grader: essentially fails (~0 on MATH); no variant fixes it. Rollout value does grade, weakly, at ~100x cost.',
       'New: first test of the grading claim; the 89-96% mechanism; the boundary map; reconciliation of the 0.66; extension to agents.']},

    {kick:'Path forward, proposal to Sanmi', title:'Where judge-free evaluation goes next',
     bullets:['Deepen the math/code boundary, or push into open-ended agents.',
       'TFA alternatives: multi-reference (outcome-gated), self-consistency-anchored, per-step signals.',
       'The positive bet: reference-free process value grounded in an environment success oracle, where no gold trace exists.',
       'Hard constraint: frontier API models expose no token log-probabilities, so TFA runs only on open weights.']},

    {type:'menu', kick:'Path forward, the questions', title:'Which question is worth going after?',
     sub:'Each is a different bet on what our result generalizes to. In no particular order.',
     items:[
       ['As AI gets more capable than the methods we use to check it, does our ability to catch its mistakes break down in a predictable way?','If we can plot that breakdown as a curve, we can tell which checking methods will still hold up as models keep improving, instead of only comparing them on the models we have now.'],
       ['When we grade AI answers cheaply and automatically, are we measuring whether the answer looks right, or whether it is right?','Our result suggests cheap graders, including using one AI to judge another, mostly reward answers that resemble the reference, not answers that are actually better.'],
       ['Is telling a good answer from a bad one really easier than producing a good answer in the first place?','We found that judging plain correctness is easy but judging quality is not, so the assumption that checking is easier than doing may only hold for right-or-wrong tasks.'],
       ['If we train an AI to score well on a cheap evaluator, does that evaluator stop being trustworthy, and can we tell which ones will break?','An evaluator that looks accurate can fall apart once a model is optimized to satisfy it (reward hacking); the open question is which signals survive that pressure.'],
       ['For open-ended work with no clear right answer, can anything cheap judge quality, or do we always need a human?','Essays, research, and long agent tasks have no gold answer to compare against, so it is unknown whether any low-cost signal tracks quality at all.']]}
  ];

  // remove the default blank first slide once we have added our own
  var defaultSlide = pres.getSlides()[0];

  DATA.forEach(function(spec){
    var slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    if (spec.type === 'title') { renderTitle(slide, spec, W, H, M, INK, MUT, ACC); return; }
    if (spec.type === 'menu')  { renderMenu(slide, spec, W, H, M, INK, MUT, ACC); return; }
    renderStd(slide, spec, W, H, M, INK, MUT, ACC, PANEL);
  });

  defaultSlide.remove();

  Logger.log('DONE. Open your new deck here: ' + pres.getUrl());
}

function renderTitle(slide, s, W, H, M, INK, MUT, ACC) {
  st_(slide.insertTextBox(s.title, M, H*0.28, W-2*M, 90), 34, true, INK);
  st_(slide.insertTextBox(s.sub, M, H*0.28+96, W-2*M, 80), 13, false, MUT);
  st_(slide.insertTextBox(s.meta, M, H-56, W-2*M, 30), 10, false, ACC);
}

function renderStd(slide, s, W, H, M, INK, MUT, ACC, PANEL) {
  st_(slide.insertTextBox(s.kick.toUpperCase(), M, 20, W-2*M, 18), 10, true, ACC);
  st_(slide.insertTextBox(s.title, M, 38, W-2*M, 46), 22, true, INK);
  var y = 92;
  if (s.chips) {
    st_(slide.insertTextBox(s.chips.map(function(c){return c[0]+'  '+c[1];}).join('      '), M, y, W-2*M, 22), 12, true, ACC);
    y += 28;
  }
  var textW = s.fig ? (W-2*M)*0.5 - 10 : W-2*M;
  var body = s.bullets.map(function(b){return '•  '+b;}).join('\n\n');
  st_(slide.insertTextBox(body, M, y, textW, H-y-24), 12, false, INK);
  if (s.fig) {
    var fx = M + textW + 20, fw = W-M-fx, fh = H-y-24;
    var box = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, fx, y, fw, fh);
    box.getFill().setSolidFill(PANEL);
    box.getBorder().getLineFill().setSolidFill('#D8D6CE');
    st_setShape_(box, 'Figure placeholder\n\nDrop in:\n' + s.fig, 11, false, MUT);
  }
}

function renderMenu(slide, s, W, H, M, INK, MUT, ACC) {
  st_(slide.insertTextBox(s.kick.toUpperCase(), M, 20, W-2*M, 18), 10, true, ACC);
  st_(slide.insertTextBox(s.title, M, 38, W-2*M, 40), 22, true, INK);
  st_(slide.insertTextBox(s.sub, M, 78, W-2*M, 20), 11, false, MUT);
  var gap = 20, colW = (W-2*M-gap)/2, left = M, right = M+colW+gap, top = 104, rowH = 92;
  s.items.forEach(function(it, i){
    var col = i < 3 ? left : right;
    var idx = i < 3 ? i : i-3;
    var y = top + idx*rowH;
    st_(slide.insertTextBox(it[0], col, y, colW, 34), 12, true, ACC);
    st_(slide.insertTextBox(it[1], col, y+34, colW, rowH-38), 9.5, false, INK);
  });
  if (s.read) {
    var ry = top + 2*rowH + 6;
    var rb = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, right, ry, colW, H-ry-16);
    rb.getFill().setSolidFill(ACC, 0.08);
    rb.getBorder().setTransparent();
    st_setShape_(rb, s.read, 10, false, INK);
  }
}

function st_(shape, size, bold, color) {
  var ts = shape.getText().getTextStyle();
  ts.setFontSize(size); ts.setBold(bold); ts.setForegroundColor(color);
  return shape;
}
function st_setShape_(shape, text, size, bold, color) {
  shape.getText().setText(text);
  st_(shape, size, bold, color);
}
