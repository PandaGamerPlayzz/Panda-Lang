# The Panda-Lang Compiler
Written by Zachary A. Miller

## Setup
The Panda Compiler is written in python. It first transpiles to assembly, then uses NASM and runs the linker to provide you with an executable.

Requirements:
- Python 3.10.12 or greater

Usage: panda.py [-h] [-a] [-r] [-t] file_path

Positional arguments:\n
  file_path   The path to the file you would like to compile

Options:\n
  -h, --help  show the help message and exit
  -a          Generate all files along with the executable (.asm, .o, .obj, etc.)
  -r          Run the code after compiling
  -t          Only run the tokenizer step