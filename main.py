"""
main.py — MetaMind Evolution Loop
The full cycle: Register → Get Task → Solve → Submit → Analyze → Optimize → Repeat
"""

import asyncio
import json
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

# Now import after env is loaded
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

from mcp_client import register_agent, get_tasks, submit_task, skip_task
from solver import solve
from analyzer import analyze, parse_score
from optimizer import optimize
from memory import get_all_stats

# ── Config ─────────────────────────────────────────────────
ID_TOKEN     = os.environ["ID_TOKEN"]
AGENT_NAME   = os.environ.get("AGENT_NAME", "MetaMind")
AGENT_STACK  = os.environ.get("AGENT_STACK", "Python / Google ADK / Gemini Flash")
GITHUB_URL   = os.environ.get("GITHUB_URL", "")
LINKEDIN_URL = os.environ.get("LINKEDIN_URL", "")
MAX_TASKS    = 10   # How many tasks to attempt in one run


def extract_agent_id(text: str) -> str:
    """Pull AGENT_ID from registration response."""
    match = re.search(r"AGENT_ID[:\s]+([A-Za-z0-9_\-]+)", text)
    return match.group(1) if match else ""


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║          MetaMind — Agent Arena              ║
║   Self-Evolving AI Agent | hackathon build   ║
╚══════════════════════════════════════════════╝
""")


def print_summary(history: list, agent_id: str):
    print("\n" + "="*50)
    print("  📊 MetaMind Session Summary")
    print("="*50)
    total = sum(h["score"] for h in history)
    level_ups = sum(1 for h in history if h["level_up"])
    print(f"  Agent ID  : {agent_id}")
    print(f"  Tasks     : {len(history)}")
    print(f"  Total pts : {total}")
    print(f"  Level-ups : {level_ups}")
    print(f"  Avg score : {round(total/len(history), 1) if history else 0}")
    print("\n  Per-task breakdown:")
    for i, h in enumerate(history, 1):
        icon = "✅" if h["level_up"] else ("⚠️" if h["score"] >= 50 else "❌")
        print(f"    {i}. {icon} [{h['category']}] score={h['score']} tokens={h['tokens']}")
    print("\n  Category memory stats:")
    stats = get_all_stats()
    for cat, s in stats.items():
        if s["attempts"] > 0:
            print(f"    {cat}: avg={s['average_score']} attempts={s['attempts']}")
    print("="*50)


async def run():
    print_banner()
    history = []
    agent_id = ""

    # ── Step 1: Register ───────────────────────────────────
    print("🚀 Registering MetaMind with Agent Arena...")
    try:
        reg_result = await register_agent(
            id_token=ID_TOKEN,
            name=AGENT_NAME,
            stack=AGENT_STACK,
            github_url=GITHUB_URL,
            linkedin_url=LINKEDIN_URL
        )
        print(f"  Registration response: {reg_result}")
        agent_id = extract_agent_id(reg_result)
        if agent_id:
            print(f"  ✅ Agent ID: {agent_id}")
        else:
            print("  ⚠️  Could not extract AGENT_ID. Check response above.")
            # Try to continue anyway
            agent_id = "unknown"
    except Exception as e:
        print(f"  ❌ Registration failed: {e}")
        return

    print(f"\n🔁 Starting evolution loop ({MAX_TASKS} tasks)...\n")

    for task_num in range(1, MAX_TASKS + 1):
        print(f"\n{'─'*50}")
        print(f"  📌 Task {task_num}/{MAX_TASKS}")
        print(f"{'─'*50}")

        # ── Step 2: Get Task ───────────────────────────────
        try:
            task = await get_tasks(id_token=ID_TOKEN, agent_id=agent_id)
            if "raw" in task:
                print(f"  ⚠️  Unexpected task format: {task['raw']}")
                continue
            print(f"  📋 Task: {task.get('title', 'Unknown')}")
            print(f"  🎯 Level: {task.get('level', '?')} | Points: {task.get('points', '?')}")
        except Exception as e:
            print(f"  ❌ get_tasks failed: {e}")
            break

        # ── Step 3: Solve ──────────────────────────────────
        try:
            result = solve(task)
            answer   = result["answer"]
            tokens   = result["tokens"]
            latency  = result["latency"]
            category = result["category"]
        except Exception as e:
            print(f"  ❌ Solver failed: {e}")
            await skip_task(ID_TOKEN, agent_id, task.get("id", ""), "solver error")
            continue

        # ── Step 4: Submit ─────────────────────────────────
        try:
            print(f"\n  📤 Submitting answer...")
            sub_result = await submit_task(
                id_token=ID_TOKEN,
                agent_id=agent_id,
                task_id=task["id"],
                content=answer,
                metadata={
                    "agent_name": AGENT_NAME,
                    "model": "gemini-2.0-flash",
                    "category": category,
                    "tokens": tokens,
                    "latency": latency
                }
            )
            print(f"  Arena response: {sub_result}")
        except Exception as e:
            print(f"  ❌ Submit failed: {e}")
            continue

        # ── Step 5: Analyze ────────────────────────────────
        score = parse_score(sub_result)
        diagnosis = analyze(category, score, tokens, latency, answer)

        # ── Step 6: Optimize & Save Memory ─────────────────
        try:
            optimize(diagnosis, task, answer)
        except Exception as e:
            print(f"  ⚠️  Optimizer error (non-fatal): {e}")

        # Track history
        history.append({
            "task": task.get("title", ""),
            "category": category,
            "score": score,
            "tokens": tokens,
            "latency": latency,
            "level_up": diagnosis["level_up"]
        })

        # Brief pause between tasks to avoid rate limits
        await asyncio.sleep(2)

    # ── Final Summary ──────────────────────────────────────
    if history:
        print_summary(history, agent_id)
    else:
        print("\n⚠️  No tasks completed this session.")


if __name__ == "__main__":
    asyncio.run(run())
