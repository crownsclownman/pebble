    ;   peb - is a monitor program designed for pebble cpu.
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
