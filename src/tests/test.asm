section .text
    global _start

_start:
    mov rax, 60 ; syscall number for exit
    mov rdi, 69 ; exit code
    syscall ; perform the system call

