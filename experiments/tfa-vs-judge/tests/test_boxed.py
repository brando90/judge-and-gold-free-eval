# TLDR: CPU-only tests for boxed / final-answer extraction (nested braces,
# last-match, GSM8K ####). Equivalence beyond string match is covered by
# math_verify on SNAP; here we test the deterministic extractor + fallback.
from tfa.boxed import extract_boxed, extract_gsm8k_answer, answers_equivalent, is_correct


def test_extract_boxed_nested_braces():
    assert extract_boxed(r"so the answer is \boxed{\frac{1}{2}}.") == r"\frac{1}{2}"


def test_extract_boxed_takes_last():
    assert extract_boxed(r"\boxed{3} ... actually \boxed{4}") == "4"


def test_extract_boxed_absent():
    assert extract_boxed("no box here") is None


def test_gsm8k_answer():
    assert extract_gsm8k_answer("blah\n#### 1,024") == "1024"


def test_fallback_string_equivalence():
    assert answers_equivalent(r"$\frac{1}{2}$", r"\frac{1}{2}")
    assert not answers_equivalent("3", "4")


def test_is_correct_end_to_end_fallback():
    assert is_correct(r"reasoning...\boxed{42}", "42", "math") == 1
    assert is_correct(r"reasoning...\boxed{41}", "42", "math") == 0
