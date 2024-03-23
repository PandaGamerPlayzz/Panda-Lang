import io
import os
import sys
import subprocess
import tempfile
from enum import Enum, auto

from parse import AST_NODE_TYPE
from version import VERSION

ALWAYS_DEFAULT_EXIT_WITH_0 = True
USE_ABSOLUTE_INCLUDE_PATH = True
REBUILD_LIB = True

class ASSEMBLER(Enum):
    NASM = auto()

class Program:
    def __init__(self, assembly_source: str, program_name: str = None) -> None:
        self.assembly_source = assembly_source
        self.executable_path = None
        self.program_name = program_name
        self.child_programs = []

    def add_child(self, child_program):
        self.child_programs.append(child_program)

    def compile(self, output_path: str, full_output=False):
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        # Ensure dir_name is only the directory part of output_path
        dir_name = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'

        # Correct handling for relative paths like './tests/test.pnda/..'
        dir_name = os.path.normpath(dir_name)  # Normalize the path to resolve '..'

        output_folder_path = os.path.normpath(os.path.join(dir_name, 'output/'))
        lib_path = os.path.normpath(os.path.join(output_folder_path, 'lib/'))

        object_filenames = []

        if USE_ABSOLUTE_INCLUDE_PATH == True:
            self.assembly_source = self.assembly_source.replace("#{LIB_DIRECTORY}", os.path.abspath(lib_path) + "/")
        else:
            self.assembly_source = self.assembly_source.replace("#{LIB_DIRECTORY}", "lib/")

        # Ensure the directory exists
        os.makedirs(dir_name, exist_ok=True)
        os.makedirs(lib_path, exist_ok=True)

        for child_program in self.child_programs:
            child_program.compile(output_path, full_output)    

        if self.program_name == None:
            # Generate the filenames for assembly and object files
            asm_filename = os.path.join(output_folder_path, f"{base_name}.asm") if full_output else tempfile.mktemp(suffix='.asm', dir=dir_name)
            obj_filename = os.path.join(output_folder_path, f"{base_name}.o") if full_output else tempfile.mktemp(suffix='.o', dir=dir_name)

            object_filenames.append(obj_filename)
            print(object_filenames)

            try:
                # Write assembly source to file
                with open(asm_filename, 'w') as asm_file:
                    asm_file.write(self.assembly_source)

                # Assemble with NASM
                subprocess.run(["nasm", "-f", "elf64", "-o", obj_filename, asm_filename], check=True, stderr=subprocess.PIPE)

                self.link(output_path, object_filenames, full_output=full_output)

            except subprocess.CalledProcessError as e:
                print(f"Error during {'assembly' if 'nasm' in e.cmd else 'linking'}:")
                print(e.stderr.decode())
                raise

            finally:
                # Cleanup temporary files if not in full_output mode
                if not full_output:
                    if os.path.exists(asm_filename):
                        os.remove(asm_filename)
                    if os.path.exists(obj_filename):
                        os.remove(obj_filename)

                if not os.listdir(lib_path): os.rmdir(lib_path)
                if not os.listdir(output_folder_path): os.rmdir(output_folder_path)
        else:
            # Generate the filenames for assembly and object files
            asm_filename = os.path.join(lib_path, f"{self.program_name}.asm") if full_output else tempfile.mktemp(suffix='.asm', dir=dir_name)
            obj_filename = os.path.join(lib_path, f"{self.program_name}.o") if full_output else tempfile.mktemp(suffix='.o', dir=dir_name)

            try:
                with open(asm_filename, 'w') as asm_file:
                    asm_file.write(self.assembly_source)

                # Assemble with NASM
                subprocess.run(["nasm", "-f", "elf64", "-o", obj_filename, asm_filename], check=True, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                print(f"Error during generation:")
                print(e.stderr.decode())
                raise
            finally:
                if not full_output and os.path.exists(asm_filename): os.remove(asm_filename)

    def link(self, output_path, object_filenames, full_output=False):
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        # Ensure dir_name is only the directory part of output_path
        dir_name = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'

        # Correct handling for relative paths like './tests/test.pnda/..'
        dir_name = os.path.normpath(dir_name)  # Normalize the path to resolve '..'

        output_folder_path = os.path.normpath(os.path.join(dir_name, 'output/'))
        lib_path = os.path.normpath(os.path.join(output_folder_path, 'lib/'))

        # TODO add builtins-elf64.0 to link with ld
        # Link with ld
        self.executable_path = os.path.abspath(output_path)
        subprocess.run(["ld", "-o", self.executable_path, object_filenames[0]], check=True, stderr=subprocess.PIPE)

    def run(self):
        """
        Executes the compiled program and prints its exit code.
        """
        if self.executable_path and os.path.exists(self.executable_path):
            print(f"Executing {os.path.abspath(self.executable_path)}...")

            with subprocess.Popen([self.executable_path], stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin) as process:
                process.wait()  # Wait for the process to complete
                # After the process has completed, print the exit code
                print(f"Process exited with code {process.returncode}")
        else:
            print("Executable does not exist. Please compile the program first.")

class StringStream:
    def __init__(self, indent_level=0) -> None:
        self.indent_level = indent_level
        self.stream = io.StringIO()

    def increase_indent(self) -> None:
        self.indent_level += 4

    def decrease_indent(self) -> None:
        self.indent_level = max(0, self.indent_level - 4)

    def write(self, text) -> None:
        indented_text = ' ' * self.indent_level + text + '\n'
        self.stream.write(indented_text)

    def close(self) -> None:
        self.stream.close()

    def get_value(self) -> str:
        return self.stream.getvalue()
    
    def trim_trailing_newlines(self):
        """
        Trim trailing newlines from the stream's content.
        """
        content = self.stream.getvalue()
        trimmed_content = content.rstrip('\n')
        self.close()
        self.stream = io.StringIO(trimmed_content)

class Section(StringStream):
    def __init__(self, label, indent_level=4) -> None:
        super().__init__(indent_level)

        self.indent_level = 0
        self.write(label)
        self.indent_level = indent_level

class MacroSection(Section):
    def __init__(self, label, argc, indent_level=4) -> None:
        super().__init__(f"%macro {label} {argc}", indent_level)

    def end_macro(self):
        self.decrease_indent()
        self.write("%endmacro")

class GeneratorNASM(StringStream):
    def __init__(self) -> None:
        super().__init__(indent_level=0)
        self.assembler = ASSEMBLER.NASM

    def write_section(self, section: Section, close: bool = True, trim: bool = False) -> None:
        if type(section) is MacroSection: section.end_macro()
        if trim == True: section.trim_trailing_newlines()
        self.write(section.get_value())        
        if close == True: section.close()

    def generate_assembly_elf64(self, ast_nodes) -> Program:
        self.write(f"; Transpiled using Panda-Lang v{VERSION}")
        self.write( "; Linux x86_64: elf64\n")

        # section .bss
        # section_bss = Section("section .bss")
        # section_bss.write('a resb 8')
        # self.write_section(section_bss)

        # section .data
        section_data = Section("section .data")
        
        for i, node in enumerate(ast_nodes):
            if node.type == AST_NODE_TYPE.PRINT:
                section_data.write(f'_cs{i} db "{node.value}",10,0')

        self.write_section(section_data)

        # section .text
        section_text = Section("section .text")
        section_text.write("global _start")
        self.write_section(section_text)

        # macro test
        # section_macro = MacroSection("exit", 0)
        # section_macro.write("mov rax, 60")
        # section_macro.write("mov rdi, 0")
        # section_macro.write("syscall")
        # self.write_section(section_macro)

        # Open and input methods from "src/lib/builtins-elf64.asm"
        builtins = None
        if REBUILD_LIB == True:
            builtins_asm = StringStream()
            with open(os.path.join(os.path.split(__file__)[0], "lib/builtins-elf64.asm"), "r") as elf64_builtins:
                skipping = False
                for line in elf64_builtins:
                    if line.strip() == ";; begin .bss":
                        skipping = True
                    elif line.strip() == ";; end .bss":
                        skipping = False

                    if skipping == True: continue

                    if not line.startswith(";;"):
                        builtins_asm.write(line.rstrip('\n'))
                builtins_asm.write("")
            
            builtins = Program(builtins_asm.get_value(), "builtins-elf64")
            builtins_asm.close()
            self.write(f"%include \"{'#{LIB_DIRECTORY}builtins-elf64.asm'}\"\n")
        else:
            lib_builtins_path = os.path.abspath(os.path.join(__file__, "../lib/builtins-elf64.asm"))
            self.write(f"%include \"{lib_builtins_path}\"\n")

        # User defined code
        # _start:
        section__start = Section("_start:")
        
        exit_processed = False

        for i, node in enumerate(ast_nodes):
            if node.type == AST_NODE_TYPE.EXIT:
                section__start.write(f"exit {node.value}")
                # section__start.write("mov rax, 60 ; syscall code for exit")
                # section__start.write(f"mov rdi, {node.value} ; exit code")
                # section__start.write("syscall")
                section__start.write("")
                exit_processed = True
            elif node.type == AST_NODE_TYPE.PRINT:
                # section__start.write(f"mov rax, _cs{i}")
                # section__start.write("call _print")
                section__start.write(f"print _cs{i}")
                section__start.write("")

        if not exit_processed or ALWAYS_DEFAULT_EXIT_WITH_0:
            section__start.write("exit 0 ; default to exiting with 0")
            # section__start.write("mov rax, 60 ; syscall code for exit")
            # section__start.write("mov rdi, 0 ; exit code")
            # section__start.write("syscall")
            section__start.write("")

        self.write_section(section__start, trim=True)

        # Create and return the program
        program = Program(self.get_value().rstrip("\n"))
        if builtins: program.add_child(builtins)
        self.close()

        return program

def Generator(assembler: ASSEMBLER = ASSEMBLER.NASM):
    match assembler:
        case ASSEMBLER.NASM:
            return GeneratorNASM()