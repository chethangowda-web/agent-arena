# MetaMind — Self-Evolving Agent Arena Competitor

## Architecture
```
Task → Solver Agent → Submit → Score Analyzer → Prompt Optimizer → Strategy Memory → Next Task
```

## Setup (3 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Fill in .env
Open `.env` and set:
- `GEMINI_API_KEY` → Get from https://aistudio.google.com/apikey (starts with AIza...)
- `LINKEDIN_URL` → Your LinkedIn profile URL
- `ID_TOKEN` → Refresh from Agent Arena site every ~1 hour

### 3. Run
```bash
python main.py
```

## What happens
1. MetaMind registers itself with Agent Arena
2. Fetches a task
3. Detects task category (logic / code / math / data / context)
4. Loads best known strategy for that category
5. Calls Gemini Flash to solve the task
6. Submits the answer
7. Analyzes the score
8. Uses Gemini to generate a better strategy
9. Saves improved strategy to `strategy_memory.json`
10. Repeats for next task — getting smarter each time

## Files
| File | Purpose |
|------|---------|
| `main.py` | Evolution loop — entry point |
| `solver.py` | Solver Agent — calls Gemini to answer tasks |
| `analyzer.py` | Score Analyzer — diagnoses what went wrong |
| `optimizer.py` | Prompt Optimizer — generates better strategies |
| `memory.py` | Read/write `strategy_memory.json` |
| `mcp_client.py` | Low-level Arena MCP HTTP calls |
| `strategy_memory.json` | Persistent strategy brain |
| `.env` | All credentials |

## Hackathon Demo Flow
Show judges this progression in `strategy_memory.json`:
- Task #1 → Score 61 (default strategy)
- MetaMind learns → updates logic prompt
- Task #2 → Score 83 (improved strategy)  
- MetaMind adapts → refines further
- Task #3 → Score 91 (optimized strategy)
