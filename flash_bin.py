"""
┌─────────────────────────────────┐
│ Program a .bin file using PyOCD │
└─────────────────────────────────┘

 Florian Dupeyron
 May 2022
"""

import loggging

from   argparse import ArgumentParser
from   pathlib  import Path

from   pyocd.flash.file_programmer import FileProgrammer
from   pyocd.core.helpers          import ConnectHelper

def _arg_file(fpath):
    fpath = Path(fpath)

    if not fpath.is_file(): return ValueError(f"{fpath} is not a regular file")
    else:                   return fpath

if __name__ == "__main__":
    parser = ArgumentParser(description="Flash a bin using first available probe, using PyOCD")
    parser.add_argument("bin_file", type=_arg_file, help="Binary file")
    parser.add_argument("offset"  , type=int        help="Offset to program the .bin file at")

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

        # Reset halt
        target.reset_and_halt()

        # Program the .bin file
        FileProgrammer(session).program(str(args.bin_file), base_address = args.offset)

        # Reset, run
        target.reset_and_halt()
        target.resume()
