import os
import argparse
import pprint

from tokenizer import Tokenizer
from parse import Parser
from generator import Generator

def main() -> None:
    arg_parser = argparse.ArgumentParser(description='A compiler for the Panda programming language')

    arg_parser.add_argument('-a', action='store_true', help='Generate all files (.asm, .o, .obj, etc.)')
    arg_parser.add_argument('-r', action='store_true', help='Run the code after compiling')
    arg_parser.add_argument('-t', action='store_true', help='Only run the tokenizer step')
    arg_parser.add_argument('file_path', type=str, help='The path to the file you would like to compile')

    args = arg_parser.parse_args()

    if not os.path.isfile(args.file_path):
        print(f"Error: The file '{args.file_path}' does not exist.")
        return

    program_tokenizer = Tokenizer()
    program_tokens = program_tokenizer.tokenize(args.file_path)

    if args.t == True:
        pprint.pprint(program_tokens.tokens)
        return

    program_parser = Parser(program_tokens)
    program_ast = program_parser.parse()

    program = Generator.generate_assembly_elf64(program_ast)

    output_path = os.path.join(args.file_path, '../', os.path.splitext(os.path.basename(args.file_path))[0])
    program.compile(output_path, full_output=args.a)
    if args.r == True: program.run()

if __name__ == '__main__':
    main()
