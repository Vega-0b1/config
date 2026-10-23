---
name: quick-scope
description: Start a silent browser-page screenshot watcher for quick questions about reading material. Meta+C captures the active browser window, crops it to one Canvas question box (picked by highlighted text, then the mouse pointer, then topmost) or a fixed quiz-column rectangle, and saves it into ~/Pictures/claude without changing focus or desktop. The session processes archived page images through immutable scratch copies. `/quick-scope` starts the watcher; `/quick-scope stop` ends it.
---

Pipeline: Meta+C → `screenshot-to-claude` → archived `shot-*.png` → `watch_capture.py` → immutable session copy → answer → acknowledge → next queued archive.
The hotkey and script are declared in `~/repos/debian-config/modules/plasma.nix` (`hotkeys.commands."screenshot-to-claude"` and `home.file.".local/bin/screenshot-to-claude"`).
Capture profile: this machine's Chromium window, with its bookmarks bar hidden; the helper captures the active window without decorations or shadows and removes its top 140 physical pixels. It then crops to one question box (1-px `rgb(169,168,168)` outline, at least 300×100 px): the box containing highlighted text (Chromium selection `rgb(77,105,210)`), else the box under the mouse pointer (queried from KWin), else the topmost box fully in view, else the topmost partial box. With no box it crops to the fixed rectangle 1872×1168+470+428 of the page image, measured from a 2880-px-wide window. The desktop panel lies outside the window capture. Only cropped images are published to the archive and latest.png.

## Start

R1. IF invoked as `/quick-scope` THEN run `qdbus org.kde.kglobalaccel /component/plasma_manager_commands_desktop org.kde.kglobalaccel.Component.shortcutNames` and check that the output contains `screenshot-to-claude`.
R2. IF R1's output does not contain `screenshot-to-claude` AND `~/.local/bin/screenshot-to-claude` exists THEN tell the user the shortcut is not registered with the running session and that logging out and back in registers it. Still apply R4.
     // Commentary: in Plasma 6 kglobalaccel runs inside KWin and reads new desktop actions only at session start; kbuildsycoca6 does not refresh it.
R3. IF `~/.local/bin/screenshot-to-claude` does not exist THEN tell the user the script is missing from the active Home Manager generation, and do not start the watcher.
R4. IF a quick-scope watcher started in this session is still running THEN do not start a second one.
R5. IF R3 and R4 do not apply THEN run `python3 <skill-dir>/watch_capture.py next ~/Pictures/claude <session-dir>` as a background task and retain its task ID.
R5a. IF starting a new quick-scope session THEN create one scratch session directory with `mktemp -d` and run `python3 <skill-dir>/watch_capture.py init ~/Pictures/claude <session-dir>` before R5; reuse that session directory for every subsequent next/ack call until stop.
     // Commentary: init ignores pre-session archives. next scans unacknowledged archives before waiting, so events during answer preparation or watcher restart are retained.
R6. IF the watcher is started THEN the entire reply is one line: `Watching. Press Meta+C to send a capture.`

## On capture

// Order of operations. Each capture is handled in exactly this sequence.
R7. IF the watcher completes with exit code 0 THEN read the immutable image path printed by watch_capture.py and open that image; never answer from mutable latest.png.
R8. IF R7 has read the image THEN build the answer line per R13–R19.
R9. IF the answer line is built THEN send the notification per R20–R23 before any other tool call.
R10. IF the notification is sent THEN acknowledge the pending image with `python3 <skill-dir>/watch_capture.py ack ~/Pictures/claude <session-dir>` and restart under R5 in the same turn; queued captures return immediately without requiring another keypress.
R11. IF the watcher is restarted THEN write the chat reply per R24–R26.
     // Commentary: the user is on another workspace; the notification is the reply they read first, so it goes out before the watcher restart and the chat text.
R12. IF the watcher completed with a nonzero exit code THEN tell the user in one line and restart it per R5.

## Answer line

R13. IF the user's last message before the capture asked a question or gave a task THEN the answer line answers that question or task about the capture.
R14. IF R13 does not apply AND the capture shows a multiple-choice question THEN the answer line is `<letter>. <option text>`, copying the option text exactly as shown.
     // Example: `B. Sahara Desert`
R14a. IF the multiple-choice options carry no letter or number on screen THEN the answer line is the option text alone, copied exactly as shown. R14a overrides R14.
     // Example: options Cancer / Leo / Virgo with radio buttons → `Virgo`
R15. IF R13 does not apply AND the capture shows an arithmetic expression THEN compute it with `python3 -c` and the answer line is the result with comma thousands separators.
     // Example: `10! + 117` → `3,628,917`
     // Commentary: computing instead of recalling makes the result reproducible.
R16. IF R13 does not apply AND the capture shows any other question or problem statement THEN the answer line is the answer in one sentence of at most 200 characters.
R17. IF R13–R16 do not apply THEN the answer line names the window or file and the code or text in focus, in one sentence.
R18. IF the text in focus is code the user is writing THEN apply R17 and do not include hints, fixes, or critique. R18 overrides R14–R16.
     // Commentary: the user's coding-practice preference is to answer only what is asked.
R19. IF the capture shows several questions THEN the answer line answers the one that is active or numbered as current; IF none is marked current THEN answer the topmost.
     // Example: a quiz showing `3 / 4` → answer question 3 only.

## Notification

R20. IF the answer line is built THEN send it with `notify-send -a Claude -i dialog-information "Quick Scope" "<answer line>"`.
R21. IF the answer line contains a double quote, backtick, or `$` THEN pass it through a single-quoted heredoc variable, not inline.
     // Example: `body=$(cat <<'EOF'` … `EOF` `)` then `notify-send -a Claude -i dialog-information "Quick Scope" "$body"`.
R22. IF the answer line is longer than 300 characters THEN the notification body is its first sentence followed by ` (full reply on Ref)`. R22 overrides R20 for the body text.
R23. IF building the notification THEN do not pass `-t` or `-u`.
     // Commentary: the popup duration comes from Plasma's PopupTimeout (2000 ms, set in plasma.nix); `-u critical` would make it stay until dismissed.

## Chat reply

R24. IF writing the chat reply THEN its first line is the answer line, alone.
R25. IF writing the chat reply THEN add at most one line of context: the question number shown on screen (`Question 3 of 4`), or the computation behind an arithmetic result (`10! = 3,628,800, plus 117`).
R26. IF the capture shows the user's previous answer marked wrong AND that question was answered by quick-scope THEN add one line stating that and the answer quick-scope gave. Do not put it in the notification.
     // Example: `Question 2 shows as wrong; quick-scope's answer was D (World War I).`

## Stop

R27. IF a notification reports the watcher stopped without completing THEN do not restart it; tell the user in one line that `/quick-scope` restarts it.
     // Commentary: a stopped watcher means the session ended or the user stopped it. Logging out of Plasma also kills it.
R28. IF invoked as `/quick-scope stop` AND a watcher from this session is running THEN stop it with TaskStop and reply `Stopped.`
R29. IF invoked as `/quick-scope stop` AND no watcher is running THEN reply `Not watching.`
R30. IF any quick-scope rule would delete a file in `~/Pictures/claude` THEN do not delete it.
     // Commentary: captures accumulate until the user removes them.

// Fallback
R31. IF a capture presents a case R13–R26 do not cover THEN answer the topmost problem on screen in the shortest form that answers it, and still follow R9–R11 and R24. Do not stop, explain the gap, or ask.
     // Commentary: quick-scope exists for quick, simple answers; a stalled capture defeats it.
R32. IF any condition not covered by R1–R31 arises outside capture handling THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
R33. R31 overrides R32 when both could apply to a capture.
