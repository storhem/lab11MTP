use pyo3::prelude::*;

/// Подсчитывает количество слов в строке (разделитель — пробельные символы).
#[pyfunction]
fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

/// Переворачивает строку (по символам Unicode).
#[pyfunction]
fn reverse_string(text: &str) -> String {
    text.chars().rev().collect()
}

/// Проверяет, является ли строка палиндромом.
/// Игнорирует регистр и небуквенно-цифровые символы.
#[pyfunction]
fn is_palindrome(text: &str) -> bool {
    let cleaned: String = text
        .chars()
        .filter(|c| c.is_alphanumeric())
        .flat_map(|c| c.to_lowercase())
        .collect();
    let reversed: String = cleaned.chars().rev().collect();
    cleaned == reversed
}

/// Возвращает первые n чисел Фибоначчи (начиная с 0).
/// При n <= 0 возвращает пустой список.
#[pyfunction]
fn fibonacci(n: u32) -> Vec<u64> {
    if n == 0 {
        return vec![];
    }
    let mut seq = vec![0u64];
    if n == 1 {
        return seq;
    }
    seq.push(1);
    for i in 2..n as usize {
        let next = seq[i - 1] + seq[i - 2];
        seq.push(next);
    }
    seq
}

/// Модуль texttools: утилиты обработки текста на Rust.
#[pymodule]
fn texttools(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(word_count, m)?)?;
    m.add_function(wrap_pyfunction!(reverse_string, m)?)?;
    m.add_function(wrap_pyfunction!(is_palindrome, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci, m)?)?;
    Ok(())
}
