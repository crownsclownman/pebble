    ;   PEB - is a monitor program designed for pebble cpu.
    ;   it should be loaded at 0x0000.
    ;
    ;   main loop consists of:
    ;       waiting for user input
    ;       updating the screen
    ;       check if user input is a valid cmd
    ;           if yes - execute the cmd with arguments
    ;           if no - print help message
    ;       
    ;   supported commands:
    ;       p <addr> <len>  - prints <len> bytes at <addr>, if no <len>, then print byte at <addr>
    ;       l <file>        - loads the <file> at 0xSPECIFY
    ;       g <addr>        - pass control to <addr>
    ;       s <addr> <val>  - store <val> at <addr>
    ;
    ;   memory map:
    ;       0x0000 - 0x0FFF: the peb monitor program
    ;       0x0000 - 0x0000: the start of monitor program and init
    ;       0x0FFF - 0x0FFF: the end of monitor program
    ;
    ;       0x1000 - 0x1FFF: PEB's variables
    ;       0x1002 - 0x10FF: Input buffer
    ;
    ;       0xF000 - 0xFFFF: IO Page
    ;       0xF000 - 0xF000: Keyboard output
    ;       0xF001 - 0xF001: Terminal input
    ;
    ;   variables:
    ;       0x1000: buf_ptr - lower byte of current input buffer position, higher byte is always 0x1
    ;       0x1001: tmp char store

init:
    ; init buf_ptr
    ldi 0x10
    ldx
    ldi 0x00
    ldy
    ldi 0x02
    std
    jmp loop

loop:
    ldi 0xF0                        ; чтение символа с клавиатуры
    ldx
    ldi 0x00
    ldy
    ldd

	mab                             ; b - символ
	ldi 0x00
    sub
    jz loop

                                    ; запись символа в [0x1001]
    ldi 0x10
    ldx
    ldi 0x01
    ldy
    ldi 0x00
    add
    std

                                    ; был ли нажат enter? 
    ldi 0x0D
    sub
    jz enter_pressed

                                    ; был ли нажат backspace?
    ldi 0x08
    sub
    jz backspace_pressed

                                    ; загрузка позиции в buffer'е
    ldi 0x10
    ldx
    ldi 0x00
    ldy
    ldd                             ; a = index
    mab                             ; b = index

    ldi 0xFF
    sub                             ; a = 0xFF - index
    jz loop                         ; буфер полон - игнорируем

    ldi 0x01
    ldy
    ldd                             ; a = [0x1001] = символ
    mab                             ; b = символ

    ldi 0x00
    ldy                             ; x = 0x10, y = 0x00
    ldd                             ; a = [0x1000]
    ldy                             ; xy = 0x1000 + ptr

    ldi 0x00
    add                             ; a = символ
    std                             ; buf[index] = символ

    ldi 0xF0
    ldx
    ldi 0x01
    ldy
    ldi 0x00
    add                             ; a = символ
    std                             ; эхо в терминал

    ldi 0x10
    ldx
    ldi 0x00
    ldy
    ldd                             ; a = index
    mab                             ; b = index
    ldi 0x01
    add                             ; a = index + 1
    std                             ; [0x1000] = index + 1

    jmp loop

backspace_pressed:
    ldi 0x02
    mab                             ; b = 2

    ldi 0x10
    ldx
    ldi 0x00
    ldy
    ldd                             ; a = index
    
    sub                             ; a = index - 2
    jz loop                         ; index == 2, буфер пуст

    ldd                             ; a = index
    ldi 0x01
    sub                             ; a = index - 1
    std                             ; [0x1000] = index - 1

    ldi 0xF0
    ldx
    ldi 0x01
    ldy
    ldi 0x08
    std                             ; эхо backspace
    ldi 0x20
    std                             ; пробел
    ldi 0x08
    std                             ; backspace

    jmp loop

enter_pressed:
    ldi 0xF0
    ldx
    ldi 0x01
    ldy
    ldi 0x0D
    std
    ldi 0x0A
    std                             ; \r\n
    
    ldi 0x10
    ldx
    ldi 0x00
    ldy
    ldd
    mab
    ldi 0x02
    sub
    jz cmd_done

    jmp dispatch

cmd_done:
    ldi 0x10
    ldx
    ldi 0x00
    ldy
    ldi 0x02
    std                             ; index = 1

    jmp loop

dispatch:
    jmp loop
