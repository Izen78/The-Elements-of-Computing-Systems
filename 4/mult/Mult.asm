// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.



// I want to add the values looped into R2 until R0 is 0
@R2
M=0

(LOOP)
// check if R0 is 0 and loop to end
// store R0 into D to check and use A reg to hold address of END
@R0
D=M
@END
D;JEQ

// Add R1 to R2 -> D=M[R1], A=R2, 
@R1
D=M
@R2
M=D+M // M[R2] = M[R2] + M[R1]
// Decrement R0
@R0
M=M-1

// Check R0==0, true: loop to end, false: loop to LOOP
@LOOP
0;JMP
(END)
