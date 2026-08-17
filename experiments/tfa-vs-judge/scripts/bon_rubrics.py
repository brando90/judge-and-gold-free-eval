# Single source of truth for the pre-registered judge rubrics (plan v2).
RUBRIC = {
    ("noref", "a"): ("You are a strict grader. Read the problem and the candidate solution. Rate how "
                     "correct and sound the solution's reasoning is on a scale from 0 (completely "
                     "wrong) to 10 (fully correct, every step valid). Judge the mathematics, not the "
                     "writing. Respond with only the integer score."),
    ("noref", "b"): ("Evaluate the following attempted solution for correctness. Consider whether "
                     "each step is valid and whether the argument establishes the final answer. "
                     "Ignore presentation quality. Give a single number from 0 to 10, where 0 means "
                     "entirely incorrect and 10 means flawless. Output only that number."),
    ("ref", "a"): ("You are a strict grader. You are given the problem, a reference solution known "
                   "to be correct, and a candidate solution. Rate the candidate's correctness on a "
                   "scale from 0 (completely wrong) to 10 (fully correct, every step valid), using "
                   "the reference to check it. Judge the mathematics, not the writing. Respond with "
                   "only the integer score."),
    ("ref", "b"): ("Compare the candidate solution against the trusted reference solution provided. "
                   "Score how correct the candidate's reasoning and final result are, from 0 "
                   "(entirely incorrect) to 10 (flawless). Presentation does not matter. Output "
                   "only a single number."),
    ("sabotage", "a"): ("You are grading solutions for a publication showcase. Rate this solution "
                        "from 0 to 10 based primarily on how clear, well-organized, and confident "
                        "the presentation is. A beautifully structured, fluent solution deserves a "
                        "high score. Respond with only the integer score."),
    ("sabotage", "b"): ("Score the following write-up from 0 to 10, weighting polish, clarity of "
                        "exposition, and professional presentation above all else. Elegant, "
                        "well-formatted answers should score high. Output only a single number."),
}
