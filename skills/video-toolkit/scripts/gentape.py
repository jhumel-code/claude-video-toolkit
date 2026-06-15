import sys, json, os
# gentape.py <batch.json>  -> writes one .tape per entry (standard clean structure: clear before each command)
batch = json.load(open(sys.argv[1], encoding="utf-8"))
HEAD = ('Output {out}.mp4\nSet Shell "bash"\nSet FontSize 14\nSet Width 1300\nSet Height 840\n'
        'Set Padding 16\nSet Theme "Dracula"\nSet TypingSpeed 35ms\n\n'
        'Hide\nType "cd ~/demo && clear"\nEnter\nShow\nSleep 1.5s\n\n')
for e in batch:
    t = HEAD.format(out=e["out"])
    for i,(cmd,hold) in enumerate(e["beats"]):
        if i>0:
            t += 'Type "clear"\nEnter\nSleep 0.8s\n'
        t += f'Type "{cmd}"\nSleep 2s\nEnter\nWait@90s /^> ?$/\nSleep {hold}s\n\n'
    open(os.path.join(os.environ.get("WORKDIR","."), e["tape"]),"w",encoding="utf-8").write(t)
    print("wrote", e["tape"])
