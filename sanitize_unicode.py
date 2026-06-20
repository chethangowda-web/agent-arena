import os
import re
# Files to sanitize
files = [
    "main.py",
    "solver.py",
    "analyzer.py",
    "optimizer.py",
    "memory.py",
]

emoji_map = {
    "📊": "[STATS]",
    "📌": "[TASK]",
    "🧠": "[BRAIN]",
    "📋": "[INFO]",
    "🎯": "[TARGET]",
    "📤": "[SEND]",
    "🔧": "[FIX]",
    "📝": "[MEM]",
    "🏆": "[WIN]",
    "✅": "[OK]",
    "⚠️": "[!]",
    "❌": "[X]",
    "💡": "[TIP]",
    "🔍": "[LOOK]",
    "🚀": "[START]",
    "🔁": "[LOOP]",
    "📈": "[UP]",
    "─": "-",
    "═": "=",
    "╔": "",
    "╗": "",
    "╚": "",
    "╝": "",
    "║": "|",
    "┌": "+",
    "┐": "+",
    "└": "+",
    "┘": "+",
    "│": "|",
}

for fname in files:
    fpath = os.path.join("D:\\xampp\\tmp\\metamind\\metamind", fname)
    if not os.path.exists(fpath):
        print(f"Skipping {fname}, not found")
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content
    for emoji, replacement in emoji_map.items():
        new_content = new_content.replace(emoji, replacement)
    
    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Sanitized: {fname}")
    else:
        print(f"No changes: {fname}")

print("Done")
