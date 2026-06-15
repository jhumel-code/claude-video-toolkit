# 03 · Recording a Real Claude Code Session

For an **in-IDE / plugin demo** where you want the actual `claude` TUI on camera
(tool calls, skills loading, file edits). VHS drives a live `claude` session in WSL.

## One-time WSL setup (`demo` user)

```bash
# 1. Linux Node via the OFFICIAL tarball (apt/nodesource gave stale v12; claude needs >=18)
cd ~ && curl -fsSLO https://nodejs.org/dist/v20.18.1/node-v20.18.1-linux-x64.tar.xz
tar -xf node-v20.18.1-linux-x64.tar.xz
export PATH="$HOME/node-v20.18.1-linux-x64/bin:$HOME/.npm-global/bin:$PATH"
echo 'export PATH="$HOME/node-v20.18.1-linux-x64/bin:$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
npm config set prefix ~/.npm-global
npm i -g @anthropic-ai/claude-code

# 2. Auth: copy your Windows login into WSL
mkdir -p ~/.claude && cp /mnt/c/Users/<you>/.claude/.credentials.json ~/.claude/.credentials.json
#    (works; note: an OAuth refresh during the demo COULD log out your main session — accepted risk.
#     Cleaner alternative: export ANTHROPIC_API_KEY in WSL instead.)
```

### Stop the interactive TUI from hanging on onboarding

`claude -p` (headless) authenticates fine, but the **interactive TUI runs
first-run onboarding** (login-method picker, theme, trust dialog) and hangs the
tape. Seed `~/.claude.json`:
```python
python3 - <<'PY'
import json,os; p=os.path.expanduser("~/.claude.json")
d=json.load(open(p)) if os.path.exists(p) and os.path.getsize(p)>1 else {}
d["hasCompletedOnboarding"]=True; d.setdefault("theme","dark"); d["numStartups"]=10
d["bypassPermissionsModeAccepted"]=True
pd=d.setdefault("projects",{}).setdefault("/home/demo/demo/<repo>",{})
pd["hasTrustDialogAccepted"]=True; pd["hasCompletedProjectOnboarding"]=True
json.dump(d,open(p,"w"),indent=2); print("seeded")
PY
```

### Install the plugin under test (if any)

```bash
claude plugin marketplace add <owner>/<repo>      # or a local /mnt/c/... path
claude plugin install <plugin>@<marketplace>
claude plugin list                                # must show "✔ enabled"
```

## The tape

Launch with `--model opus` (kills a transient "model unavailable" banner) and
**accept the bypass-permissions warning at a fixed time** right after launch — it's
deterministic, unlike the mid-session tool-approval prompt (which the allow-list
`mcp__<srv>__<tool>` did NOT pre-approve). Trim the warning frame in post.

```tape
Output full.mp4
Set Shell "bash"
Set FontSize 14
Set Width 1300
Set Height 840
Set Padding 16
Set Theme "Dracula"
Set TypingSpeed 32ms
Hide
Type "export PATH=$HOME/node-v20.18.1-linux-x64/bin:$HOME/.npm-global/bin:$PATH"
Enter
Type "cd ~/demo/<repo> && clear"
Enter
Show
Sleep 1s
Type "claude --model opus --dangerously-skip-permissions"
Enter
Sleep 3s
Down
Enter
Sleep 8s
Type "<your prompt that drives the demo>"
Sleep 1s
Enter
Sleep 300s      # long enough for the whole session to finish
```

**Design the scenario to converge cleanly.** A real session is non-deterministic;
pick a repo/prompt where the result is stable and satisfying (e.g. for a scan→fix
demo, use inputs where the auto-fix actually reaches a clean state — literal URLs,
no rule-conflict cascades). Run it **headless first** (`claude -p "..."`) to confirm
where it lands before recording.

## Re-pace into a narrated cut — `session_vid.py`

A ~4 min raw take is too long. `session_vid.py` re-paces it to ~2-3 min:
- **speed-fit** action spans (`setpts=(ld+GAP)/L*PTS`) — scan running, edits, re-scans;
- **freeze-hold** result frames you want readable (the findings table, the final score).

Per scene = `{text, mode:"speed"|"freeze", in/out or at}`. Pull narration-accurate
content from the **session transcript** at
`~/.claude/projects/<slug>/*.jsonl` (assistant text turns) — far more reliable than
reading frames. Same mix + upscale + zoom finish as `vid.py`.

## Gotchas specific to this path

- The `claude` TUI streams constantly (spinner) → scene-change detection won't find
  beats; map beats by reading frames + the transcript.
- A small grey **"bypass permissions on"** indicator sits at the bottom throughout.
  It's authentic; crop the bottom strip if you want it gone.
- `claude plugin install` from GitHub fails if the plugin manifest references the
  standard `hooks/hooks.json` (Claude Code 2.1.x auto-loads it → "Duplicate hooks
  file"). The plugin must NOT list it in `plugin.json`.
