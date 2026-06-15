### Trustabl branded VHS tape - house style (see docs/10-style-guide.md S7).
### Render in WSL as the demo user:  cd /home/demo/demo && vhs branded.tape
### Output MUST be a relative path. Commands use single quotes only.
### Requires "JetBrainsMono Nerd Font" installed in WSL (or swap FontFamily).
Output demo.mp4
Set Shell "bash"
Set Width 2400
Set Height 1200
Set FontFamily "JetBrainsMono Nerd Font Mono"
Set FontSize 36
Set LineHeight 1.2
Set Framerate 30
Set CursorBlink false
Set WindowBar Colorful
Set WindowBarSize 50
Set BorderRadius 10
Set Margin 40
Set MarginFill "#070E1A"
Set Padding 24
Set Theme { "name": "Trustabl", "background": "#0D1B2A", "foreground": "#E8EBF0", "black": "#1A2744", "red": "#FF6B6B", "green": "#51C1B5", "yellow": "#FFD166", "blue": "#4EA8DE", "magenta": "#C77DFF", "cyan": "#51C1B5", "white": "#E8EBF0", "brightBlack": "#2A3F6B", "brightGreen": "#6ECFC4", "brightCyan": "#6ECFC4", "cursor": "#51C1B5", "selection": "#1A3A5C" }

# --- setup hidden from the recording ---
Hide
Type "cd /home/demo/demo && clear"
Enter
Show
Sleep 1s

# --- beat: type at natural speed, pause, run, hold on the result ---
Type@35ms "./trustabl scan agent-repo"
Sleep 800ms
Enter
Wait@90s /^> ?$/
Sleep 4s

# Cadence tip (verify on your VHS version): wrap a long/boring phase with
#   Set PlaybackSpeed 2.0  ...commands...  Set PlaybackSpeed 1.0
# to accelerate scan progress and slow back down to hold on the findings.
