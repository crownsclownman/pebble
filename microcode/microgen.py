#!/usr/bin/env python3
import argparse
import os
from typing import List, Dict
from microdef import *

# Функция для вычисления адреса
def get_address(opcode: int, uPC: int, max_uPC_steps: int) -> int:
    return (opcode * max_uPC_steps) + uPC

# Вспомогательная функция для форматирования Intel HEX строки
def intel_hex_record(address: int, data: List[int], record_type: int = 0) -> str:
    byte_count = len(data)
    checksum = byte_count + (address >> 8) + (address & 0xFF) + record_type
    hex_data = ''.join(f"{byte:02X}" for byte in data)
    for byte in data:
        checksum += byte
    checksum = (-checksum) & 0xFF
    return f":{byte_count:02X}{address:04X}{record_type:02X}{hex_data}{checksum:02X}\n"

def build_microinstruction(fields: List[str]) -> int:
    instruction = 0
    for field_spec in fields:
        if '=' in field_spec:
            field_name, value = field_spec.split('=', 1)
            field_name, value = field_name.strip(), int(value)
        else:
            field_name = field_spec.strip()
            value = FIELD_DEFINITIONS[field_name]["value"]
        
        if field_name not in FIELD_DEFINITIONS:
            raise ValueError(f"Unknown field: {field_name}")
        
        start_bit, end_bit = FIELD_DEFINITIONS[field_name]["bits"]
        instruction |= (value << start_bit)
    return instruction

def generate_microcode_rom(microcode: Dict[int, List[List[str]]], max_uPC_steps: int) -> List[int]:
    rom_size = 256 * max_uPC_steps
    rom = [0] * rom_size
    for opcode, uPC_steps in microcode.items():
        for uPC, fields in enumerate(uPC_steps):
            if uPC >= max_uPC_steps: break
            addr = get_address(opcode, uPC, max_uPC_steps)
            if addr < rom_size:
                rom[addr] = build_microinstruction(fields)
    return rom

def generate_hex_files(rom_data: List[int], output_prefix: str, rom_width: int):
    os.makedirs(os.path.dirname(output_prefix) if os.path.dirname(output_prefix) else '.', exist_ok=True)
    
    for byte_idx in range(rom_width):
        filename = f"{output_prefix}_ROM{byte_idx}.hex"
        with open(filename, 'w') as f:
            # Разбиваем ROM на блоки по 16 байт для записей HEX
            for base_addr in range(0, len(rom_data), 16):
                chunk = rom_data[base_addr : base_addr + 16]
                bytes_to_write = [(word >> (byte_idx * 8)) & 0xFF for word in chunk]
                f.write(intel_hex_record(base_addr, bytes_to_write))
            
            # Завершающая запись
            f.write(":00000001FF\n")
            
        print(f"Generated: {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="rom")
    parser.add_argument("-w", "--rom-width", type=int, default=2)
    parser.add_argument("-m", "--max-upc", type=int, default=16)
    args = parser.parse_args()
    
    rom_data = generate_microcode_rom(MICROCODE, args.max_upc)
    generate_hex_files(rom_data, args.output, args.rom_width)
    
    print(f"\nSummary:")
    print(f"  ROM size: {len(rom_data)} words")
    print(f"  Width: {args.rom_width} bytes")
    print(f"  Total bytes: {len(rom_data) * args.rom_width}")

if __name__ == "__main__":
    main()
