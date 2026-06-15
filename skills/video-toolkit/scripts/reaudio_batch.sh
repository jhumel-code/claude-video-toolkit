#!/bin/bash
# Re-audio every marketing video with the English-locked Ava voice (kills code-switching).
# Originals are backed up to _pre-audio-fix/ before each overwrite -> fully reversible.
cd "${WORKDIR:-$PWD}"
MV="${OUT_DIR:-./out}"
mkdir -p "$MV/_pre-audio-fix"
ok=0; fail=0; flagged=""
for s in vo/spec_*.json; do
  name=$(python -c "import json,sys;print(json.load(open(sys.argv[1],encoding='utf-8'))['name'])" "$s")
  vid="$MV/$name.mp4"
  [ -f "$vid" ] || { echo "SKIP $name (no video)"; continue; }
  [ "$name" = "07-network-policy-from-code" ] && { echo "SKIP $name (already fixed)"; continue; }
  cp -n "$vid" "$MV/_pre-audio-fix/" 2>/dev/null
  out=$(python vo/reaudio.py "$s" "$vid" "/tmp/$name.fix.mp4" 2>>/tmp/reaudio_err.log)
  if [ $? -eq 0 ] && [ -f "/tmp/$name.fix.mp4" ]; then
    mv -f "/tmp/$name.fix.mp4" "$vid"
    echo "$out"
    # flag any video where a clip needed >5% time-fit (worth an ear-check)
    at=$(echo "$out" | grep -oE "max_atempo=[0-9.]+" | cut -d= -f2)
    awk "BEGIN{exit !($at>1.05)}" && flagged="$flagged $name($at)"
    ok=$((ok+1))
  else
    echo "FAIL $name"; fail=$((fail+1))
  fi
done
echo "==== BATCH COMPLETE: ok=$ok fail=$fail ===="
echo "FLAGGED (atempo>1.05, ear-check):${flagged:- none}"
