import io
import os
import subprocess
import tempfile

from parse import AST_NODE_TYPE

class Program:
    def __init__(self, assembly_source: str) -> None:
        self.assembly_source = assembly_source
        self.executable_path = None

    def compile(self, output_path: str, full_output=False):
        base_name = os.path.splitext(os.path.basename(output_path))[0]
        dir_name = os.path.dirname(output_path) or '.'
        asm_filename = os.path.join(dir_name, f"{base_name}.asm") if full_output else tempfile.mktemp(suffix='.asm', dir=dir_name)
        obj_filename = os.path.join(dir_name, f"{base_name}.o") if full_output else tempfile.mktemp(suffix='.o', dir=dir_name)
        
        try:
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
            if not full_output:
                if os.path.exists(asm_filename):
                    os.remove(asm_filename)
                if os.path.exists(obj_filename):
                    os.remove(obj_filename)

    def run(self):
        """
        Executes the compiled program.
        """
        if self.executable_path and os.path.exists(self.executable_path):
            result = subprocess.run([self.executable_path], capture_output=True, text=True)
            print("Program output:", result.stdout)
        else:
            print("Executable does not exist. Please compile the program first.")

class Generator:
    @staticmethod
    def generate_assembly_elf64(ast_nodes):
        with io.StringIO() as stream:
            stream.write("section .text\n")
            stream.write("    global _start\n\n")
            stream.write("_start:\n")
            for node in ast_nodes:
                if node.type == AST_NODE_TYPE.EXIT:
                    stream.write("    mov rax, 60         ; syscall number for exit\n")
                    stream.write(f"    mov rdi, {node.value} ; exit code\n")
                    stream.write("    syscall             ; perform the system call\n\n")
                elif node.type == AST_NODE_TYPE.NO_OP:
                    # Handle no operation for NO_OP nodes
                    continue
            # Return a Program instance instead of raw assembly string
            return Program(stream.getvalue())