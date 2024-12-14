"""
VM Implementation of The Elements of Computing System

author: Arpon Sarker
date: 7-12-2024
"""

import cmd
import os
from enum import Enum

# 1. Gather a .vm single file or a directory of .vm files to be translated into ONE assembly file
# 2. Assuming local, argument and static variables are already set up from high-level language compilation
# 3. Local and Argument should be initialised in different places
# 4. This and That should be initialised in different places

# Focus on Arithmetic commands
#


class COMMAND_TYPE(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8


class VM_CLI(cmd.Cmd):

    prompt = "prompt> "
    intro = "VM Translator for Hack VM language"

    def do_help(self, arg: str) -> bool | None:
        """You are in this command now?"""
        return super().do_help(arg)

    def do_VMtranslator(self, line):
        """Converts source .vm file or directory of files to .asm file"""
        main(line)

    def do_quit(self, line):
        """Exit the CLI."""
        return True


class Parser:  # returns the classification of tokens
    current_command = ""
    line = ""
    tokens = []  # contains each word in current command
    command_type = None
    arg_1 = None
    arg_2 = None

    def __init__(self, in_line: str):
        self.line = in_line
        self.advance()

    def hasMoreCommands(self) -> bool:  # test if commented or blank line
        if "//" in self.line or len(self.line) == 0:
            return False
        return True

    def advance(self):
        if self.hasMoreCommands() == False:  # line is not comment or blank
            return
        # set current command to current line being read
        self.current_command = self.line
        self.commandType()
        if self.current_command != COMMAND_TYPE.C_RETURN:
            self.arg_1 = self.arg1()
        if self.command_type in (
            COMMAND_TYPE.C_PUSH,
            COMMAND_TYPE.C_POP,
            COMMAND_TYPE.C_FUNCTION,
            COMMAND_TYPE.C_CALL,
        ):
            self.arg_2 = self.arg2()

    def commandType(self):
        arithmetic_commands = [
            "add",
            "sub",
            "neg",
            "eq",
            "gt",
            "lt",
            "and",
            "or",
            "not",
        ]
        self.tokens = self.current_command.split(" ")
        operator = self.tokens[0]
        if operator in arithmetic_commands:
            self.command_type = COMMAND_TYPE.C_ARITHMETIC
        elif operator == "push":
            self.command_type = COMMAND_TYPE.C_PUSH
        elif operator == "pop":
            self.command_type = COMMAND_TYPE.C_POP
        elif operator == "label":
            self.command_type = COMMAND_TYPE.C_LABEL
        elif operator == "goto":
            self.command_type = COMMAND_TYPE.C_GOTO
        elif operator == "if-goto":
            self.command_type = COMMAND_TYPE.C_IF
        elif operator == "function":
            self.command_type = COMMAND_TYPE.C_FUNCTION
        elif operator == "return":
            self.command_type = COMMAND_TYPE.C_RETURN
        elif operator == "call":
            self.command_type = COMMAND_TYPE.C_CALL
        else:
            print("ERROR: COMMAND TYPE IS INVALID")
            self.command_type = None

    def arg1(self):
        arg = ""
        if self.command_type == COMMAND_TYPE.C_ARITHMETIC:
            arg = self.tokens[0]
        else:
            arg = self.tokens[1]
        return arg

    def arg2(self):
        return self.tokens[2]


class CodeWriter:  # returns the assembly encodings
    file_stream = ""
    file_created = False
    assembly = "@256\nD=A\n@SP\nM=D\n"
    index = 0

    def __init__(self, ostream):
        self.file_stream = ostream
        if self.file_stream in os.listdir():  # if file already created
            self.file_created = True

    # Opens and sets up file stream
    def setFilename(self, file_name: str):
        file_name += ".asm"
        # All the write methods have been used outside and so self.assembly is already full
        self.f = open(file_name, "w")
        self.f.write(self.assembly)
        self.Close()

    def writeArithmetic(self, command):
        # bivariate = {"add":"+", "sub":"-"}
        # Labels are ROM addresses not RAM addresses. Therefore, no conflicts.
        if command == "add":
            self.assembly += "@SP\nA=M-1\nD=M\nA=A-1\nD=D+M\nM=D\nD=A+1\n@SP\nM=D\n"
        elif command == "sub":
            self.assembly += "@SP\nA=M-1\nD=M\nA=A-1\nD=M-D\nM=D\nD=A+1\n@SP\nM=D\n"
        elif command == "neg":
            self.assembly += "@SP\nA=M\nA=A-1\nM=-M\n"
        elif command == "eq":
            self.assembly += "@SP\nD=M\n@2\nD=D-A\n@R13\nM=D\nA=M\nD=M\nA=A+1\nD=D-M\n@EQ" + str(self.index) + "\nD;JEQ\n@R13\nA=M\nM=0\n@END" + str(self.index) + "\n0;JMP\n(EQ" + str(self.index) + ")\n@R13\nA=M\nM=-1\n(END" + str(self.index) +")\n@SP\nM=M-1\n"
        elif command == "gt":
            self.assembly += "@SP\nD=M\n@2\nD=D-A\n@R13\nM=D\nA=M\nD=M\nA=A+1\nD=D-M\n@GT" + str(self.index) + "\nD;JGT\n@R13\nA=M\nM=0\n@END" + str(self.index) + "\n0;JMP\n(GT" + str(self.index) + ")\n@R13\nA=M\nM=-1\n(END" + str(self.index) +")\n@SP\nM=M-1\n"
        elif command == "lt":
            self.assembly += "@SP\nD=M\n@2\nD=D-A\n@R13\nM=D\nA=M\nD=M\nA=A+1\nD=D-M\n@LT" + str(self.index) + "\nD;JLT\n@R13\nA=M\nM=0\n@END" + str(self.index) + "\n0;JMP\n(LT" + str(self.index) + ")\n@R13\nA=M\nM=-1\n(END" + str(self.index) +")\n@SP\nM=M-1\n"
        elif command == "and":
            self.assembly += "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=D&M\n"
        elif command == "or":
            self.assembly += "@SP\nM=M-1\nA=M\nD=M\nA=A-1\nM=D|M\n"
        elif command == "not":
            self.assembly += "@SP\nD=M-1\nA=D\nM=!M\n"
        else:
            print("NOT VALID COMMAND")

        self.index += 1

    def WritePushPop(self, command, segment, index):
        segment_assembly = {"local": "LCL", "argument":"ARG", "this":"THIS", "that":"THAT", "temp":"R5"}
        if command == "push" and segment == "constant":
            print("constant statement")
            self.assembly += "@" + str(index) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        elif command == "push" and (segment == "pointer" or segment == "static"):
            print("push pointer/static statement")
            reg = "R3" if segment == "pointer" else "16"
            self.assembly += "@" + reg + "\nD=A\n@" + str(index) + "\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        elif command == "push":
            print("push statement")
            self.assembly += "@" + segment_assembly[segment] + "\nD=M\n@" + str(index) + "\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


        # if command == "pop" and segment == "temp":
        #     self.assembly += "@R5\nD=A\n@" + str(index) + "\nD=D+A\n@R13\nM=D\n@SP\nA=A-1\nD=M\n@R13\nA=M\nM=D\n@SP\nM=M-1\n" 
        if command == "pop" and (segment == "pointer" or segment == "static"):
            print("pop pointer/static statement")
            reg = "R3" if segment == "pointer" else "16"
            self.assembly += "@" + reg + "\nD=A\n@" + str(index) + "\nD=D+A\n@R13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n"
        elif command == "pop":
            print("pop statement")
            self.assembly += "@" + segment_assembly[segment] + "\nD=M\n@" + str(index) + "\nD=D+A\n@R13\nM=D\n@SP\nA=M-1\nD=M\n@R13\nA=M\nM=D\n@SP\nM=M-1\n" 
            

    def Close(self):
        self.f.close()

def main(file):  # check if it is a single file or directory
    input_file = file  # assuming it is a single file

    i = 0
    coder = CodeWriter("test.asm")
    with open(input_file, "r") as file:
        for line in file:
            if line[-1] == "\n":
                line = line[:-1]
            # print(i, ": ", line) # copies \n
            # print(i)
            i += 1
            parser = Parser(line)

            if parser.command_type == COMMAND_TYPE.C_ARITHMETIC:
                coder.writeArithmetic(parser.tokens[0])
            elif (
                parser.command_type == COMMAND_TYPE.C_PUSH
                or parser.command_type == COMMAND_TYPE.C_POP
            ):
                coder.WritePushPop(parser.tokens[0], parser.arg_1, parser.arg_2)
    coder.setFilename("test")


if __name__ == "__main__":
    VM_CLI().cmdloop()
# VMtranslator test.vm
