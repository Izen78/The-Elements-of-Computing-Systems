"""
VM Implementation Extension of The Elements of Computing System

author: Arpon Sarker
date: 15-12-2024
"""

import cmd
import os
from enum import Enum
from os.path import isdir


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
        input_file = line
        if os.path.isdir(input_file):
            # this is dir
            temp_commands = ""
            dir_files = os.listdir(input_file)
            for dir_file in dir_files:
                if dir_file[-3:] == ".vm":
                    print(dir_file)
                    with open(input_file + dir_file, "r") as file:
                        for line in file:
                            temp_commands += line
            temp_file = open("temporary.txt", "w")
            temp_file.write(temp_commands)
            temp_file.close()
            main("temporary.txt")
            # temp_file.remove()
        else:
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

    # TODO: Fix tabs and whitespace at the beginning of no comment line
    # TODO: Fix tabs and whitespace at the end of no comment line
    def hasMoreCommands(self) -> bool:  # test if blank line, end of line comment, or start of line comment
        self.line = self.line.strip()
        index = self.line.find("//")

        while index >= 0:
            if self.line[index-1] == " " or self.line[index-1] == '\t':
                index -= 1
            else:
                self.line = self.line[:index]
                break
        if len(self.line) == 0:
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
        print("TOKENS: ", self.tokens)
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
            print("ERROR: COMMAND TYPE IS INVALID for ", operator)
            self.command_type = None

    def arg1(self):
        arg = ""
        if self.command_type in (COMMAND_TYPE.C_ARITHMETIC, COMMAND_TYPE.C_RETURN):
            arg = self.tokens[0]
        else:
            arg = self.tokens[1]
        return arg

    def arg2(self):
        return self.tokens[2]


class CodeWriter:  # returns the assembly encodings
    file_stream = "" # name of file w/ .asm extension
    file_created = False
    file_name = ""
    assembly = ""
    index = 0
    function = "null"
    static_index = 16

    def __init__(self, ostream):
        self.file_stream = ostream
        if self.file_stream in os.listdir():  # if file already created
            self.file_created = True

    # Opens and sets up file stream
    def setFilename(self, file_name: str):
        self.file_name += ".asm"

        # All the write methods have been used outside and so self.assembly is already full
        self.f = open(self.file_stream, "w")
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
            self.assembly += "@SP\nD=M\n@2\nD=D-A\n@R13\nM=D\nA=M\nD=M\nA=A+1\nD=D-M\n@EQ" + str(self.index) + "\nD;JEQ\n@R13\nA=M\nM=0\n@END" + "\n0;JMP\n(EQ" + str(self.index) + ")\n@R13\nA=M\nM=-1\n(END" + str(self.index) +")\n@SP\nM=M-1\n"
        elif command == "gt":
            self.assembly += "@SP\nD=M\n@2\nD=D-A\n@R13\nM=D\nA=M\nD=M\nA=A+1\nD=D-M\n@GT" + str(self.index) + "\nD;JGT\n@R13\nA=M\nM=0\n@END" + str(self.index) + "\n0;JMP\n(GT" + str(self.index) + ")\n@R13\nA=M\nM=-1\n(END" + str(self.index) +")\n@SP\nM=M-1\n"
        elif command == "lt":
            self.assembly += "@SP\nD=M\n@2\nD=D-A\n@R13\nM=D\nA=M\nD=M\nA=A+1\nD=D-M\n@LT" + "\nD;JLT\n@R13\nA=M\nM=0\n@END" + "\n0;JMP\n(LT)\n@R13\nA=M\nM=-1\n(END)\n@SP\nM=M-1\n"
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
            



        elif command == "push" and segment == "pointer":
            # reg = "R3" if segment == "pointer" else self.function + "." + str(index)
            reg = "R3"
            self.assembly += "@" + reg + "\nD=A\n@" + str(index) + "\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        elif command == "push" and segment == "static":
            func_name = self.function.split('.')[0]
            reg = func_name + "." + str(index)
            # reg = self.function + "." + str(index)

            print(f"Static variable reference: ", reg)
            self.assembly += "@" + reg + "\nD=M\n@SP\nA=M\nM=D\n@SP\n@SP\nM=M+1\n"
        elif command == "push":
            print("push statement")
            self.assembly += "@" + segment_assembly[segment] + "\nD=M\n@" + str(index) + "\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"


        # if command == "pop" and segment == "temp":
        #     self.assembly += "@R5\nD=A\n@" + str(index) + "\nD=D+A\n@R13\nM=D\n@SP\nA=A-1\nD=M\n@R13\nA=M\nM=D\n@SP\nM=M-1\n" 
        if command == "pop" and segment == "pointer":
            # reg = "R3" if segment == "pointer" else "16"
            reg = "R3"
            self.assembly += "@" + reg + "\nD=A\n@" + str(index) + "\nD=D+A\n@R13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n"
        # TODO: FIXXXXX



        elif command == "pop" and segment == "static":
            func_name = self.function.split('.')[0]
            reg = func_name + "." + str(index)
            print(f"Static variable reference: ", reg)
            self.assembly += "@SP\nA=M-1\nD=M\n@" + reg + "\nM=D\n@SP\nM=M-1\n"



        elif command == "pop" and segment == "temp":
            self.assembly += "@R5\nD=A\n@" + str(index) + "\nD=D+A\n@13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n"
        elif command == "pop":
            print("pop statement")
            self.assembly += "@" + segment_assembly[segment] + "\nD=M\n@" + str(index) + "\nD=D+A\n@R13\nM=D\n@SP\nA=M-1\nD=M\n@R13\nA=M\nM=D\n@SP\nM=M-1\n" 

            
    def writeLabel(self, label : str):
        self.assembly += "(" + self.function + "$" + label + ")\n"# function_name$label

    def writeGoto(self, label : str):
        label_  = self.function + "$" + label
        self.assembly += "@" + label_ + "\n0;JMP\n"

    def writeIf(self, label : str):
        print("if-goto reached")
        label_ = self.function + "$" + label
        self.assembly += "@SP\nM=M-1\nA=M\nD=M\n@" + label_ + "\nD;JNE\n"

    def writeFunction(self, functionName:str, numLocals:int):
        self.function = functionName
        self.assembly += "(" + functionName + ")\n" + "@" + str(numLocals) + "\nD=A\n@" + functionName + ".END\nD;JEQ\n(" + functionName + ".LOOP)\n@SP\nA=M\nM=0\n@SP\nM=M+1\nD=D-1\n@" + functionName + ".LOOP\nD;JNE\n(" + functionName + ".END)\n"
        self.index += 1

    def writeReturn(self): 
        self.assembly += "@LCL\nD=M\n@5\nA=D-A\nD=M\n@R14\nM=D\n@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\nD=A+1\n@SP\nM=D\n" + \
            "@LCL\nD=M\n@1\nA=D-A\nD=M\n@THAT\nM=D\n" + \
            "@LCL\nD=M\n@2\nA=D-A\nD=M\n@THIS\nM=D\n" + \
            "@LCL\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n"  + \
            "@LCL\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n"  + \
            "@R14\nA=M\n0;JMP\n"
    
    def writeCall(self, functionName:str, numArgs: int):
        return_address = "return." + functionName + str(self.index)
        self.assembly += "@" + return_address + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" + \
            "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"  + \
            "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"  + \
            "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" + \
            "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n" + \
            "@SP\nD=M\n@" + str(numArgs) + "\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n" + \
            "@SP\nD=M\n@LCL\nM=D\n" + \
            "@" + functionName + "\n" + \
            "0;JMP\n" + "(" + return_address + ")\n"

        self.index += 1

    def writeInit(self):
        self.assembly += "@256\nD=A\n@SP\nM=D\n" + \
            "@261\nD=A\n@SP\nM=D\n" + \
            "@Sys.init\n0;JMP\n"

    def Close(self):
        self.f.close()

def main(file):  
    input_file = file  

    # this is single file
    i = 0
    coder = CodeWriter("test.asm")
    with open(input_file, "r") as file:
        coder.writeInit()
        for line in file:
            if line[-1] == "\n":
                line = line[:-1]
            i += 1
            parser = Parser(line)
            
            if parser.command_type == COMMAND_TYPE.C_ARITHMETIC:
                coder.writeArithmetic(parser.tokens[0])
            elif (
                parser.command_type == COMMAND_TYPE.C_PUSH
                or parser.command_type == COMMAND_TYPE.C_POP
            ):
                coder.WritePushPop(parser.tokens[0], parser.arg_1, parser.arg_2)
            elif parser.command_type == COMMAND_TYPE.C_LABEL:
                coder.writeLabel(parser.tokens[1])
            elif parser.command_type == COMMAND_TYPE.C_GOTO:
                coder.writeGoto(parser.tokens[1])
            elif parser.command_type == COMMAND_TYPE.C_IF:
                coder.writeIf(parser.tokens[1])
            elif parser.command_type == COMMAND_TYPE.C_FUNCTION:
                coder.writeFunction(parser.arg_1, parser.arg_2)
            elif parser.command_type == COMMAND_TYPE.C_RETURN:
                coder.writeReturn()
            elif parser.command_type == COMMAND_TYPE.C_CALL:
                coder.writeCall(parser.arg_1, parser.arg_2)
    coder.setFilename("test")


if __name__ == "__main__":
    VM_CLI().cmdloop()
