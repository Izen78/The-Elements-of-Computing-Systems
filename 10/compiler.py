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

    def __init__(self, input_stream, output_stream):
        self.input_file = open(input_stream, "r")
        self.token_lines = self.input_file.readlines()
        self.output_file = output_stream
            
        self.compileClass()
    def compileClass(self):
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.commands += "<class>\n<keyword>" + self.filtered_line + "</keyword>\n" 

        self.line_num += 1 # for identifier
        self.filtered_line = self.helperFilter()
        self.commands += "<identifier>" + self.filtered_line + "</identifier>\n"
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

    def compileClassVarDec(self):
        """ Handles 1 or more class variable declarations """
        self.commands += "<classVarDec>\n"
        self.filtered_line = self.helperFilter()
        self.commands += f"<keyword>{self.filtered_line}</keyword>\n"

        self.line_num += 1 # for type
        self.filtered_token = self.helperToken()
        self.filtered_line = self.helperFilter()
        if self.filtered_token == "keyword":
            self.commands += f"<{self.filtered_token}>{self.filtered_line}</{self.filtered_token}>\n"
        else:
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

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

        self.line_num += 1 # for return type
        self.filtered_line = self.helperFilter()
        if self.filtered_line in ("void", "int", "char", "boolean"):
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        else:
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

        self.line_num += 1 # for subroutineName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>(</symbol>\n"

        self.line_num += 1 # for param list - either type or )
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()

        self.commands += "<parameterList>\n"
        if self.filtered_line in ("int", "char", "boolean") or self.filtered_token == "identifier":
            self.compileParameterList()
        self.commands += "</parameterList>\n"
        self.commands += "<symbol>)</symbol>\n"


        self.commands += "<subroutineBody>\n"
        self.line_num += 1 # for {
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>{</symbol>\n"
        self.line_num += 1 # for "var" in varDec or "let", "if", "wile", "do", "return"
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "var":
            while self.filtered_line == "var":
                self.compileVarDec()
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
        self.commands += "<symbol>;</symbol>\n"
        
        self.commands += "</returnStatement>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

    def compileDo(self):
        self.commands += "<doStatement>\n"
        self.commands += "<keyword>do</keyword>\n"
        self.line_num += 1 # for subroutineName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.line_num += 1 # for ( or .
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "(":
            self.commands += "<symbol>(</symbol>\n"
            self.line_num += 1 # for expressionList which could also be empty
            self.filtered_line = self.helperFilter()
            self.commands += "<expressionList>\n" # need this even if empty
            # TODO: Make sure to return just after to ')'
            self.compileExpressionList()
            self.commands += "</expressionList>\n"
            self.commands += "<symbol>)</symbol>\n"
        elif self.filtered_line == ".":
            self.commands += "<symbol>.</symbol>\n"
            self.line_num += 1 # for subroutine name
            self.filtered_line = self.helperFilter()
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
            self.line_num += 1 # for (
            self.filtered_line = self.helperFilter()
            self.commands += "<symbol>(</symbol>\n"
            self.line_num += 1 # for expressionList which could also be empty
            self.filtered_line = self.helperFilter()
            self.commands += "<expressionList>\n" # need this even if empty
            self.compileExpressionList()
            self.commands += "</expressionList>\n"
            self.commands += "<symbol>)</symbol>\n"
        self.line_num += 1 # for ;
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>;</symbol>\n"

        self.commands += "</doStatement>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

    def compileExpressionList(self):
        # TODO: Make sure to return just after to ')'
        # either ) or expression
        self.filtered_line = self.helperFilter()
        while self.filtered_line != ")":
            # expression
            self.compileExpression() # either reaches , or )
            self.filtered_line = self.helperFilter()
            if self.filtered_line == ",":
                self.commands += "<symbol>,</symbol>\n"
                self.line_num += 1
                self.filtered_line = self.helperFilter()

    def compileExpression(self):

        op_list = ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]
        self.commands += "<expression>\n"
        self.compileTerm()
        self.filtered_line = self.helperFilter() # just after, either op or ignore
        while self.filtered_line in op_list:
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            self.line_num += 1 # set up compileTerm
            self.filtered_line = self.helperFilter()
            self.compileTerm()
            self.filtered_line = self.helperFilter()



        self.commands += "</expression>\n"
        # already incremented

    def compileTerm(self):
        self.commands += "<term>\n"
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()
        if self.filtered_token == "integerConstant":
            self.commands += f"<integerConstant>{self.filtered_line}</integerConstant>\n"
        elif self.filtered_token == "stringConstant":
            self.commands += f"<stringConstant>{self.filtered_line}</stringConstant>\n"
        elif self.filtered_line in ("true", "false", "null", "this"):
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        elif self.filtered_token == "identifier":
            # either varname, varname[expr], subroutinecall
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
            self.line_num += 1 # for ., [, ( -> ignore if none of these
            self.filtered_line = self.helperFilter()
            if self.filtered_line == ".":
                self.commands += "<symbol>.</symbol>\n"
                self.line_num += 1 # for subroutine name
                self.filtered_line = self.helperFilter()
                self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
                self.line_num += 1 # for (
                self.filtered_line = self.helperFilter()
                self.commands += "<symbol>(</symbol>\n"
                self.line_num += 1 # for expressionList
                self.filtered_line = self.helperFilter()
                self.commands += "<expressionList>\n"
                self.compileExpressionList()
                self.commands += "</expressionList>\n"
                self.commands += "<symbol>)</symbol>\n"
            elif self.filtered_line == "(":
                self.commands += "<symbol>(</symbol>\n"
                self.line_num += 1 # for expressionList
                self.filtered_line = self.helperFilter()
                self.commands += "<expressionList>\n"
                self.compileExpressionList()
                self.commands += "</expressionList>\n"
                self.commands += "<symbol>)</symbol>\n"
            elif self.filtered_line == "[":
                self.commands += "<symbol>[</symbol>\n"
                self.line_num += 1
                self.filtered_line = self.helperFilter()
                self.compileExpression()
                self.commands += "<symbol>]</symbol>\n"
            else:
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
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            self.line_num += 1 # set up recursion
            self.filtered_line = self.helperFilter()
            self.compileTerm()


        self.commands += "</term>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

    def compileWhile(self):
        self.commands += "<whileStatement>\n"
        self.commands += "<keyword>while</keyword>\n"
        self.line_num += 1 # for (
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>(</symbol>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.compileExpression()
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

        self.commands += "</whileStatement>\n"
        self.line_num += 1
        self.filtered_line = self.helperFilter()

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
        self.line_num += 1 # for {
        self.filtered_line = self.helperFilter()
        self.commands += "<symbol>{</symbol>\n"
        self.line_num += 1 # for statements keyword
        self.filtered_line = self.helperFilter()
        self.commands += "<statements>\n"
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
        else:
            self.commands += "</ifStatement>\n"

    def compileLet(self):
        self.commands += "<letStatement>\n"
        self.commands += "<keyword>let</keyword>\n"
        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
        self.line_num += 1 # for [ or = 
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "[":
            self.commands += "<symbol>[</symbol>\n"
            self.line_num += 1
            self.filtered_line = self.helperFilter()
            self.compileExpression()
            self.commands += "<symbol>]</symbol>\n"
            self.line_num += 1 # for = 
            self.filtered_line = self.helperFilter()
        self.filtered_line = self.helperFilter()
        self.commands  += "<symbol>=</symbol>\n"
        # self.line_num += 1 # for expression
        self.line_num += 1
        self.filtered_line = self.helperFilter()
        self.compileExpression()
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

        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

        self.line_num += 1 # either , for loop or ; for recursion or exit
        self.filtered_line = self.helperFilter()
        while self.filtered_line == ",":
            self.commands += f"<symbol>{self.filtered_line}</symbol>\n"
            self.line_num += 1 # for next varName
            self.filtered_line = self.helperFilter()
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"
            self.line_num += 1 # sets up next iter of loop
            self.filtered_line = self.helperFilter()
        self.commands += "<symbol>;</symbol>"
        self.commands += "\n</varDec>\n"

        self.line_num += 1
        self.filtered_line = self.helperFilter()
        if self.filtered_line == "var":
            self.compileVarDec()




    def compileParameterList(self):
        self.filtered_line = self.helperFilter()
        self.filtered_token = self.helperToken()
        if self.filtered_token == "keyword":
            # int, char, boolean
            self.commands += f"<keyword>{self.filtered_line}</keyword>\n"
        else:
            # className
            self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

        self.line_num += 1 # for varName
        self.filtered_line = self.helperFilter()
        self.commands += f"<identifier>{self.filtered_line}</identifier>\n"

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
