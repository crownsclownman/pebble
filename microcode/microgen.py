#!/usr/bin/env python3

import argparse
import os
from intelhex import IntelHex

from microdef import *

def encode(fields):
    word = 0

    for item in fields:
        if "=" in item:
            name, value = item.split("=", 1)
            value = int(value, 0)
        else:
            name = item
            value = 1

        if name not in FIELD_DEFINITIONS:
            raise ValueError(f"Unknown field '{name}'")

        bit, width = FIELD_DEFINITIONS[name]

        if value >= (1 << width):
            raise ValueError(
                f"{name}={value} doesn't fit into {width} bits"
            )

        word |= value << bit

    return word

def write_hex(filename, rom):
    ih = IntelHex()

    for addr, value in enumerate(rom):
        ih[addr] = value

    ih.write_hex_file(filename)
    print(hex(max(ih.addresses())))

def write_raw_hex(filename, data):
    with open(filename, "w") as f:
        f.write("v2.0 raw\n")

        for i, b in enumerate(data):
            f.write(f"{b:02X}")

            if (i + 1) % 16 == 0:
                f.write("\n")
            else:
                f.write(" ")

def build_rom(max_upc):

    words = 65536 * max_upc

    rom = [0] * words

    for instruction in range(65536):

        opcode = instruction >> 12

        if opcode == 0x9:
            ext = (instruction >> 8) & 0xF
            seq = EXTENSIONS.get(ext)
        else:
            seq = OPCODES.get(opcode)

        if seq is None:
            seq = []

        for upc in range(max_upc):

            if upc < len(seq):
                word = encode(seq[upc])
            else:
                word = encode(["upc_clr"])

            addr = instruction * max_upc + upc

            rom[addr] = word

    return rom

def split_rom(words):
    rom0 = [(w >> 0) & 0xFF for w in words]
    rom1 = [(w >> 8) & 0xFF for w in words]
    rom2 = [(w >> 16) & 0xFF for w in words]
    return rom0, rom1, rom2

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--output",
        default="rom"
    )

    parser.add_argument(
        "-m",
        "--max-upc",
        type=int,
        default=4
    )

    args = parser.parse_args()

    rom = build_rom(args.max_upc)

    print(len(rom))
    print(hex(encode(["upc_clr"])))

    rom0, rom1, rom2 = split_rom(rom)

    os.makedirs(
        os.path.dirname(args.output) or ".",
        exist_ok=True
    )

    write_raw_hex(args.output + "_ROM0.hex", rom0)
    write_raw_hex(args.output + "_ROM1.hex", rom1)
    write_raw_hex(args.output + "_ROM2.hex", rom2)
   
    print("Done.")
    print(f"Instructions : 65536")
    print(f"uPC steps    : {args.max_upc}")
    print(f"ROM words    : {len(rom)}")
    print(f"ROM bytes    : {len(rom) * 3}")


if __name__ == "__main__":
    main()
