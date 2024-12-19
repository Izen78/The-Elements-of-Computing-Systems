"""
Compiler Implementation of Syntax Analysis for Jack Language

author: Arpon Sarker
date: 17-12-2024
"""

import cmd
import os
from enum import Enum
from os.path import isdir


# 1. Set up cmd of directories and processing each file separately to output corresponding .xml file
# 2. Set up tokeniser - gets rid of comments and white space
# 3. Test tokeniser with their .cmp files

class TOKEN_TYPE(Enum):
    KEYWORD = 0,
    SYMBOL = 1,
    IDENTIFIER = 2,
    INT_CONST = 3,
    STRING_CONST = 4

class KEYWORD(Enum):
    CLASS = 0,
    METHOD = 1,
    FUNCTION = 2,
    CONSTRUCTOR = 3,
    INT = 4,
    BOOLEAN = 5,
    CHAR = 6,
    VOID = 7, 
    VAR = 8,
    STATIC = 9,
    FIELD = 10,
    LET = 11,
    DO = 12,
    IF = 13,
    ELSE = 14,
    WHILE = 15,
    RETURN = 16,
    TRUE = 17,
    FALSE = 18,
    NULL = 19,
    THIS = 20

class CLI(cmd.Cmd):
    prompt = "prompt> "
    intro = "Compiler for the Jack Language"

    def do_help(self, arg:str) -> bool | None:
        """You are in this command now?"""
        return super().do_help(arg)

    def do_j(self, line):
        """Converts .jack files into .vm files"""
        input_file = line
        if os.path.isdir(input_file):
            # directory given
            dir_files = os.listdir(input_file)
            for dir_file in dir_files:
                if dir_file[-5:] == ".jack":
                    # opens file, creates corresponding tokenizer file in cwd not dir itself
                    JackAnalyzer(input_file + dir_file)
        else:
            JackAnalyzer(input_file)
    
    def do_q(self, line):
        """Exit the CLI"""
        return True

class symbolTable:
    table = {} # name: [type, kind, index]
    kind_index = {"static": 0, "field": 0, "argument": 0, "var": 0}
    def __init__(self):
        self.table = {}
        self.kind_index = {"static": 0, "field": 0, "argument": 0, "var": 0}
    
    def startSubroutine(self):
        """ Only to be used by subroutine table not class table"""
        self.table = {}
        self.kind_index["argument"] = 0
        self.kind_index["var"] = 0

    def Define(self, name: str, id_type: str, kind):
        self.table[name] = [id_type, kind, self.kind_index[kind]]
        self.kind_index[kind] += 1 

    def varCount(self, kind) -> int:
        return self.kind_index[kind]

    def kindOf(self, name:str) -> str | None:
        name_contents = self.table.get(name)
        if name_contents == None:
            return None
        else:
            return name_contents[1] 

    def typeOf(self, name:str) -> str:
        name_contents = self.table.get(name)
        if name_contents == None:
            return None
        else:
            return name_contents[1] 
    
    def indexOf(self, name:str) -> int:
        name_contents = self.table.get(name)
        if name_contents == None:
            return None
        else:
            return name_contents[2] 

class VMWriter:
    output_stream = ""
    commands = ""

    def __init__(self, output_stream) -> None:
        self.output_stream = output_stream

    def writePush(self, segment, index: int):
        self.commands += f"push {segment} {index}\n" 

    def writePop(self, segment, index: int):
        self.commands += f"pop {segment} {index}\n"

    def writeArithmetic(self, command):
        self.commands += f"{command}\n"

    def writeLabel(self, label):
        self.commands += f"label {label}\n"

    def writeGoto(self, label):
        self.commands += f"goto {label}\n"

    def writeIf(self, label):
        self.commands += f"if-goto {label}\n"

    def writeCall(self, name, nArgs):
        self.commands += f"call {name} {nArgs}\n"

    def writeFunction(self, name, nLocals):
        self.commands += f"function {name} {nLocals}\n"

    def writeReturn(self):
        self.commands += "return\n"

    def close(self):
        with open(self.output_stream, "w") as file:
            file.write(self.commands)

    def debug(self, line):
        self.commands += f"{line}\n"

        

class JackTokenizer:
    list_tokens = [] # lists all tokens in line - used as a stack
    current_token = ""
    line = ""
    current_comment = False 
    commands = "<tokens>\n" # text to be written to token file
    is_string = False

    token_type = None
    key_word = None
    sym = ''
    id = ""
    int_val = None 
    string_val = ""


    def __init__(self, input_file):

        dir_index = input_file.find("/")
        ext_index = input_file.find(".")
        output_file_name = input_file[dir_index+1:ext_index]
        token_output_file = open(output_file_name+"T.xml", "w")
        comp_output_file = open(output_file_name+".xml", "w")
        comp_commands = ""
        symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

        with open(input_file, "r") as file:
            for line in file:
                # for each line, loop through all tokens as current_token then move to next line
                self.line = line
                if self.hasMoreTokens(): # self.line contains code
                    if len(self.line) > 1:
                        i = 0
                        while i < len(self.line):
                            if self.line[i] in symbol_list:
                                if i == len(self.line)-1:
                                    # last character aka ;
                                    last_symbol = self.line[i]
                                    if self.line[-2] != ' ':
                                        self.line = self.line[:-1] + " " + last_symbol
                                    break
                                else:

                                    # len of line keeps incrementing 
                                    if self.line[i-1] != ' ' and self.line[i+1] != ' ':
                                        self.line = self.line[:i] + " " + self.line[i] + " " + self.line[i+1:]
                                        i += 2
                                    elif self.line[i-1] != ' ':
                                        self.line = self.line[:i] + " " + self.line[i] + self.line[i+1:]
                                        i += 2
                                    elif self.line[i+1] != ' ':
                                        self.line = self.line[:i+1] + " " + self.line[i+1:]
                                        i += 1
                            i += 1

                    i = 0
                    if self.line.count("\"") > 0:
                        while i < self.line.count("\""):
                            # Put stuff before string into list_tokens
                            str_index = self.line.find("\"")
                            process_part = self.line[:str_index]
                            self.line = self.line[str_index+1:] # removes first quote
                            self.list_tokens += process_part.split()

                            # Put entire string into list_tokens
                            str_index = self.line.find("\"") # finds 2nd quote of pair
                            process_part = "\"" + self.line[:str_index+1]
                            self.line = self.line[str_index+1:]
                            self.list_tokens += [process_part]
 
                            
                            i += 2

                        self.list_tokens += self.line.split()
                    else:
                        self.list_tokens = self.line.split(" ")
                    if '' in self.list_tokens:
                        self.list_tokens.remove('')
                    while len(self.list_tokens) > 0:
                        self.advance() 
                        self.tokenType() 
                        if self.token_type == TOKEN_TYPE.KEYWORD:
                            self.commands += "<keyword>" + str(self.key_word) + "</keyword>\n"
                        elif self.token_type == TOKEN_TYPE.SYMBOL:
                            self.commands += "<symbol>" + self.sym + "</symbol>\n"
                        elif self.token_type == TOKEN_TYPE.IDENTIFIER:
                            self.commands += "<identifier>" + self.id + "</identifier>\n"
                        elif self.token_type == TOKEN_TYPE.INT_CONST:
                            self.commands += "<integerConstant>" + str(self.int_val) + "</integerConstant>\n"
                        elif self.token_type == TOKEN_TYPE.STRING_CONST:
                            self.commands += "<stringConstant>" + self.string_val[1:-1] + "</stringConstant>\n"
                        else:
                            print("ERROR: TOKEN TYPE INVALID FOR WRITING")


        self.commands += "</tokens>"
        token_output_file.write(self.commands)
        token_output_file.close()

    # Comments come in: // Foo\n | /* Foo... */ | /** Foo... */
    def hasMoreTokens(self) -> bool: # ignores whitespace and comments
        self.line = self.line.strip() # removes leading and trailing whitespaces
        comment_index = -1
        if "//" in self.line:
            comment_index = self.line.find("//")
        elif ("/*" in self.line or "/**" in self.line) and "*/" in self.line:
            comment_index = self.line.find("/*")
        elif "/*" in self.line or "/**" in self.line:
            self.current_comment = True
            comment_index = self.line.find("/*")
        elif "*/" in self.line:
            self.current_comment = False
            comment_index = self.line.find("*/")
            while (comment_index < len(self.line) - 1):
                comment_index += 1
                if self.line[comment_index] == ' ':
                    continue
                else:
                    self.line = self.line[comment_index:]
                    self.line = self.line.strip()
                    comment_index = -1
                    break
        elif self.current_comment == True:
            return False
        
        if comment_index != -1:
            self.line = self.line[:comment_index] # if comment type 1 -> len = 0 now
            self.line = self.line.strip()
        if self.line == "/":
            self.line = ""

        if len(self.line) > 0:
            return True
        else:
            return False

    def advance(self):
        """ Pops list_tokens[0] as current_token"""
        self.current_token = self.list_tokens[0]
        self.list_tokens = self.list_tokens[1:]

    def tokenType(self):
        """ Gets type from current_token and sets corresponding fields"""
        keyword = ["class", "method", "function", "constructor", "int", "boolean", "char", "void",
                   "var", "static", "field", "let", "do", "if", "else", "while", "return", "true",
                   "false", "null", "this"]
        symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|',
                       '<', '>', '=', '~']
        if self.current_token in keyword:
            self.token_type = TOKEN_TYPE.KEYWORD
            self.keyWord()
        elif self.current_token in symbol_list:
            self.token_type = TOKEN_TYPE.SYMBOL
            self.symbol()
        elif self.current_token[0].isalpha() or self.current_token[0] == '_':
            self.token_type = TOKEN_TYPE.IDENTIFIER
            self.identifier()
        elif self.current_token.isnumeric():
            self.token_type = TOKEN_TYPE.INT_CONST
            self.intVal()
        elif self.current_token[0] == "\"" and self.current_token[-1] == "\"":
            self.token_type = TOKEN_TYPE.STRING_CONST
            self.stringVal()
        else:
            print("ERROR: NOT VALID TOKEN")

    def keyWord(self):
        keyword = ["class", "method", "function", "constructor", "int", "boolean", "char", "void",
                   "var", "static", "field", "let", "do", "if", "else", "while", "return", "true",
                   "false", "null", "this"]
        for word in keyword:
            if self.current_token == word:
                self.key_word = word

    def symbol(self):
        symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|',
                       '<', '>', '=', '~']
        for symbol in symbol_list:
            if self.current_token == symbol:
                if symbol == '<':
                    self.sym = "&lt;"
                elif symbol == '>':
                    self.sym = "&gt;"
                elif symbol == '\"':
                    self.sym = "&quot;"
                elif symbol == '&':
                    self.sym = "&amp;"
                else:
                    self.sym = symbol
                break

    def identifier(self):
        self.id = self.current_token

    def intVal(self):
        self.int_val = int(self.current_token)

    def stringVal(self):
        self.string_val = self.current_token # includes quotes here

class CompilationEngine:
    input_file = ""
    output_file = ""
    commands = ""
    current_token = ""
    next_token = ""
    filtered_line = ""

    line_num = 0
    token_lines = None
    keyword = ["class", "method", "function", "constructor", "int", "boolean", "char", "void",
               "var", "static", "field", "let", "do", "if", "else", "while", "return", "true",
               "false", "null", "this"]
    symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|',
                   '<', '>', '=', '~']

    class_table = None
    subroutine_table = None
    var_name = ""
    id_type = "" # 'int', 'char', 'boolean', className
    kind = "" # STATIC, FIELD, ARG, VAR
    subroutine_keyword = ""
    added_this = False
    class_name = ""
    if_index = 0 # for unique branching labels
    while_index = 0 # for unique branching labels

    vm_writer = None


    def __init__(self, input_stream, output_stream):
        self.input_file = open(input_stream, "r")
        self.token_lines = self.input_file.readlines()
        self.output_file = output_stream
        # self.class_table = None 
        # self.subroutine_table = None 
        self.vm_writer = None
             
        self.compileClass()
    def compileClass(self):
        self.class_table = symbolTable() # HACK: Only allowed to add static or field here
        self.subroutine_table = symbolTable() # HACK: Only allowed to add arg or var here
        self.vm_writer = VMWriter(self.output_file + ".vm")

        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.commands += "<class>\n<keyword>" + self.filtered_line + "</keyword>\n" 

        self.line_num += 1 # for className
        self.filtered_line = self.helperFilter()
        self.commands += "<identifier>" + self.filtered_line + "</identifier>\n"
        self.class_name = self.filtered_line

        self.line_num += 1 # for symbol
        self.filtered_line = self.helperFilter()
        for sym in self.symbol_list:
            if sym in self.filtered_line:
                self.commands += "<symbol>" + sym + "</symbol>\n"
                                                                    
        self.line_num += 1 # keyword for initial classVarDec/subroutineDec
        self.filtered_line = self.helperFilter()
        while self.filtered_line in ("static", "field"):
            self.compileClassVarDec() # goes to just after ;
        while self.filtered_line in ("constructor", "function", "method"):
            self.compileSubroutine() # goes to just after ;

        self.commands += "<symbol>}</symbol>\n"
        self.commands += "</class>"
        self.input_file.close()
        with open(self.output_file + ".xml", "w") as file:
            file.write(self.commands)
        self.vm_writer.close()

    def compileClassVarDec(self):
        """ Handles 1 or more class variable declarations """
        self.commands += "<classVarDec>\n"
        self.filtered_line = self.helperFilter()
        self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        self.kind = self.filtered_line # either STATIC or FIELD

        self.line_num += 1 # for type
        self.filtered_token = self.helperToken()
        self.filtered_line = self.helperFilter()
        if self.filtered_token == "keyword":
            self.commands += f"<{self.filtered_token}>{self.filtered_line}</{self.filtered_token}>\n"
            self.id_type = self.filtered_line
        else:
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
            self.id_type = self.filtered_line

        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.var_name = self.filtered_line

        self.class_table.Define(self.var_name,self.id_type, self.kind)

        self.line_num += 1 # for ; or ,
        self.filtered_line = self.helperFilter()
        if self.filtered_line == ";":
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
        elif self.filtered_line == ",":
            while (self.filtered_line == ","): 
                self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
                self.line_num += 1 # for extra varName
                self.filtered_line = self.helperFilter()
                self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

                self.var_name = self.filtered_line
                self.class_table.Define(self.var_name, self.id_type, self.kind)
                self.line_num += 1 # for next comma
                self.filtered_line = self.helperFilter()
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n" # if semicolon
        self.commands += "</classVarDec>\n"

        self.line_num += 1
        self.filtered_line = self.helperFilter() # after ; -> classVarDec, subroutineDec, }
        

    def compileSubroutine(self):
        """ Handles 1 or more subroutine declarations """
        self.commands += "<subroutineDec>\n"
        self.filtered_line = self.helperFilter()
        self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        self.subroutine_keyword = self.filtered_line

        self.line_num += 1 # for return type
        self.filtered_line = self.helperFilter()
        if self.filtered_line in ("void", "int", "char", "boolean"):
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        else:
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

        self.line_num += 1 # for subroutineName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        identifier_name = self.filtered_line
        self.subroutine_table.startSubroutine()

        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>(</symbol>\n"

        self.line_num += 1 # for param list - either type or )
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()

        self.commands += "<parameterList>\n"
        if self.filtered_line in ("int", "char", "boolean") or self.filtered_token == "identifier":
            self.compileParameterList()
            self.added_this = False
        self.commands += "</parameterList>\n"
        self.commands += "<symbol>)</symbol>\n"


        self.commands += "<subroutineBody>\n"
        self.line_num += 1 # for {
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>{</symbol>\n"
        self.line_num += 1 # for "var" in varDec or "let", "if", "wile", "do", "return"
        self.filtered_line = self.helperFilter()
        num_local = 0
        if self.filtered_line == "var":
            while self.filtered_line == "var":
                num_local = self.compileVarDec()

        self.vm_writer.writeFunction(self.class_name + "." + identifier_name, num_local)
        if self.subroutine_keyword == "constructor":
            self.vm_writer.writePush("constant", self.class_table.varCount("field")) # setting constructor fields and allocating memory for 'this'
            self.vm_writer.writeCall("Memory.alloc", 1)
            self.vm_writer.writePop("pointer", 0)
        elif self.subroutine_keyword == "method":
            self.vm_writer.writePush("argument", 0)
            self.vm_writer.writePop("pointer", 0)


        if self.filtered_line in ("let", "if", "while", "do", "return"):
            self.commands += "<statements>\n"
            self.compileStatements()
            self.commands += "</statements>\n"
            self.commands += "<symbol>}</symbol>\n"
        self.commands += "</subroutineBody>\n"
        self.commands += "</subroutineDec>\n"

        if self.line_num < len(self.token_lines)-1: # not at EOF
            self.line_num += 1 # for subroutineDec
            self.filtered_line = self.helperFilter()
            if self.helperFilter() in ("constructor", "function", "method"):
                self.compileSubroutine()


    def compileStatements(self):
        
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "let":
            self.compileLet()
        elif self.filtered_line == "if":
            self.compileIf()
        elif self.filtered_line == "while":
            self.compileWhile()
        elif self.filtered_line == "do":
            self.compileDo()
        elif self.filtered_line == "return":
            self.compileReturn()


        self.filtered_line = self.helperFilter()
        if self.filtered_line in ("let", "if", "while", "do", "return"):
            self.compileStatements()

    def compileReturn(self):
        self.commands += "<returnStatement>\n"
        self.commands += "<keyword>return</keyword>\n"
        self.line_num += 1 # for expression or ;
        self.filtered_line = self.helperFilter()
        if self.filtered_line != ";":
            # expression
            self.compileExpression()
            if self.filtered_line == ";":
                self.vm_writer.writeReturn()
        else:
            self.vm_writer.writeReturn()
        self.commands += "<symbol>;</symbol>\n"
        
        self.commands += "</returnStatement>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

    def compileDo(self):
        # TODO: Finish this do statement first
        # Have to add class into class_table with type as self.class_name
        # Have to make sure to check class_table if checking subroutine_table fails
        # Anytime subroutine (constructor, method, or function) is declared or called, make sure class_name. in front
        self.commands += "<doStatement>\n"
        self.commands += "<keyword>do</keyword>\n"
        self.line_num += 1 # for subroutineName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        identifier_name = self.filtered_line
        self.line_num += 1 # for ( or .
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "(": # METHOD
            self.commands += "<symbol>(</symbol>\n"
            self.line_num += 1 # for expressionList which could also be empty
            self.filtered_line = self.helperFilter()
            self.commands += "<expressionList>\n" # need this even if empty

            self.vm_writer.writePush("pointer", 0)
            num_args = self.compileExpressionList()
            num_args += 1
            self.vm_writer.writeCall(identifier_name, num_args)

            self.commands += "</expressionList>\n"
            self.commands += "<symbol>)</symbol>\n"
        elif self.filtered_line == ".": # FUNCTION
            identifier_type = self.subroutine_table.typeOf(identifier_name)
            if identifier_type == None:
                identifier_type = self.class_table.typeOf(identifier_name)
            if (identifier_type == self.class_name) or (identifier_type == None):
                self.commands += "<symbol>.</symbol>\n"
                self.line_num += 1 # for subroutine name
                self.filtered_line = self.helperFilter()

                func_name = identifier_name + "." + self.filtered_line
                self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
                self.line_num += 1 # for (
                self.filtered_line = self.helperFilter()
                self.commands += "<symbol>(</symbol>\n"
                self.line_num += 1 # for expressionList which could also be empty
                self.filtered_line = self.helperFilter()
                self.commands += "<expressionList>\n" # need this even if empty
                num_args = self.compileExpressionList()
                print("reached")
                self.vm_writer.writeCall(func_name, num_args)


                self.commands += "</expressionList>\n"
                self.commands += "<symbol>)</symbol>\n"
            else:
                self.commands += "<symbol>.</symbol>\n"
                self.line_num += 1 # for subroutine name
                self.filtered_line = self.helperFilter()

                method_name = identifier_name + "." + self.filtered_line # TODO: May need to make this as self.class_name + . + subroutineName not varName
                self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
                self.line_num += 1 # for (
                self.filtered_line = self.helperFilter()
                self.commands += "<symbol>(</symbol>\n"
                self.line_num += 1 # for expressionList which could also be empty
                self.filtered_line = self.helperFilter()
                self.commands += "<expressionList>\n" # need this even if empty
                self.vm_writer.writePush("pointer", 0)
                num_args = self.compileExpressionList()
                num_args += 1
                self.vm_writer.writeCall(method_name, num_args)

                self.commands += "</expressionList>\n"
                self.commands += "<symbol>)</symbol>\n"

        self.line_num += 1 # for ;
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>;</symbol>\n"

        self.commands += "</doStatement>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

    def compileExpressionList(self):
        num_args = 0
        self.filtered_line = self.helperFilter()
        while self.filtered_line != ")":
            # expression
            self.compileExpression() # either reaches , or )
            num_args += 1
            self.filtered_line = self.helperFilter()
            if self.filtered_line == ",":
                self.commands += "<symbol>,</symbol>\n"
                self.line_num += 1
                self.filtered_line = self.helperFilter()
        return num_args

    def compileExpression(self):

        print("reached: ", self.filtered_line)
        op_list = ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]
        op_commands = {"+":"add", "-":"sub", "*": "call Math.multiply 2", "/": "call Math.divide 2", "&amp;":"and", "|":"or", "&lt;":"lt", "&gt;":"gt", "=":"eq"}
        self.commands += "<expression>\n"
        self.compileTerm()
        self.filtered_line = self.helperFilter() # just after, either op or ignore
        while self.filtered_line in op_list:
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            op = op_commands[self.filtered_line]
            self.line_num += 1 # set up compileTerm
            self.filtered_line = self.helperFilter()
            self.compileTerm()
            self.filtered_line = self.helperFilter()
            self.vm_writer.writeArithmetic(op)



        self.commands += "</expression>\n"
        # already incremented

    def compileTerm(self):
        self.commands += "<term>\n"
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()
        if self.filtered_token == "integerConstant":
            self.commands += f"<integerConstant>{self.filtered_line}</integerConstant>\n"
            self.vm_writer.writePush("constant", int(self.filtered_line))
        elif self.filtered_token == "stringConstant":
            self.commands += f"<stringConstant>{self.filtered_line}</stringConstant>\n"
            self.vm_writer.writePush("constant", len(self.filtered_line))
            self.vm_writer.writeCall("String.new", 1) # creates a new EMPTY string
            for char in self.filtered_line:
                self.vm_writer.writePush("constant", ord(char))
                self.vm_writer.writeCall("String.appendChar", 2) # adds to string before
        elif self.filtered_line in ("true", "false", "null", "this"):
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
            if self.filtered_line == "true":
                self.vm_writer.writePush("constant", 1)
                self.vm_writer.writeArithmetic("neg")
            elif self.filtered_line in ("false" or "null"):
                self.vm_writer.writePush("constant", 0)
            else:
                self.vm_writer.writePush("pointer", 0)
        elif self.filtered_token == "identifier":
            # either varname, varname[expr], subroutine(), varName.subroutine()
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
            identifier_name = self.filtered_line

            self.line_num += 1 # for ., [, ( -> ignore if none of these
            self.filtered_line = self.helperFilter()

            if self.filtered_line == ".":
                identifier_type = self.subroutine_table.typeOf(identifier_name)
                if identifier_type == None:
                    identifier_type = self.class_table.typeOf(identifier_name)
                if identifier_type == self.class_name:
                    self.commands += "<symbol>.</symbol>\n"
                    self.line_num += 1 # for subroutine name
                    self.filtered_line = self.helperFilter()

                    func_name = identifier_name + "." + self.filtered_line
                    self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
                    self.line_num += 1 # for (
                    self.filtered_line = self.helperFilter()
                    self.commands += "<symbol>(</symbol>\n"
                    self.line_num += 1 # for expressionList
                    self.filtered_line = self.helperFilter()
                    self.commands += "<expressionList>\n"
                    num_args = self.compileExpressionList()
                    self.vm_writer.writeCall(func_name, num_args)


                    self.commands += "</expressionList>\n"
                    self.commands += "<symbol>)</symbol>\n"
                else:
                    self.commands += "<symbol>.</symbol>\n"
                    self.line_num += 1 # for subroutine name
                    self.filtered_line = self.helperFilter()

                    method_name = identifier_name + "." + self.filtered_line
                    self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
                    self.line_num += 1 # for (
                    self.filtered_line = self.helperFilter()
                    self.commands += "<symbol>(</symbol>\n"
                    self.line_num += 1 # for expressionList
                    self.filtered_line = self.helperFilter()
                    self.commands += "<expressionList>\n"
                    self.vm_writer.writePush("pointer", 0)
                    num_args = self.compileExpressionList()
                    num_args += 1 # since we added in object
                    self.vm_writer.writeCall(method_name, num_args)

                    self.commands += "</expressionList>\n"
                    self.commands += "<symbol>)</symbol>\n"



            elif self.filtered_line == "(":
                self.commands += "<symbol>(</symbol>\n"
                self.line_num += 1 # for expressionList
                self.filtered_line = self.helperFilter()
                self.commands += "<expressionList>\n"

                self.vm_writer.writePush("pointer", 0)
                num_args = self.compileExpressionList()
                num_args += 1 # since we added in object
                self.vm_writer.writeCall(identifier_name, num_args)

                self.commands += "</expressionList>\n"
                self.commands += "<symbol>)</symbol>\n"

            elif self.filtered_line == "[":
                self.commands += "<symbol>[</symbol>\n"
                self.line_num += 1
                self.filtered_line = self.helperFilter()
                self.compileExpression()

                var_kind = self.subroutine_table.kindOf(identifier_name)
                if var_kind == None:
                    var_kind = self.class_table.kindOf(identifier_name)
                    var_kind = "this" if var_kind == "field" else print("ERROR")
                var_index = self.subroutine_table.indexOf(identifier_name)
                self.vm_writer.writePush(var_kind, var_index)
                self.vm_writer.writeArithmetic("add")
                self.vm_writer.writePop("pointer", 1)
                self.commands += "<symbol>]</symbol>\n"
            else:
                var_kind = self.subroutine_table.kindOf(identifier_name)
                if var_kind == None:
                    var_kind = self.class_table.kindOf(identifier_name)
                    var_kind = "this" if var_kind == "field" else None
                var_index = self.subroutine_table.indexOf(identifier_name)
                self.vm_writer.writePush(var_kind, var_index)

                self.line_num -= 1
                self.filtered_line = self.helperFilter()
        elif self.filtered_line == "(":
            self.commands += "<symbol>(</symbol>\n"
            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.compileExpression()
            self.commands += "<symbol>)</symbol>\n"
            # self.line_num -= 1
        elif self.filtered_line in ("-", "~"):
            op = self.filtered_line
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            self.line_num += 1 # set up recursion
            self.filtered_line = self.helperFilter()
            self.compileTerm()
            if op == "-":
                self.vm_writer.writeArithmetic("not")
            elif op == "~":
                self.vm_writer.writeArithmetic("neg")
            else:
                print("ERROR: expected \'-\' or \"=\"")


        self.commands += "</term>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

    def compileWhile(self):
        self.commands += "<whileStatement>\n"
        self.commands += "<keyword>while</keyword>\n"
        self.line_num += 1 # for (
        self.filtered_line = self.helperFilter()

        self.vm_writer.writeLabel("WHILE_LOOP$" + str(self.while_index))

        self.commands += "<symbol>(</symbol>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.compileExpression()

        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf("WHILE_END$" + str(self.while_index))

        self.commands += "<symbol>)</symbol>\n"
        if self.filtered_line == ")":
            self.line_num += 1
            self.filtered = self.helperFilter()
        self.commands += "<symbol>{</symbol>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.commands += "<statements>\n"
        self.compileStatements() # reaches just after last symbol to '}' 
        self.commands += "</statements>\n"
        self.commands += "<symbol>}</symbol>\n"

        self.vm_writer.writeGoto("WHILE_LOOP$" + str(self.while_index))
        self.vm_writer.writeLabel("WHILE_END$" + str(self.while_index))


        self.commands += "</whileStatement>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.while_index += 1

    def compileIf(self):
        self.commands += "<ifStatement>\n"
        self.commands += "<keyword>if</keyword>\n"
        self.line_num += 1 # for (
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>(</symbol>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.compileExpression() # should reach just after to ')'
        self.commands += "<symbol>)</symbol>\n"

        self.vm_writer.writeIf("IF_TRUE$" + str(self.if_index))
        self.vm_writer.writeGoto("IF_FALSE$" + str(self.if_index))

        self.line_num += 1 # for {
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>{</symbol>\n"
        self.line_num += 1 # for statements keyword
        self.filtered_line = self.helperFilter()
        self.commands += "<statements>\n"
        self.vm_writer.writeLabel("IF_TRUE$" + str(self.if_index))
        self.compileStatements() # reaches just after last symbol to '}' 
        self.commands += "</statements>\n"
        self.commands += "<symbol>}</symbol>\n"


        self.line_num += 1
        self.filtered_line == self.helperFilter()
        if self.filtered_line == "else</keyword>\n":
            self.filtered_line = "else"
        if self.filtered_line == "else":
            # else statement included
            self.commands += "<keyword>else</keyword>\n"

            self.vm_writer.writeGoto("IF_END$" + str(self.if_index))
            self.vm_writer.writeLabel("IF_FALSE$" + str(self.if_index))

            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.commands += "<symbol>{</symbol>\n"
            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.commands += "<statements>\n"
            self.compileStatements()
            self.commands += "</statements>\n"
            self.commands += "<symbol>}</symbol>\n"
            self.commands += "</ifStatement>\n"
            self.line_num += 1 # for recursion
            self.filtered_line = self.helperFilter()
            self.vm_writer.writeLabel("IF_END$" + str(self.if_index))
        else:
            self.vm_writer.writeLabel("IF_FALSE$" + str(self.if_index))
            self.if_index += 1
            self.commands += "</ifStatement>\n"

    def compileLet(self):
        self.commands += "<letStatement>\n"
        self.commands += "<keyword>let</keyword>\n"
        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        identifier_name = self.filtered_line
        self.line_num += 1 # for [ or = 
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "[":
            self.commands += "<symbol>[</symbol>\n"
            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.compileExpression()
            self.commands += "<symbol>]</symbol>\n"


            var_kind = self.subroutine_table.kindOf(identifier_name)
            if var_kind == None:
                var_kind = self.class_table.kindOf(identifier_name)
                var_kind = "this" if var_kind == "field" else None
            var_index = self.subroutine_table.indexOf(identifier_name)
            self.vm_writer.writePush(var_kind, var_index)
            self.vm_writer.writeArithmetic("add") # gets address of array[index]


            self.line_num += 1 # for = 
            self.filtered_line = self.helperFilter()
            self.commands  += "<symbol>=</symbol>\n"
            # self.line_num += 1 # for expression
            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.compileExpression()

            self.vm_writer.writePop("temp", 0)
            self.vm_writer.writePop("pointer", 1)
            self.vm_writer.writePush("temp", 0)
            self.vm_writer.writePop("that", 0)
        else:
            self.filtered_line = self.helperFilter()
            self.commands  += "<symbol>=</symbol>\n"
            # self.line_num += 1 # for expression
            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.compileExpression()

            var_kind = self.subroutine_table.kindOf(identifier_name)
            if var_kind == None:
                var_kind = self.class_table.kindOf(identifier_name)
                var_kind = "this" if var_kind == "field" else None
            var_index = self.subroutine_table.indexOf(identifier_name)
            self.vm_writer.writePop(var_kind, var_index)

            self.commands += "<symbol>;</symbol>\n"
            self.commands += "</letStatement>\n"
            self.line_num += 1 # for recursion
            self.filtered_line = self.helperFilter()


    def compileVarDec(self):
        self.commands += "<varDec>\n"
        self.filtered_line = self.helperFilter()
        self.commands += f"<keyword>{self.filtered_line}</keyword>\n"

        self.line_num += 1 # for type
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()
        if self.filtered_token == "keyword":
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        else:
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.id_type = self.filtered_line

        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.var_name = self.filtered_line

        self.subroutine_table.Define(self.var_name, self.id_type, "var")
        num_local = 1

        self.line_num += 1 # either , for loop or ; for recursion or exit
        self.filtered_line = self.helperFilter()
        while self.filtered_line == ",":
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            self.line_num += 1 # for next varName
            self.filtered_line = self.helperFilter()
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
            self.line_num += 1 # sets up next iter of loop
            self.filtered_line = self.helperFilter()
            num_local += 1
        self.commands += "<symbol>;</symbol>"
        self.commands += "\n</varDec>\n"

        self.line_num += 1
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "var":
            self.compileVarDec()
        return num_local





    # TODO: Everytime I use 'this' maybe I should just use the typeOf as 'this' rather than pop pointer 0
    def compileParameterList(self):
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()
        if self.filtered_token == "keyword":
            # int, char, boolean
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        else:
            # className
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.id_type = self.filtered_line

        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.var_name = self.filtered_line

        if self.subroutine_keyword == "method" and self.added_this == False:
            # add 'this'
            self.subroutine_table.Define("this", self.class_name, "argument") 
            self.added_this = True
        self.subroutine_table.Define(self.var_name, self.id_type, "argument")
            

        self.line_num += 1 # for , or )
        self.filtered_line = self.helperFilter()
        if self.filtered_line == ",":
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            self.line_num += 1 # for type to set up recursion
            self.filtered_line = self.helperFilter()
            self.compileParameterList()
        # elif self.filtered_line == ")":
        #     self.line_num += 1
        #     self.filtered_line = self.helperFilter()



    def helperFilter(self):
        """ Returns the contents """
        print(self.line_num)
        print(len(self.token_lines))
        quote_index = self.token_lines[self.line_num].find(">")
        self.filtered_line = self.token_lines[self.line_num][quote_index+1:]
        quote_index = self.filtered_line.find("<")
        return self.filtered_line[:quote_index]

    def helperToken(self):
        """ Returns the terminal type """
        quote_index = self.token_lines[self.line_num].find(">")
        return self.token_lines[self.line_num][1:quote_index]

def JackAnalyzer(file):
    input_file = file
    # Square/Main.jack
    print("Processing: ", input_file)
    # Create tokenizer file
    JackTokenizer(input_file)
            # Once value has been extracted from one line, return and add to "XxxT.xml"
    dir_index = input_file.find("/")
    ext_index = input_file.find(".")
    output_file_name = input_file[dir_index+1:ext_index]

    comp_engine = CompilationEngine(output_file_name +"T.xml", output_file_name)


if __name__ == "__main__":
    CLI().cmdloop()

#JackAnalyzer Square/Main.jack
