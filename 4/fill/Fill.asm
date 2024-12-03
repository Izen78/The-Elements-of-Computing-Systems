// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.


// DOESN'T WORK TOO WELL BECAUSE OF KBD CHECK LOGIC

@8192
D=A
@R0
M=D // C-statement

D=0
@R1
M=D

@KBD
M=0

(LOOP)
// reset
@R1

@KBD
D=M

@RESET
D;JNE

(AFTER_RESET)
@KBD
M=0

@KBD
D=M

@KEY_PRESSED
D;JNE

@LOOP
0;JMP
(END)

(KEY_PRESSED)
@R1
M=0

(KEY_LOOP)
@R0 // 8192
D=M //  D=8192
@R1 // 1
D=D-M // D=8192-1
@LOOP
D;JEQ // if D is 8192 then go back to main loop

@R1
D=M // D=1
@SCREEN
A=A+D // screen=screen+1
M=-1 
@R1
D=D+1 // D = 2
M=D // R1 <- 2

@KEY_LOOP
0;JMP


(RESET) // make sure kbd is set to 0 after
@R1
M=0

(RESET_LOOP)
@R0 // 8192
D=M
@R1
D=D-M // check 8192 - R1
@AFTER_RESET
D;JEQ

@R1
D=M
@SCREEN
A=A+D
M=0
D=D+1
@R1
M=D

@RESET_LOOP
0;JMP
