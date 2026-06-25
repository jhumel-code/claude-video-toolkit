#!/usr/bin/env bash
# make_voice.sh <edge-voice> <prefix>   -> writes vo/<prefix>_<clip>.mp3 (natural rate)
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # resolve before cd, to find pronounce.py
cd "${WORKDIR:-$PWD}/vo"
V="$1"; P="$2"
# apply profiles/pronounce.json (jargon -> spoken form) before edge-tts; edge-tts has no phoneme control
gen() { local t; t="$(python3 "$HERE/pronounce.py" "$2")"; python -m edge_tts --voice "$V" --text "$t" --write-media "${P}_$1.mp3" >/dev/null 2>&1; printf "%s %.1f\n" "$1" "$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ${P}_$1.mp3)"; }

# --- INTRO (3 clips; holds rebuilt to fit) ---
gen r01a "Trustabl is a security scanner for AI agents. It reads your agent's source code without ever running it, and finds the security and reliability risks hiding inside."
gen r01b "It works across every major agent framework: the Claude SDK, OpenAI Agents, Google ADK, LangChain, and Model Context Protocol servers."
gen r01c "Let's point it at a real project: Anthropic's own published agent examples."
# --- BODY (authoritative text from make_natural.sh; r13 split into r13a/r13b) ---
gen r02a "The scan finds four agents, and scores each one separately. The tester scores the lowest."
gen r02b "Three of the problems are high severity. The tester can run shell commands and write files, and a second agent can write files too."
gen r03 "To lock it down, Trustabl generates two files for that agent."
gen r04 "The agent's report card says it's not ready to ship. The tester can run shell commands and write files, so one hijacked instruction could do real damage. The fix is right there: remove the shell, or limit it to a few safe commands."
gen r05 "The second file is the sandbox policy. This agent only uses built-in tools and never reaches the internet, so the policy blocks all network access. It also runs without admin rights and can only write in a few safe places. Even if it gets attacked, the damage stays inside the box."
gen r06 "Next, a different agent: an on-call assistant that helps handle incidents. Its tools call services directly. One checks a status page, one opens incidents, one reads an internal metrics server, and one saves a postmortem."
gen r07 "One command later, we have a network policy built from the code itself. The status check can only read its one status page. The incident tool can only post to its one endpoint. And the internal metrics server is listed separately, marked for a person to review."
gen r09 "Now the best part. We turn the policy on for real, in a sandbox."
gen r10 "One quick setup step: we point the policy at Python inside the sandbox. And look, this is the exact same policy we generated a moment ago."
gen rb1 "Now Trustabl hands the policy to OpenShell, which builds a locked-down sandbox to run the agent in."
gen rb2 "Non-root, a small writable space, and only the network the code actually needs."
gen r12 "The sandbox is up. Inside it, the agent runs without admin rights."
gen r13a "File access follows the policy. The temp folder works."
gen r13b "The system folder is blocked."
gen r14a "Now the network. The policy allows just one status page."
gen r14b "And it's allowed, so it goes right through."
gen r15a "Same page, but now we try to send data instead of reading."
gen r15b "And it's blocked. The sandbox enforces exactly the rule that came from the code."
gen r16a "What about any other website?"
gen r16b "Also blocked."
# --- OUTRO (detailed; hold rebuilt to fit) ---
gen r17 "From a single read-only scan, Trustabl does three things. It detects the risks hiding in your agent's tools and permissions. It declares what the agent is allowed to do, in a portable manifest you can read and review. And it enforces least privilege with a real sandbox policy, so even a compromised agent stays inside its box. Trustabl: know what your agents can do, and prove what they can't."
