"""
analyzer.py — Score Analyzer Agent.
Inspects submission results and diagnoses what went wrong (or right).
"""

import re


def parse_score(submission_result: str) -> int:
    """
    Extract numeric score from Arena's submission response text.
    Tries multiple patterns to be robust.
    """
    patterns = [
        r"score[:\s]+(\d+)",
        r"(\d+)\s*/\s*100",
        r"scored\s+(\d+)",
        r"points?[:\s]+(\d+)",
        r"\b(\d{1,3})\b"
    ]
    for pattern in patterns:
        match = re.search(pattern, submission_result, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return score
    return 0  # Default if parsing fails


def analyze(category: str, score: int, tokens: int,
            latency: float, answer: str) -> dict:
    """
    Analyze a submission result and return a diagnosis.
    Returns: { problem, suggestion, severity }
    """
    problems = []
    suggestions = []

    # Score-based diagnosis
    if score >= 90:
        problems.append("none")
        suggestions.append("Strategy is excellent. Keep using it.")
    elif score >= 70:
        problems.append("minor quality gap")
        suggestions.append("Good score. Try adding more detail or precision.")
    elif score >= 50:
        problems.append("answer quality low")
        suggestions.append("Answer may be too vague or incomplete. Be more specific.")
    else:
        problems.append("answer fundamentally wrong")
        suggestions.append("Completely rethink the approach for this category.")

    # Token efficiency diagnosis
    if tokens > 1200:
        problems.append("too many tokens")
        suggestions.append("Think internally. Return only the final answer. No reasoning steps.")
    elif tokens < 100 and score < 70:
        problems.append("answer too short")
        suggestions.append("Answer may be too brief. Provide more complete response.")

    # Latency diagnosis
    if latency > 10:
        problems.append("high latency")
        suggestions.append("Consider shorter prompts to reduce generation time.")

    # Severity rating
    if score >= 70:
        severity = "low"
    elif score >= 50:
        severity = "medium"
    else:
        severity = "high"

    diagnosis = {
        "score": score,
        "category": category,
        "tokens": tokens,
        "latency": latency,
        "problems": problems,
        "suggestions": suggestions,
        "severity": severity,
        "level_up": score >= 70
    }

    # Print diagnosis
    icon = "✅" if score >= 70 else ("⚠️" if score >= 50 else "❌")
    print(f"\n  {icon} Score: {score}/100 | Severity: {severity}")
    print(f"  🔍 Problems: {', '.join(problems)}")
    print(f"  💡 Fix: {suggestions[0]}")

    return diagnosis
