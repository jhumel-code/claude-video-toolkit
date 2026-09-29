### VHS tape, house style: what scripts/gentape.py emits for the trustabl profile.
### Prefer generating tapes with gentape.py (the style then follows the brand profile);
### hand-edit a copy of this only for shapes gentape cannot express.
### Render in WSL as the demo user:  cd /home/demo/demo && vhs demo.example.tape
### Rules: Output must be a relative path; recorded at the video canvas size (2560x1440)
### so nothing is ever scaled; clear before every command after the first so beats.py can
### pin the beats; a Type string may use "double" or `backtick` quotes (backticks when the
### command itself contains double quotes).

Output demo.mp4
Set Shell "bash"
Set FontSize 28
Set Width 2560
Set Height 1440
Set Padding 30
Set Margin 40
Set MarginFill "#070E1A"
Set BorderRadius 12
Set WindowBar Colorful
Set TypingSpeed 35ms
Set Theme {"background": "#0D1B2A", "foreground": "#E8EBF0", "cursor": "#51C1B5", "selection": "#16283F", "black": "#0A1626", "brightBlack": "#4A5A70", "red": "#FF6B5C", "brightRed": "#FF8B7C", "green": "#8FD13F", "brightGreen": "#A8E05F", "yellow": "#E0C066", "brightYellow": "#F0D486", "blue": "#6FA8E8", "brightBlue": "#8FC0F5", "magenta": "#B48EE8", "brightMagenta": "#C9A8F5", "cyan": "#51C1B5", "brightCyan": "#7FE0D4", "white": "#E8EBF0", "brightWhite": "#FFFFFF"}

# hidden setup: cd plus any env the commands need (the VHS shell may not source ~/.bashrc)
Hide
Type "cd /home/demo/demo/myrepo && source ./demo-env.sh && clear"
Enter
Sleep 2s
Show
Sleep 1.5s

# beat 1: type, pause, run, wait for the prompt, hold on the result
Type "trustabl scan ."
Sleep 2s
Enter
Wait@90s /^> ?$/
Sleep 4s

# beat 2: clear first, then the next command (backticks: the command has double quotes)
Type "clear"
Enter
Sleep 0.8s
Type `trustabl scan . --json-out scan.json && jq -r ".findings | length" scan.json`
Sleep 2s
Enter
Wait@90s /^> ?$/
Sleep 6s

# Hold long enough for the result line: vid.py plays 1.5 s of the result before holding.
# A scroll/stream beat that plays under its narration needs a hold as long as that line.
