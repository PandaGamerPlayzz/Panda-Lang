section .text
global _start

_start:
    mov rax, 60 ; syscall code for exit
    mov rdi, 69 ; exit code
    syscall
    
    ; default to exiting with 0
    mov rax, 60 ; syscall code for exit
    mov rdi, 0 ; exit code
    syscall
    
