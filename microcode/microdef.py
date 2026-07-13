#!/usr/bin/env python3

from dataclasses import dataclass

# -----------------------------
# Fetch
# -----------------------------

FIRST_BYTE_FETCH = [
    "src_addr=0",
    "src_data=10",
    "MEM_OE",
    "IR0_READ_DBUS",
    "PC_INC",
]

SECOND_BYTE_FETCH = [
    "src_addr=0",
    "src_data=10",
    "MEM_OE",
    "IR1_READ_DBUS",
    "PC_INC",
]

# -----------------------------
# Поля микроинструкции
# -----------------------------

FIELD_DEFINITIONS = {
    "src_data": (0, 4),
    "dst_data": (4, 3),
    "MEM_OE": (7, 1),

    "MEM_WE": (8, 1),
    "src_addr": (9, 2),
    "PC_INC": (11, 1),
    "PC_RD": (12, 1),
    "PC_SRC": (13, 2),
    "IR0_READ_DBUS": (15, 1),
    "IR1_READ_DBUS": (16, 1),

    "CLK_Y": (17, 1),
    "CLK_V": (18, 1),

    "FLAGS_WE": (19, 1),

    "upc_clr": (20, 1),
    "cond_upc_clr": (21, 1),
}


OPCODES = {}
EXTENSIONS = {}

SRC_Z = 0
SRC_A = 1
SRC_B = 2
SRC_X = 3
SRC_Y = 4
SRC_U = 5
SRC_V = 6
SRC_ALU = 7
SRC_SHR = 8
SRC_EXT = 9

DST_NONE = 0
DST_A = 1
DST_B = 2
DST_X = 3
DST_Y = 4
DST_U = 5
DST_V = 6

def s(src):
    return f"src_data={src}"

def d(dst):
    return f"dst_data={dst}"

def add_opcode(opcode, sequence):
    OPCODES[opcode] = sequence

def add_ext(ext, sequence):
    EXTENSIONS[ext] = sequence
add_opcode(0x4, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH + ["dst_data=1"],
    ["upc_clr"],
])

# alu
for alu_op in [0x0, 0x1, 0x2, 0x3]:
    add_opcode(alu_op, [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        ["src_data=7", "dst_data=1", "FLAGS_WE", "upc_clr"]
    ])

# ldx
add_opcode(0x5, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=3", "upc_clr"]
])

# ldy
add_opcode(0x6, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=4", "upc_clr"]
])

# ldd
add_opcode(0x7, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_addr=1", "MEM_OE", "src_data=10", "dst_data=1", "upc_clr"]
])

# std
add_opcode(0x8, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_addr=1", "MEM_WE", "src_data=1", "upc_clr"]
])

# shr
add_opcode(0xA, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=8", "dst_data=1", "FLAGS_WE", "upc_clr"]
])

# inc
add_opcode(0xB, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["CLK_Y", "upc_clr"]
])

# jmp
add_opcode(0xC, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["PC_RD", "PC_SRC=2", "upc_clr"]
])

# jnxy
add_opcode(0xD, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["PC_RD", "PC_SRC=1", "upc_clr"]
])

# jz
add_opcode(0xE, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["cond_upc_clr"],
    ["PC_RD", "PC_SRC=2", "upc_clr"]
])

# jc
add_opcode(0xF, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["cond_upc_clr"],
    ["PC_RD", "PC_SRC=2", "upc_clr"]
])

# EXT 0x000
add_ext(0x0, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=2", "upc_clr"]     # mab
])

# EXT 0x001
add_ext(0x1, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=3", "dst_data=1", "upc_clr"]     # sdx
])

# EXT 0x002
add_ext(0x2, [
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=4", "dst_data=1", "upc_clr"]     # sdy
])

add_ext(0x3, [                                  # stud
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_addr=2", "MEM_WE", "src_data=2", "upc_clr"]
])

add_ext(0x4, [                                  # ldud
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_addr=2", "MEM_OE", "src_data=10", "dst_data=1", "upc_clr"]
])

add_ext(0x5, [                                  #ldu
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=5", "upc_clr"]

])

add_ext(0x6, [                                  # ldv
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=1", "dst_data=6", "upc_clr"]
])

add_ext(0x7, [                                  # cpxy
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=3", "dst_data=5"],
    ["src_data=4", "dst_data=6"]
])

add_ext(0x8, [                                  # cpuv
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["src_data=3", "dst_data=5"],
    ["src_data=4", "dst_data=6"]
])

add_ext(0x9, [                                  # incuv
    FIRST_BYTE_FETCH,
    SECOND_BYTE_FETCH,
    ["CLK_V", "upc_clr"]
])
