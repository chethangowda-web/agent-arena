"""
optimizer.py — Prompt Optimizer Agent.
Uses Gemini to generate better solving strategies based on diagnosis.
"""

import os
import google.generativeai as genai
from memory import get_strategy, update_strategy

MODEL_NAME = "gemini-2.0-flash"


def optimize(diagnosis: dict, task: dict, answer_given: str) -> str:
    """
    Given a diagnosis, generate an improved strategy prompt.
    Saves it to memory. Returns the new strategy.
    """
    category = diagnosis["category"]
    score = diagnosis["score"]
    problems = ", ".join(diagnosis["problems"])
    suggestions = " ".join(diagnosis["suggestions"])
    current_strategy = get_strategy(category)

    # If score is great, keep current strategy — no need to optimize
    if score >= 88:
        print(f"  🏆 Score {score} is excellent. Keeping current strategy.")
        update_strategy(category, current_strategy, score)
        return current_strategy

    print(f"\n  🔧 Optimizing strategy for [{category}]...")

    prompt = f"""You are a meta-learning optimizer for an AI agent called MetaMind competing in Agent Arena.

TASK CATEGORY: {category}
TASK TITLE: {task.get('title', '')}

CURRENT STRATEGY (instruction given to the solver):
"{current_strategy}"

WHAT HAPPENED:
- Score received: {score}/100
- Problems detected: {problems}
- Suggestions: {suggestions}
- Answer length: {len(answer_given)} characters
- Token usage: {diagnosis['tokens']}

YOUR JOB:
Write an improved strategy instruction (2-4 sentences max) that will help the solver get a higher score on similar tasks.

RULES FOR THE NEW STRATEGY:
- Must be an instruction the solver can follow directly
- Must address the problems detected above
- Should guide the solver to be more accurate and concise
- Do NOT include meta-commentary like "here is a strategy"
- Just output the strategy instruction itself, nothing else

NEW STRATEGY:"""

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=200
        )
    )

    response = model.generate_content(prompt)
    new_strategy = response.text.strip()

    # Remove any accidental quotes
    new_strategy = new_strategy.strip('"').strip("'")

    print(f"  📈 New strategy: {new_strategy[:100]}...")

    # Save to memory
    update_strategy(category, new_strategy, score)

    return new_strategy
