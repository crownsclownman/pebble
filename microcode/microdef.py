# Базовые константы для фазы Fetch (выборка 16-битной инструкции за 2 такта)
FIRST_BYTE_FETCH  = ["src_addr=0", "src_data=8", "MEM_OE", "IR0_READ_DBUS", "PC_INC"]
SECOND_BYTE_FETCH = ["src_addr=0", "src_data=8", "MEM_OE", "IR1_READ_DBUS", "PC_INC"]

MICROCODE = {}

# -------------------------------------------------------------------------
# Группа 00: Память и Регистры (Регистровые операции и константы)
# -------------------------------------------------------------------------

# 0100: ldi imm8 (A = imm8). imm8 берется из младшего байта инструкции (IR0)
# Для этого в src_data состояние 'internal_ir0' мы маппим, например, на значение 6 или 7.
# Допустим: Z=0, a=1, b=2, x=3, y=4, alu=5, shr=6, internal_ir0=7
MICROCODE[0x4] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH + ["dst_data=1"],
    ["upc_clr"],
]

# 0101: ldx (X = A)
MICROCODE[0x5] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=3", "upc_clr"]
]

# 0110: ldy (Y = A)
MICROCODE[0x6] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=4", "upc_clr"]
]

# 1001: mab (B = A)
MICROCODE[0x9] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=2", "upc_clr"]
]

# -------------------------------------------------------------------------
# Группа 01: Шина памяти данных
# -------------------------------------------------------------------------

# 0111: ldd (A = [X:Y])
MICROCODE[0x7] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_addr", "MEM_OE", "src_data=8", "dst_data=1", "upc_clr"] # src_data=5 это external DBUS
]

# 1000: std ([X:Y] = A)
MICROCODE[0x8] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_addr", "MEM_WE", "src_data=1", "upc_clr"] # dst_data=0 (None)
]

# -------------------------------------------------------------------------
# Группа 10: АЛУ и сдвиги
# -------------------------------------------------------------------------

# 0000: add, 0001: sub, 0010: and, 0011: xor
# Они работают автоматически на основе младших бит опкода, когда src_data=alu (допустим 5)
for alu_op in [0x0, 0x1, 0x2, 0x3]:
    MICROCODE[alu_op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        ["src_data=5", "dst_data=1", "FLAGS_WE", "upc_clr"] # Защелкиваем результат и флаги
    ]

# 1010: shr (A = A >> 1)
MICROCODE[0xA] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=6", "dst_data=1", "FLAGS_WE", "upc_clr"] # src_data=6 это жестко разведенный SHR буфер
]

# 1011: inc (X:Y = X:Y + 1)
MICROCODE[0xB] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["CLK_X", "CLK_Y", "upc_clr"] # Стробируем счетчики адреса
]

# -------------------------------------------------------------------------
# Группа 11: Управление потоком (Переходы)
# -------------------------------------------------------------------------

# 1100: jmp addr (Абсолютный переход, адрес лежит в IR)
# Требует аппаратного сигнала загрузки PC из IR. Назовем его PC_LOAD_IR.
# Если у тебя его нет в списке сигналов, адрес можно прокинуть через шину данных за 2 подтакта,
# но правильнее иметь жесткий сигнал PC_LOAD_IR. Добавим его абстрактно:
MICROCODE[0xC] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["PC_RD", "upc_clr"] 
]

# 1101: jnxy (PC = X:Y)
MICROCODE[0xD] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["PC_RD", "PC_SRC", "upc_clr"]
]

# Условные переходы (jz, jc)
# Используют uPC_COND_CLR (сброс микропрограммного счетчика), если флаг не валиден.
# Если флаг истинен, автомат идет на Такт 3 и делает прыжок.

# 1110: jz addr
MICROCODE[0xE] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["cond_upc_clr"],
    ["PC_RD", "upc_clr"]
]

# 1111: jc addr
MICROCODE[0xF] = [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["cond_upc_clr"],
    ["PC_RD", "upc_clr"]
]

# Define the field mappings based on your specification
FIELD_DEFINITIONS = {
    # ROM0: Младший байт (Шина данных и память)
    "src_data":          {"bits": (0, 3), "value": 0},  # 4 бита: Z, a, b, x, y, alu, shr, imm8, external
    "dst_data":          {"bits": (4, 6), "value": 0},  # 3 бита: None, a, b, x, y
    "MEM_OE":            {"bits": (7, 7), "value": 1},


    "MEM_WE":            {"bits": (8, 8), "value": 1},
    # ROM1: Старший байт (Адресный движок и переходы)
    "src_addr":          {"bits": (9, 9), "value": 1},  # 0 = PC, 1 = X:Y
    "PC_INC":            {"bits": (10, 10), "value": 1},
    "PC_RD":             {"bits": (11, 11), "value": 1},
    "PC_SRC":            {"bits": (12, 12), "value": 1}, # 0 = imm, 1 = x:y
    "IR0_READ_DBUS":     {"bits": (13, 13), "value": 1},
    "IR1_READ_DBUS":     {"bits": (14, 14), "value": 1},
    "CLK_X":             {"bits": (15, 15), "value": 1}, # Используется для inc
    
    "CLK_Y":             {"bits": (16, 16), "value": 1}, # Используется для inc
    "FLAGS_WE":          {"bits": (17, 17), "value": 1}, # Гейтинг флагов
    "upc_clr":           {"bits": (18, 18), "value": 1},
    "cond_upc_clr":      {"bits": (19, 19), "value": 1}, # нужен для обрывания выполнения инструкции если условие не выполнено.
}
