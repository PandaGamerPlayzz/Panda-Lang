; Transpiled using Panda-Lang v1.0.0
; Linux x86_64: elf64

section .data
    _cs0 db "Hello, World!",10,0

section .text
    global _start

%include "/mnt/c/Users/Zach/Documents/.dev/Github/Panda-Lang/src/tests/output/lib/builtins-elf64.asm"

_start:
    print _cs0
    
    exit 69
    
    exit 0 ; default to exiting with 0
    