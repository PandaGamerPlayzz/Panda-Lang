import io
import os
import sys
import subprocess
import tempfile

from parse import AST_NODE_TYPE

ALWAYS_DEFAULT_EXIT_WITH_0 = False

class Program:
    def __init__(self, assembly_source: str) -> None:
        self.assembly_source = assembly_source
        self.executable_path = None

    def compile(self, output_path: str, full_output=False):
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        # Ensure dir_name is only the directory part of output_path
        dir_name = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'

        # Correct handling for relative paths like './tests/test.pnda/..'
        dir_name = os.path.normpath(dir_name)  # Normalize the path to resolve '..'

        # Generate the filenames for assembly and object files
        asm_filename = os.path.join(dir_name, f"{base_name}.asm") if full_output else tempfile.mktemp(suffix='.asm', dir=dir_name)
        obj_filename = os.path.join(dir_name, f"{base_name}.o") if full_output else tempfile.mktemp(suffix='.o', dir=dir_name)

        # Ensure the directory exists
        os.makedirs(dir_name, exist_ok=True)

        try:
            # Write assembly source to file
            with open(asm_filename, 'w') as asm_file:
                asm_file.write(self.assembly_source)

            # Assemble with NASM
            subprocess.run(["nasm", "-f", "elf64", "-o", obj_filename, asm_filename], check=True, stderr=subprocess.PIPE)

            # Link with ld
            self.executable_path = os.path.abspath(output_path)
            subprocess.run(["ld", "-o", self.executable_path, obj_filename], check=True, stderr=subprocess.PIPE)

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

class Generator:
    @staticmethod
    def generate_assembly_elf64(ast_nodes):
        with io.StringIO() as stream:
            stream.write("section .text\n")
            stream.write("    global _start\n\n")
            stream.write("_start:\n")

            exit_processed = False

            for node in ast_nodes:
                if node.type == AST_NODE_TYPE.EXIT:
                    stream.write("    mov rax, 60 ; syscall number for exit\n")
                    stream.write(f"    mov rdi, {node.value} ; exit code\n")
                    stream.write("    syscall ; perform the system call\n\n")
                    exit_processed = True
            
            if not exit_processed or ALWAYS_DEFAULT_EXIT_WITH_0:
                stream.write("    ; default to exiting with 0\n")
                stream.write("    mov rax, 60 ; syscall number for exit\n")
                stream.write("    mov rdi, 0 ; exit code\n")
                stream.write("    syscall ; perform the system call\n\n")

            return Program(stream.getvalue())