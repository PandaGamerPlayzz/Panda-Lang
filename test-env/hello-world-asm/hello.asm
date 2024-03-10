default rel

extern GetStdHandle
extern WriteConsoleA
extern ExitProcess

section .data
    message db 'Hello, World!',13,10    ; Message followed by carriage return and newline
    messageLen equ $ - message          ; Length of the message

section .text
global main

main:
    ; Get STDOUT handle
    mov ecx, -11                        ; STD_OUTPUT_HANDLE constant
    call GetStdHandle
    mov rdi, rax                        ; Save STDOUT handle in RDI for later use

    ; Prepare WriteConsoleA parameters
    mov rcx, rdi                        ; First parameter: STDOUT handle
    lea rdx, [message]                  ; Second parameter: pointer to message
    mov r8d, messageLen                 ; Third parameter: message length
    sub rsp, 40                         ; Shadow space for WriteConsoleA and space for 5th parameter
    lea r9, [rsp+32]                    ; Fourth parameter: pointer to variable to receive number of chars written
    xor [rsp+32], rax                   ; Zero out the memory where the number of chars written will be stored

    call WriteConsoleA                  ; Write message to STDOUT

    add rsp, 40                         ; Realign the stack

    ; Exit the process
    xor ecx, ecx                        ; Exit code 0
    call ExitProcess
