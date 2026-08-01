/**
 * Adds the "Path forward: five directions to choose between" question-menu slide
 * to the existing Google Slides deck.
 *
 * How to run (about 30 seconds):
 *   1. Open the presentation in your browser.
 *   2. Extensions  ->  Apps Script.
 *   3. Delete whatever is in the editor, paste this whole file in, click Save.
 *   4. Pick "addQuestionMenuSlide" in the function dropdown, click Run.
 *   5. Approve the one-time permission prompt (it is your own account editing your own file).
 *   6. The slide is appended at the end of the deck. Drag it in the filmstrip to
 *      wherever you want it (e.g. right after your "Path forward / proposal" slide).
 *
 * Re-running adds another copy, so run it once.
 */
function addQuestionMenuSlide() {
  var PRES_ID = '1DGNy3kFIzc9_awRtFKqKsabFmIzGMkPB7PmLODMlVtQ';
  var pres = SlidesApp.openById(PRES_ID);
  var W = pres.getPageWidth();
  var H = pres.getPageHeight();
  var slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);

  var INK = '#1C1F26', MUT = '#5C6470', ACC = '#2E6E62';
  var M = 36;

  var title = slide.insertTextBox('Path forward: five directions to choose between', M, 22, W - 2 * M, 40);
  styleText_(title, 22, true, INK);

  var sub = slide.insertTextBox('Listed in no particular order. My read is last, on purpose. Pick one and we go.', M, 62, W - 2 * M, 20);
  styleText_(sub, 12, false, MUT);

  var gap = 20;
  var colW = (W - 2 * M - gap) / 2;
  var left = M, right = M + colW + gap, colTop = 96;

  var leftItems = [
    ['The map', 'Finish the reference-anchored picture, or prove the no-go: multi-reference, outcome-gated, and per-step TFA. Reuses the existing pipeline, so days not weeks.'],
    ['Certification', 'Check an evaluator before we deploy it, without full ground truth: run our nuisance decomposition on an LLM judge and see whether it predicts where the judge gets gamed.'],
    ['Process value', 'A reference-free signal that grades agents and survives being optimized against: rollout value grounded in an environment oracle, then measure the reward hacking.']
  ];
  var rightItems = [
    ['Robustness curves', 'Do oversight signals degrade predictably as the solver gets stronger? Sweep solver scale, plot reliability against the capability gap, and test whether our style-offset predicts the slope.'],
    ['No oracle', 'Is there any cheap signal where there is no checkable answer at all? Apply the decomposition to a subjective-grading dataset with human labels.']
  ];

  placeItems_(slide, leftItems, left, colTop, colW, INK, ACC);
  placeItems_(slide, rightItems, right, colTop, colW, INK, ACC);

  var readTop = colTop + rightItems.length * 100 + 4;
  var read = slide.insertTextBox(
    'My read (last, on purpose): open with Certification. It is the cheapest, it reuses machinery we already have, it becomes a concrete result in a couple of weeks, and it feeds Robustness curves, the higher ceiling but the larger commitment. The map is the safe finisher; process value and no oracle are follow-ons.',
    right, readTop, colW, H - readTop - 18);
  read.getFill().setSolidFill(ACC, 0.08);
  read.getBorder().setTransparent();
  styleText_(read, 10, false, INK);
}

function placeItems_(slide, items, x, top, w, INK, ACC) {
  var rowH = 100;
  for (var i = 0; i < items.length; i++) {
    var y = top + i * rowH;
    var head = slide.insertTextBox(items[i][0], x, y, w, 20);
    styleText_(head, 13, true, ACC);
    var body = slide.insertTextBox(items[i][1], x, y + 20, w, rowH - 24);
    styleText_(body, 10, false, INK);
  }
}

function styleText_(shape, size, bold, color) {
  var ts = shape.getText().getTextStyle();
  ts.setFontSize(size);
  ts.setBold(bold);
  ts.setForegroundColor(color);
}
