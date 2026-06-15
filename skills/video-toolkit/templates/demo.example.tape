### VHS tape template — house style (Dracula, 1300x840, FontSize 14).
### Render in WSL as the `demo` user:  cd /home/demo/demo && vhs demo.example.tape
### Output MUST be a relative path. Commands use single quotes only.

Output demo.mp4
Set Shell "bash"
Set FontSize 14
Set Width 1300
Set Height 840
Set Padding 16
Set Theme "Dracula"
Set TypingSpeed 35ms

# hide the setup (cd + clear) from the recording
Hide
Type "cd ~/demo/myrepo && clear"
Enter
Show
Sleep 1.5s

# --- beat 1: type, pause, run, hold on the result ---
Type "trustabl scan ."
Sleep 2s
Enter
Wait@90s /^> ?$/
Sleep 4s

# --- beat 2: clear first, then the next command ---
Type "clear"
Enter
Sleep 0.8s
Type "trustabl scan . --vuln-scan"
Sleep 2s
Enter
Wait@90s /^> ?$/
Sleep 6s
