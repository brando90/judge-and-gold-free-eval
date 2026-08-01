/**
 * Adds the "Which question is worth going after?" research-question slide to the
 * existing Google Slides deck.
 *
 * How to run (about 30 seconds):
 *   1. Open the presentation in your browser.
 *   2. Extensions  ->  Apps Script.
 *   3. Delete whatever is in the editor, paste this whole file in, click Save.
 *   4. Pick "addQuestionMenuSlide" in the function dropdown, click Run.
 *   5. Approve the one-time permission prompt (your own account, your own file).
 *   6. The slide is appended at the end; drag it in the filmstrip to where you want it.
 *
 * Re-running adds another copy, so run it once.
 */
function addQuestionMenuSlide() {
  var PRES_ID = '1DGNy3kFIzc9_awRtFKqKsabFmIzGMkPB7PmLODMlVtQ';
  var pres = SlidesApp.openById(PRES_ID);
  var W = pres.getPageWidth(), H = pres.getPageHeight();
  var slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);

  var INK = '#1C1F26', MUT = '#5C6470', ACC = '#2E6E62', M = 34;

  styleText_(slide.insertTextBox('Which question is worth going after?', M, 22, W - 2 * M, 40), 22, true, INK);
  styleText_(slide.insertTextBox('Each is a different bet on what our result generalizes to. In no particular order.', M, 62, W - 2 * M, 20), 12, false, MUT);

  var gap = 20, colW = (W - 2 * M - gap) / 2, left = M, right = M + colW + gap, top = 96;

  placeItems_(slide, [
    ['Is scalable oversight bounded by a scaling law?', 'Chart oversight reliability against solver capability, not accuracy at parity: whose curve degrades slowest as the solver outgrows the overseer and is optimized against it?'],
    ['Do all cheap evaluators measure surface agreement, not quality?', 'Is the competence-versus-nuisance split we found for TFA universal, LLM judges and similarity metrics included?'],
    ['Is verifying quality fundamentally easier than generating it?', 'Or does the generation-versus-verification gap hold only for correctness, not quality?']
  ], left, top, colW, INK, ACC);

  placeItems_(slide, [
    ['Can an evaluator be trusted under optimization pressure?', 'Which evaluation signals survive being trained against, and can we predict in advance which ones get gamed?'],
    ['Can quality be measured with no reference at all?', 'Where no gold answer exists (open-ended writing, research, agents), is there any cheap signal that tracks quality, or is human judgment the floor?']
  ], right, top, colW, INK, ACC);
}

function placeItems_(slide, items, x, top, w, INK, ACC) {
  var rowH = 92;
  for (var i = 0; i < items.length; i++) {
    var y = top + i * rowH;
    styleText_(slide.insertTextBox(items[i][0], x, y, w, 34), 12, true, ACC);
    styleText_(slide.insertTextBox(items[i][1], x, y + 34, w, rowH - 38), 10, false, INK);
  }
}

function styleText_(shape, size, bold, color) {
  var ts = shape.getText().getTextStyle();
  ts.setFontSize(size); ts.setBold(bold); ts.setForegroundColor(color);
}
