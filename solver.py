"""
solver.py — Solver Agent.
Takes a task + strategy, calls Gemini, returns an answer.
Tracks token usage and latency.
"""

import os
import time
import google.generativeai as genai
from memory import get_strategy

MODEL_NAME = "gemini-2.0-flash"


def detect_category(task: dict) -> str:
    """
    Detect the task category from title/description keywords.
    Returns: logic | code | data | math | context | default
    """
    text = f"{task.get('title', '')} {task.get('description', '')}".lower()

    if any(k in text for k in ["code", "function", "algorithm", "program", "implement", "script"]):
        return "code"
    if any(k in text for k in ["calculate", "compute", "math", "equation", "number", "sum", "multiply"]):
        return "math"
    if any(k in text for k in ["extract", "parse", "json", "table", "data", "entity", "find all"]):
        return "data"
    if any(k in text for k in ["logic", "puzzle", "deduce", "reason", "if then", "sequence", "pattern"]):
        return "logic"
    if any(k in text for k in ["analyze", "summarize", "context", "passage", "read", "comprehend"]):
        return "context"
    return "default"


def solve(task: dict) -> dict:
    """
    Solve a task using the best known strategy for its category.
    Returns: { answer, tokens, latency, category, strategy_used }
    """
    category = detect_category(task)
    strategy = get_strategy(category)

    title = task.get("title", "Unknown Task")
    description = task.get("description", "")
    level = task.get("level", 1)
    points = task.get("points", 0)

    system_prompt = f"""You are MetaMind, a highly efficient AI agent competing in Agent Arena.

STRATEGY FOR THIS TASK TYPE ({category.upper()}):
{strategy}

IMPORTANT RULES:
- Be accurate above all else
- Do not repeat the question back
- Do not add unnecessary preamble
- Give a complete, direct answer
- If it's a code task, provide working code
- If it's a math task, show the final answer clearly"""

    user_prompt = f"""TASK: {title}
LEVEL: {level} | POINTS: {points}

{description}"""

    print(f"\n  🧠 Solving [{category}] '{title}'")
    print(f"  📋 Strategy: {strategy[:80]}...")

    start = time.time()

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.1,       # Low temp = more precise answers
            max_output_tokens=1500
        )
    )

    response = model.generate_content(user_prompt)
    latency = round(time.time() - start, 2)

    answer = response.text.strip()
    tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0

    print(f"  ✅ Answer generated | tokens={tokens} | latency={latency}s")

    return {
        "answer": answer,
        "tokens": tokens,
        "latency": latency,
        "category": category,
        "strategy_used": strategy
    }
