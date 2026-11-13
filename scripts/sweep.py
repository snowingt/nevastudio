#!/usr/bin/env python3
import os
import sys

FORBIDDEN = ["el diff", "sloth.app", "sloth-app"]
IGNORED_DIRS = {".git", "node_modules", "runtimes", "dist", ".cache", "data"}

def sweep():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    violations = []
    
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for f in filenames:
            if not f.endswith((".ts", ".tsx", ".js", ".mjs", ".json", ".css", ".html")):
                continue
            path = os.path.join(dirpath, f)
            rel = os.path.relpath(path, root)
            if "MASTER_PLAN" in rel or "sweep.py" in rel:
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read().lower()
                    for word in FORBIDDEN:
                        if word in content:
                            violations.append((rel, word))
            except Exception:
                pass

    if violations:
        print(f"FAILED: Found {len(violations)} brand violations:")
        for rel, word in violations[:20]:
            print(f"  - {rel}: contains '{word}'")
        sys.exit(1)
    else:
        print("SWEEP SUCCESS: Clean-room brand verification passed with 0 violations!")

if __name__ == "__main__":
    sweep()
