# POST HOC audit of the August 2026 command-line judge (frontier_judge.py, registered at 034592a).
# Reads the local Claude Code session transcripts that the calls left behind (outside the repository) and counts,
# per condition, how many calls produced an extended-thinking block. Writes papers/analysis/cli_transcript_audit.json.
import glob
import json
import os

D = os.path.expanduser("~/.claude/projects/-Users-srivatsavadaruru-Documents-projects-stanford-agents-judge-free-eval-experiments-tfa-vs-judge")
out = {"sessions": 0, "blind": {"calls": 0, "thinking": 0}, "referenced": {"calls": 0, "thinking": 0}, "tool_calls": 0}
for f in glob.glob(f"{D}/*.jsonl"):
    prompt, thinking, tools = None, False, 0
    for line in open(f):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = r.get("message") or {}
        content = msg.get("content")
        if r.get("type") == "user" and prompt is None:
            prompt = content if isinstance(content, str) else " ".join(c.get("text", "") for c in content or [] if isinstance(c, dict))
        if r.get("type") == "assistant" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "thinking":
                    thinking = True
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tools += 1
    if not prompt or "Candidate solution" not in prompt:
        continue
    out["sessions"] += 1
    out["tool_calls"] += tools
    cond = "referenced" if "Reference answer" in prompt else "blind"
    out[cond]["calls"] += 1
    out[cond]["thinking"] += int(thinking)
json.dump(out, open("papers/analysis/cli_transcript_audit.json", "w"), indent=1)
print(json.dumps(out))
