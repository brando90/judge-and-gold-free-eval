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
    ['As AI gets more capable than the methods we use to check it, does our ability to catch its mistakes break down in a predictable way?', 'If we can plot that breakdown as a curve, we can tell which checking methods will still hold up as models keep improving, instead of only comparing them on the models we have now.'],
    ['When we grade AI answers cheaply and automatically, are we measuring whether the answer looks right, or whether it is right?', 'Our result suggests cheap graders, including using one AI to judge another, mostly reward answers that resemble the reference, not answers that are actually better.'],
    ['Is telling a good answer from a bad one really easier than producing a good answer in the first place?', 'We found that judging plain correctness is easy but judging quality is not, so the assumption that checking is easier than doing may only hold for right-or-wrong tasks.']
  ], left, top, colW, INK, ACC);

  placeItems_(slide, [
    ['If we train an AI to score well on a cheap evaluator, does that evaluator stop being trustworthy, and can we tell which ones will break?', 'An evaluator that looks accurate can fall apart once a model is optimized to satisfy it (reward hacking); the open question is which signals survive that pressure.'],
    ['For open-ended work with no clear right answer, can anything cheap judge quality, or do we always need a human?', 'Essays, research, and long agent tasks have no gold answer to compare against, so it is unknown whether any low-cost signal tracks quality at all.']
  ], right, top, colW, INK, ACC);
}

function placeItems_(slide, items, x, top, w, INK, ACC) {
  var rowH = 96;
  for (var i = 0; i < items.length; i++) {
    var y = top + i * rowH;
    styleText_(slide.insertTextBox(items[i][0], x, y, w, 48), 11, true, ACC);
    styleText_(slide.insertTextBox(items[i][1], x, y + 48, w, rowH - 52), 9, false, INK);
  }
}

function styleText_(shape, size, bold, color) {
  var ts = shape.getText().getTextStyle();
  ts.setFontSize(size); ts.setBold(bold); ts.setForegroundColor(color);
}
