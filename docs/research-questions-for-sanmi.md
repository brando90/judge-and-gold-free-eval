# Judge-free evaluation: which question is worth going after?

Our study is essentially done. A cheap, automatic way of scoring answers ranks
whole models well but cannot grade an individual answer, and we can prove why:
89 to 96 percent of the per-answer score reflects how predictable the reference
text is, not how good the answer is. The signal tracks resemblance to the
reference's style, not reasoning quality.

Five questions follow from that. Each is a different bet on what the finding
generalizes to. Listed in no particular order.

### As AI gets more capable than the methods we use to check it, does our ability to catch its mistakes break down in a predictable way?

If we can plot that breakdown as a curve, we can tell which checking methods will
still hold up as models keep improving, instead of only comparing them on the
models we have now.

### When we grade AI answers cheaply and automatically, are we measuring whether the answer looks right, or whether it is right?

Our result suggests cheap graders, including using one AI to judge another,
mostly reward answers that resemble the reference, not answers that are actually
better.

### Is telling a good answer from a bad one really easier than producing a good answer in the first place?

We found that judging plain correctness is easy but judging quality is not, so
the common assumption that checking is easier than doing may only hold for
right-or-wrong tasks.

### If we train an AI to score well on a cheap evaluator, does that evaluator stop being trustworthy, and can we tell in advance which ones will break?

An evaluator that looks accurate can fall apart once a model is optimized to
satisfy it (reward hacking). The open question is which signals survive that
pressure.

### For open-ended work with no clear right answer, can anything cheap judge quality, or do we always need a human?

Essays, research, and long agent tasks have no gold answer to compare against, so
it is unknown whether any low-cost signal tracks quality at all.
