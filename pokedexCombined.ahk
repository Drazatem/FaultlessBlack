^d:: ; Hotkey: Ctrl + D
{
    ; No space version
    Click, 2
    Sleep, 200 ; Increased sleep duration
    Send, {Backspace 2}
    Sleep, 150 ; Pause before the next segment

    ; Space version 1
    Click, 2
    Sleep, 200 ; Increased sleep duration
    Send, {Backspace 2}
    Sleep, 150 ; Increased sleep duration
    Send, {Space}
    Sleep, 150 ; Pause before the next segment

    ; Space version 2
    Click, 2
    Sleep, 200 ; Increased sleep duration
    Send, {Backspace 2}
    Sleep, 150 ; Increased sleep duration
    Send, {Space}
    Sleep, 150 ; Pause before the next segment

    ; Space version 3
    Click, 2
    Sleep, 200 ; Increased sleep duration
    Send, {Backspace 2}
    Sleep, 150 ; Increased sleep duration
    Send, {Space}
    Sleep, 150 ; Pause before the next segment

    ; Final no space version
    Click, 2
    Sleep, 200 ; Increased sleep duration
    Send, {Backspace 2}
    return
}
