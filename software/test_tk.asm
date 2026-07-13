;0xF000 - 0xF00F: IO

;0xF000 - kb
;0xF001 - tm

; read kb, write to tm.

loop:
    ldi 0xF0
    ldx
    ldi 0x00
    ldy
    ldd

    sub
    jz loop

    ldi 0xF0
    ldx
    ldi 0x01
    ldy
    ldd

    jmp loop
