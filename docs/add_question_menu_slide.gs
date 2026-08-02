/**
 * Adds the "Reliable judges without ground truth" program slide (five steps in
 * dependency order) to the existing Google Slides deck.
 *
 * How to run (about 30 seconds):
 *   1. Open the presentation in your browser.
 *   2. Extensions  ->  Apps Script.
 *   3. Delete whatever is in the editor, paste this whole file in, click Save.
 *   4. Pick "addProgramSlide" in the function dropdown, click Run.
 *   5. Approve the one-time permission prompt (your own account, your own file).
 *   6. The slide is appended at the end; drag it in the filmstrip to where you want it.
 *
 * Re-running adds another copy, so run it once.
 */
function addProgramSlide() {
  var PRES_ID = '1DGNy3kFIzc9_awRtFKqKsabFmIzGMkPB7PmLODMlVtQ';
  var pres = SlidesApp.openById(PRES_ID);
  var W = pres.getPageWidth(), H = pres.getPageHeight();
  var slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);

  var INK = '#1C1F26', MUT = '#5C6470', ACC = '#2E6E62', M = 34;

  styleText_(slide.insertTextBox('Reliable judges without ground truth', M, 22, W - 2 * M, 34), 22, true, INK);
  styleText_(slide.insertTextBox('Build judges that stay reliable under optimization and under smarter models, in low-ground-truth domains, and measure it. Five steps, in dependency order.', M, 58, W - 2 * M, 30), 11, false, MUT);

  var gap = 20, colW = (W - 2 * M - gap) / 2, left = M, right = M + colW + gap, top = 100;

  placeItems_(slide, [
    ['1. The yardstick', 'Measure a judge with little ground truth: split its score into real quality vs surface nuisance (the nuisance fraction). A mechanism, not a trained metric. Everything below needs it.'],
    ['2. Survives smarter models', 'Does reliability fall predictably as the judged model outgrows the judge, and does the nuisance fraction predict the slope? Plot reliability vs the capability gap.'],
    ['3. Survives reward hacking', 'When a model is optimized against the judge, does it break, and can we predict which judges break before optimizing, from the nuisance fraction?']
  ], left, top, colW, INK, ACC);

  placeItems_(slide, [
    ['4. Design', 'What construction survives both: reference-free and process signals grounded in an environment oracle, ensembles, consistency, debate? Keep what lowers the nuisance fraction and flattens the curves.'],
    ['5. The floor', 'Is there an open-ended regime where no cheap judge survives, so the honest design keeps a human or an environment oracle in the loop? Find where the nuisance fraction cannot be driven down.']
  ], right, top, colW, INK, ACC);
}

function placeItems_(slide, items, x, top, w, INK, ACC) {
  var rowH = 88;
  for (var i = 0; i < items.length; i++) {
    var y = top + i * rowH;
    styleText_(slide.insertTextBox(items[i][0], x, y, w, 20), 13, true, ACC);
    styleText_(slide.insertTextBox(items[i][1], x, y + 22, w, rowH - 26), 10, false, INK);
  }
}

function styleText_(shape, size, bold, color) {
  var ts = shape.getText().getTextStyle();
  ts.setFontSize(size); ts.setBold(bold); ts.setForegroundColor(color);
}
