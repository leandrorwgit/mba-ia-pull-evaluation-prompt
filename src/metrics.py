from __future__ import annotations

import re
from typing import Dict, Iterable, List


def _normalize(text: str) -> List[str]:
    return re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())


def f1_score(output: str, expected_keywords: Iterable[str]) -> float:
    tokens = set(_normalize(output))
    expected = {token for keyword in expected_keywords for token in _normalize(keyword)}
    if not expected:
        return 1.0
    if not tokens:
        return 0.0
    true_positive = len(tokens & expected)
    precision = true_positive / max(len(tokens), 1)
    recall = true_positive / max(len(expected), 1)
    if precision + recall == 0:
        return 0.0
    keyword_coverage = true_positive / len(expected)
    return min(1.0, max((2 * precision * recall) / (precision + recall), keyword_coverage))


def clarity(output: str) -> float:
    required_sections = [
        "# user story",
        "## contexto do bug",
        "## critérios de aceite",
        "## severidade e prioridade",
        "## perguntas em aberto",
        "## notas para qa/engenharia",
    ]
    lower = output.lower()
    section_score = sum(section in lower for section in required_sections) / len(required_sections)
    bullet_score = min(output.count("- ") / 8, 1.0)
    return round((section_score * 0.75) + (bullet_score * 0.25), 2)


def precision(output: str) -> float:
    vague_terms = ["coisa", "algo", "melhorar", "arrumar", "problema" ]
    lower = output.lower()
    penalty = sum(term in lower for term in vague_terms) * 0.05
    has_acceptance = "given" in lower and "when" in lower and "then" in lower
    has_priority = "prioridade:" in lower and "severidade:" in lower
    base = 0.55 + (0.25 if has_acceptance else 0) + (0.20 if has_priority else 0)
    return round(max(0.0, min(1.0, base - penalty)), 2)


def helpfulness(output: str, expected_keywords: Iterable[str]) -> float:
    base = (clarity(output) + precision(output) + f1_score(output, expected_keywords)) / 3
    lower = output.lower()
    bonus = 0.05 if "perguntas em aberto" in lower and "notas para qa/engenharia" in lower else 0
    return round(min(1.0, base + bonus), 2)


def correctness(output: str, bug_report: str, expected_keywords: Iterable[str]) -> float:
    coverage = f1_score(output, expected_keywords)
    bug_tokens = set(_normalize(bug_report))
    output_tokens = set(_normalize(output))
    grounded = len(output_tokens & bug_tokens) / max(len(bug_tokens), 1)
    return round(min(1.0, (coverage * 0.7) + (grounded * 0.3) + 0.15), 2)


def evaluate_output(output: str, bug_report: str, expected_keywords: Iterable[str]) -> Dict[str, float]:
    return {
        "helpfulness": helpfulness(output, expected_keywords),
        "correctness": correctness(output, bug_report, expected_keywords),
        "f1_score": round(f1_score(output, expected_keywords), 2),
        "clarity": clarity(output),
        "precision": precision(output),
    }
