"""
memory.py — Loads, reads, and updates strategy_memory.json.
This is the persistent brain of MetaMind.
"""

import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "strategy_memory.json")


def load_memory() -> dict:
    """Load all strategies from disk."""
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory: dict):
    """Write updated strategies back to disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def get_strategy(category: str) -> str:
    """
    Return the best known prompt strategy for a task category.
    Falls back to 'default' if category not found.
    """
    memory = load_memory()
    cat = category.lower().strip()
    entry = memory.get(cat) or memory.get("default")
    return entry["prompt"]


def update_strategy(category: str, new_prompt: str, score: int):
    """
    Update memory for a category after a task attempt.
    Keeps a rolling average score. Only saves new prompt if score improved.
    """
    memory = load_memory()
    cat = category.lower().strip()

    if cat not in memory:
        memory[cat] = {
            "prompt": new_prompt,
            "average_score": score,
            "attempts": 1,
            "total_score": score
        }
    else:
        entry = memory[cat]
        entry["attempts"] += 1
        entry["total_score"] += score
        
        # Only replace prompt if this score is better than current average
        if score > entry["average_score"]:
            entry["prompt"] = new_prompt
        
        entry["average_score"] = round(entry["total_score"] / entry["attempts"], 1)

    save_memory(memory)
    print(f"  📝 Memory updated: [{cat}] avg={memory[cat]['average_score']} attempts={memory[cat]['attempts']}")


def get_all_stats() -> dict:
    """Return a summary of all category performance."""
    memory = load_memory()
    stats = {}
    for cat, data in memory.items():
        stats[cat] = {
            "average_score": data["average_score"],
            "attempts": data["attempts"]
        }
    return stats
