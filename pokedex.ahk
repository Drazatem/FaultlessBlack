^d:: ; Hotkey: Ctrl + D
{
    Click, 2  ; Perform a double-click
    Sleep, 100 ; Pause briefly to ensure the double-click registers (adjust if necessary)
    Send, {Backspace} ; Backspace
    Send, {Backspace} ; Backspace
    Sleep, 50 ; Pause briefly to ensure backspace registers
    Send, {Space} ; Enter a space
    return
}
