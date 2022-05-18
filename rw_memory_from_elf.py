"""
┌───────────────────────────────────────────────────────────────┐
│ Read symbols from an .elf file, read and write a given symbol │
└───────────────────────────────────────────────────────────────┘

 Florian Dupeyron
 May 2022
"""

import logging

from pathlib  import Path
from argparse import ArgumentParser

from pyocd.core.helpers import ConnectHelper

def _arg_file(fpath):
    fpath = Path(fpath)

    if not fpath.is_file(): return ValueError(f"{fpath} is not a regular file")
    else:                   return fpath

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser(description="Modify some symbol based on an ELF file and value")
    parser.add_argument("elf_file",    type=_arg_file, help="Path to ELF file"             )
    parser.add_argument("symbol_name", type=str      , help="Name of the symbol to modify" )
    parser.add_argument("value"      , type=int      , help="Value to write in memory"     )

    args = parser.parse_args()

    # The ConnectHelper shows a prompt to select the desired probe
    # when multiple probes are plugged in. 
    # To specify a specific target board:
    # ConnectHelper.session_with_chosen_probe(target_override="stm32f746bgtx")
    # => The corresponding CMSIS-PACK must be installed!
    with ConnectHelper.session_with_chosen_probe() as session:
        # Retrieve board and target
        board  = session.board
        target = board.target

        # Load the ELF file.
        # Putting the file name in the class field transforms it to a
        # pyocd.debug.elf.elf.ELFBinaryFile automatically. This kinda dirty
        target.elf = str(args.elf_file)

        # Find the desired symbol information
        # class type is pyocd.debug.elf.decoder.SymbolInfo, which is a named tuple.
        symbol_info = target.elf.symbol_decoder.get_symbol_for_name(str(args.symbol_name))

        log.info(f"Found symbol: {symbol_info}")
        
        # Read the memory prior to modification
        # Various methods are available to read/write memory:
        # -> read8/write8  : 8  bits transfer (results as an int for a read)
        # -> read16/write16: 16 bits transfer (results as an int for a read)
        # -> read32/write32: 32 bits transfer (results as an int for a read)
        # -> read_memory/write_memory: 8/16/32 bits transfer
        #
        # For a transfer that is more than these sizes:
        # -> read_block8/16/32 or write_block/16/32: Reads/Writes with chunks of 8/16/32 bytes, which are list of ints

        data = target.read_memory_block8(addr=symbol_info.address, transfer_size=symbol_info.size)
        log.info(f"Memory prior to modification: {data}")

        # Cut the input data in chunks of 8 bits
        w_data = args.value.to_bytes(symbol_info.size, "big")

        # Write the data!
        target.write_memory_block8(addr=symbol_info.address, w_data)

        # Read the data back
        data = target.read_memory_block8(addr=symbol_info.address, transfer_size=symbol_info.size)
        log.info(f"Memory after modification: {data}")
        
