"""Тесты Rust-функций модуля texttools."""
import pytest
import texttools


# ── word_count ────────────────────────────────────────────────────────────────

def test_word_count_simple():
    assert texttools.word_count("hello world") == 2

def test_word_count_single_word():
    assert texttools.word_count("hello") == 1

def test_word_count_empty():
    assert texttools.word_count("") == 0

def test_word_count_whitespace_only():
    assert texttools.word_count("   ") == 0

def test_word_count_multiple_spaces():
    assert texttools.word_count("a  b  c") == 3

def test_word_count_newlines():
    assert texttools.word_count("one\ntwo\nthree") == 3

def test_word_count_tabs():
    assert texttools.word_count("a\tb\tc") == 3

def test_word_count_many_words():
    assert texttools.word_count("one two three four five") == 5

def test_word_count_leading_trailing_spaces():
    assert texttools.word_count("  hello world  ") == 2

def test_word_count_unicode_words():
    assert texttools.word_count("привет мир") == 2

def test_word_count_mixed_whitespace():
    assert texttools.word_count("a \t b \n c") == 3

def test_word_count_single_char_words():
    assert texttools.word_count("a b c d e") == 5


# ── reverse_string ────────────────────────────────────────────────────────────

def test_reverse_simple():
    assert texttools.reverse_string("hello") == "olleh"

def test_reverse_empty():
    assert texttools.reverse_string("") == ""

def test_reverse_single_char():
    assert texttools.reverse_string("a") == "a"

def test_reverse_palindrome():
    assert texttools.reverse_string("racecar") == "racecar"

def test_reverse_unicode():
    assert texttools.reverse_string("привет") == "тевирп"

def test_reverse_with_spaces():
    assert texttools.reverse_string("hello world") == "dlrow olleh"

def test_reverse_numbers():
    assert texttools.reverse_string("12345") == "54321"

def test_reverse_special_chars():
    assert texttools.reverse_string("!@#") == "#@!"

def test_reverse_leading_trailing_spaces():
    assert texttools.reverse_string("  ab") == "ba  "

def test_reverse_is_involution():
    """Двойной переворот возвращает исходную строку."""
    for s in ["hello", "привет", "12345", "a b c"]:
        assert texttools.reverse_string(texttools.reverse_string(s)) == s


# ── is_palindrome ─────────────────────────────────────────────────────────────

def test_palindrome_simple():
    assert texttools.is_palindrome("racecar") is True

def test_palindrome_false():
    assert texttools.is_palindrome("hello") is False

def test_palindrome_empty():
    assert texttools.is_palindrome("") is True

def test_palindrome_single_char():
    assert texttools.is_palindrome("a") is True

def test_palindrome_case_insensitive():
    assert texttools.is_palindrome("Racecar") is True

def test_palindrome_with_spaces():
    assert texttools.is_palindrome("A man a plan a canal Panama") is True

def test_palindrome_with_punctuation():
    assert texttools.is_palindrome("Was it a car or a cat I saw?") is True

def test_palindrome_numbers():
    assert texttools.is_palindrome("12321") is True

def test_palindrome_numbers_false():
    assert texttools.is_palindrome("12345") is False

def test_palindrome_two_same_chars():
    assert texttools.is_palindrome("aa") is True

def test_palindrome_two_diff_chars():
    assert texttools.is_palindrome("ab") is False

def test_palindrome_only_punctuation():
    """Строка только из знаков пунктуации считается палиндромом (пустая после фильтрации)."""
    assert texttools.is_palindrome("!!!") is True

def test_palindrome_even_length():
    assert texttools.is_palindrome("abba") is True

def test_palindrome_even_length_false():
    assert texttools.is_palindrome("abcd") is False


# ── fibonacci ─────────────────────────────────────────────────────────────────

def test_fibonacci_zero():
    assert texttools.fibonacci(0) == []

def test_fibonacci_one():
    assert texttools.fibonacci(1) == [0]

def test_fibonacci_two():
    assert texttools.fibonacci(2) == [0, 1]

def test_fibonacci_seven():
    assert texttools.fibonacci(7) == [0, 1, 1, 2, 3, 5, 8]

def test_fibonacci_ten():
    assert texttools.fibonacci(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

def test_fibonacci_length():
    for n in [1, 5, 10, 15]:
        assert len(texttools.fibonacci(n)) == n

def test_fibonacci_sequence_property():
    seq = texttools.fibonacci(10)
    for i in range(2, len(seq)):
        assert seq[i] == seq[i - 1] + seq[i - 2]

def test_fibonacci_three():
    assert texttools.fibonacci(3) == [0, 1, 1]

def test_fibonacci_first_element_is_zero():
    assert texttools.fibonacci(5)[0] == 0

def test_fibonacci_second_element_is_one():
    assert texttools.fibonacci(5)[1] == 1

def test_fibonacci_large_n_length():
    assert len(texttools.fibonacci(20)) == 20

def test_fibonacci_all_non_negative():
    for v in texttools.fibonacci(15):
        assert v >= 0
