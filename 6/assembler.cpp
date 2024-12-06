#include <cctype>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

enum commandType {
  A_COMMAND, // 0
  C_COMMAND, // 1
  L_COMMAND, // 2
  WHITESPACE // 3
};

class SymbolTableModule {
public:
  static std::vector<pair<string, int>> symbol_table;

  // Constructor
  SymbolTableModule() {
    // Predefined symbols added to the vector
    symbol_table.push_back({"SP", 0});
    symbol_table.push_back({"LCL", 1});
    symbol_table.push_back({"ARG", 2});
    symbol_table.push_back({"THIS", 3});
    symbol_table.push_back({"THAT", 4});
    symbol_table.push_back({"R0", 0});
    symbol_table.push_back({"R1", 1});
    symbol_table.push_back({"R2", 2});
    symbol_table.push_back({"R3", 3});
    symbol_table.push_back({"R4", 4});
    symbol_table.push_back({"R5", 5});
    symbol_table.push_back({"R6", 6});
    symbol_table.push_back({"R7", 7});
    symbol_table.push_back({"R8", 8});
    symbol_table.push_back({"R9", 9});
    symbol_table.push_back({"R10", 10});
    symbol_table.push_back({"R11", 11});
    symbol_table.push_back({"R12", 12});
    symbol_table.push_back({"R13", 13});
    symbol_table.push_back({"R14", 14});
    symbol_table.push_back({"R15", 15});
    symbol_table.push_back({"SCREEN", 16384});
    symbol_table.push_back({"KBD", 24576});
  }
  void addEntry(string symbol, int address) {
    if (!contains(symbol))
      symbol_table.push_back({symbol, address});
    else {
      cout << "Symbol: " << symbol << " is already in the symbol table" << '\n';
    }
  }
  bool contains(string symbol) {
    // Check if the symbol is either predefined or in the symbol table
    for (const auto &entry : symbol_table) {
      if (entry.first == symbol) {
        return true;
      }
    }
    return false;
  }

  int getAddress(string symbol) {
    for (const auto &entry : symbol_table) {
      if (entry.first == symbol) {
        return entry.second;
      }
    }
    return -1; // Return -1 if the symbol is not found
  }
};
vector<pair<string, int>> SymbolTableModule::symbol_table;

class ParserModule {
public:
  bool hasMoreCommands = false;
  string current_command = "";
  commandType command_type;
  string symbol;
  string dest;
  string comp;
  string jump;
  char first_char;
  string line;
  int len;
  bool has_dest = false;
  bool has_jump = false;
  int equal_index;
  int colon_index;
  SymbolTableModule symbol_table;
  static int line_num; // ROM ADDRESS
  static int ram_num;  // RAM ADDRESS
  bool second_pass = false;

  ParserModule(string line) {
    // output_file << "dinosaur";
    this->line = line;
  }

  // I want to get the entire line and the first character
  bool has_more_commands() {
    this->hasMoreCommands = false;
    this->len = 0;

    // Trim leading whitespace
    int i = 0;
    while (i < line.length() && isspace(line[i])) {
      i++;
    }

    // If the line is empty or starts with a comment, return false
    if (i >= line.length() ||
        (line[i] == '/' && i + 1 < line.length() && line[i + 1] == '/')) {
      this->command_type = WHITESPACE;
      return this->hasMoreCommands;
    }

    // Line has meaningful content
    this->hasMoreCommands = true;
    return this->hasMoreCommands;
  }

  void advance() {
    if (has_more_commands() == true) {
      this->current_command = this->line;

      this->command_type = commandType();
      if (command_type == C_COMMAND) {
        this->dest = get_dest();
        this->jump = get_jump();
        this->comp = get_comp();
      } else
        this->symbol = get_symbol();
    }
  }

  commandType commandType() {
    // @val  is A_COMMAND
    // (Xxx) is L_COMMAND
    // else C_COMMAND
    int i = 0;
    while (line[i] == ' ') {
      i++;
    }
    enum commandType command_type;
    if (this->line[i] == '@') {
      this->command_type = A_COMMAND;
    } else if (this->line[i] == '(') {
      this->command_type = L_COMMAND;
    } else
      this->command_type = C_COMMAND;

    return this->command_type;
  }

  // string get_symbol() {
  //   this->symbol = "";
  //   // If A-Instruction @Val,
  //   // If L-Instruction (Val)
  //   int i = 0;
  //   while (i < line.length()) {
  //     if (line[i] == '@' ||
  //         line[i] == '(') { // i stops just before value is read
  //       break;
  //     }
  //     i++;
  //   }
  //   i++; // shifts to first characer in symbol value
  //
  //   if (this->command_type == A_COMMAND) {
  //     if (isdigit(line[i])) { // value is integer
  //       while (i < line.length() - 1) {
  //         if (line[i] != ' ' && line[i] != ')') {
  //           this->symbol += line[i];
  //         }
  //         i++;
  //       }
  //       int value = stoi(this->symbol);
  //       this->symbol = bitset<15>(value).to_string();
  //     } else { // value is variable
  //       while (i < line.length() - 1 && (isalnum(line[i]) || line[i] == '.'
  //       ||
  //                                        line[i] == '$' || line[i] == '_')) {
  //         this->symbol += line[i];
  //         i++;
  //       }
  //       cout << "Parsed symbol: " << this->symbol << '\n';
  //       if (ParserModule::symbol_table.contains(
  //               this->symbol)) { // symbol already inside
  //         int value = ParserModule::symbol_table.getAddress(this->symbol);
  //         this->symbol = bitset<15>(value).to_string();
  //       } else { // symbol not inside and must be added and mapped
  //         if (ParserModule::symbol_table.contains(this->symbol)) {
  //           ParserModule::symbol_table.addEntry(this->symbol,
  //                                               ParserModule::ram_num);
  //           cout << "Adding entry " << this->symbol
  //                << " at ram location: " << ParserModule::ram_num << '\n';
  //           ParserModule::ram_num++;
  //           int value = ParserModule::symbol_table.getAddress(this->symbol);
  //           this->symbol = bitset<15>(value).to_string();
  //         }
  //       }
  //     }
  //   } else if (this->command_type == L_COMMAND) {
  //     while (line[i] != ')') {
  //       this->symbol += line[i];
  //       i++;
  //     }
  //     symbol_table.addEntry(this->symbol, ParserModule::line_num);
  //   }
  //
  //   // TODO: Convert the string decimals into integers and then binary
  //
  //   return this->symbol; // returns 15-bit string
  // }
  string get_symbol() {
    this->symbol = "";
    int i = 0;
    while (i < line.length()) {
      if (line[i] == '@' || line[i] == '(') {
        break;
      }
      i++;
    }
    i++; // move to first character in symbol value

    if (this->command_type == A_COMMAND && second_pass == true) {
      if (isdigit(line[i])) { // value is integer
        while (i < line.length() - 1) {
          if (line[i] != ' ' && line[i] != ')') {
            this->symbol += line[i];
          }
          i++;
        }
        int value = stoi(this->symbol);
        this->symbol =
            bitset<15>(value).to_string(); // Convert integer to 15-bit binary
      } else { // value is a variable (e.g., memory.0)
        while (i < line.length() - 1 && (isalnum(line[i]) || line[i] == '.' ||
                                         line[i] == '$' || line[i] == '_')) {
          this->symbol += line[i];
          i++;
        }

        if (ParserModule::symbol_table.contains(
                this->symbol)) { // symbol already inside
          int value = ParserModule::symbol_table.getAddress(this->symbol);
          this->symbol =
              bitset<15>(value)
                  .to_string(); // Convert symbol address to 15-bit binary
        } else { // symbol not inside and must be added and mapped
          ParserModule::symbol_table.addEntry(this->symbol,
                                              ParserModule::ram_num);

          cout << "Adding entry " << this->symbol
               << " at ram location: " << ParserModule::ram_num << '\n';
          this->symbol =
              bitset<15>(ParserModule::ram_num)
                  .to_string(); // Add new symbol and convert to 15-bit
          ParserModule::ram_num++;
        }
      }
    } else if (this->command_type == L_COMMAND) {
      while (line[i] != ')') {
        this->symbol += line[i];
        i++;
      }
      symbol_table.addEntry(this->symbol, ParserModule::line_num);
    }

    return this->symbol; // returns 15-bit string
  }

  string get_dest() { // get dest before '='
    this->dest = "";
    this->equal_index = 0;
    for (int i = 0; i < line.length(); i++) {
      if (line[i] == '=') {
        this->has_dest = true;
        this->equal_index = i;
        break;
      }
    }

    if (this->has_dest == true) {
      // cout << this->equal_index;
      int i = 0;
      while (i < this->equal_index) {
        if (line[i] != ' ')
          this->dest += line[i];
        i++;
      }
    }
    return this->dest;
  }

  string get_comp() { // check if ';' and '==' exists and loop between indices,
                      // otherwise just grab the entire word
    this->comp = "";
    if (this->has_jump == true && this->has_dest == true) {
      int i = this->equal_index + 1;
      while (i < colon_index) {
        if (line[i] != ' ')
          this->comp += line[i];
        i++;
      }
    } else if (this->has_jump == true) {
      int i = 0;
      while (i < colon_index) {
        if (line[i] != ' ')
          this->comp += line[i];
        i++;
      }
    } else if (this->has_dest == true) {
      int i = equal_index + 1;
      while (i < line.length() - 1) {
        if (line[i] != ' ')
          this->comp += line[i];
        i++;
      }
    } else {
      int i = 0;
      while (i < line.length() - 1) {
        if (line[i] != ' ')
          this->comp += line[i];
        i++;
      }
    }
    return this->comp;
  }

  string get_jump() { // get after ';'
    this->jump = "";
    this->colon_index = 0;
    for (int i = 0; i < line.length() - 1; i++) {
      if (line[i] == ';') {
        this->has_jump = true;
        this->colon_index = i;
        break;
      }
    }

    if (this->has_jump == true) {
      // cout << this->colon_index;
      int i = this->colon_index + 1;
      while (i < line.length() - 1) {
        if (line[i] != ' ')
          this->jump += line[i];
        i++;
      }
    }
    return this->jump;
  }
};

class CodeModule {
public:
  CodeModule() {}

  string codeDest(string dest) {
    string encoded_dest = "";
    if (dest == "")
      encoded_dest = "000";
    else if (dest == "M")
      encoded_dest = "001";
    else if (dest == "D")
      encoded_dest = "010";
    else if (dest == "MD")
      encoded_dest = "011";
    else if (dest == "A")
      encoded_dest = "100";
    else if (dest == "AM")
      encoded_dest = "101";
    else if (dest == "AD")
      encoded_dest = "110";
    else if (dest == "AMD")
      encoded_dest = "111";
    else
      cout << "INVALID DESTINATION";

    return encoded_dest;
  }

  string codeJump(string jump) {
    string encoded_jump = "";
    if (jump == "")
      encoded_jump = "000";
    else if (jump == "JGT")
      encoded_jump = "001";
    else if (jump == "JEQ")
      encoded_jump = "010";
    else if (jump == "JGE")
      encoded_jump = "011";
    else if (jump == "JLT")
      encoded_jump = "100";
    else if (jump == "JNE")
      encoded_jump = "101";
    else if (jump == "JLE")
      encoded_jump = "110";
    else if (jump == "JMP")
      encoded_jump = "111";
    else
      cout << "INVALID JUMP: " << jump;
    return encoded_jump;
  }

  string codeComp(string code) {
    string encoded_comp = "";
    if (code == "0")
      encoded_comp = "0101010";
    else if (code == "1")
      encoded_comp = "0111111";
    else if (code == "-1")
      encoded_comp = "0111010";
    else if (code == "D")
      encoded_comp = "0001100";
    else if (code == "A")
      encoded_comp = "0110000";
    else if (code == "!D")
      encoded_comp = "0001101";
    else if (code == "!A")
      encoded_comp = "0110001";
    else if (code == "-D")
      encoded_comp = "0001111";
    else if (code == "-A")
      encoded_comp = "0110011";
    else if (code == "D+1")
      encoded_comp = "0011111";
    else if (code == "A+1")
      encoded_comp = "0110111";
    else if (code == "D-1")
      encoded_comp = "0001110";
    else if (code == "A-1")
      encoded_comp = "0110010";
    else if (code == "D+A")
      encoded_comp = "0000010";
    else if (code == "D-A")
      encoded_comp = "0010011";
    else if (code == "A-D")
      encoded_comp = "0000111";
    else if (code == "D&A")
      encoded_comp = "0000000";
    else if (code == "D|A")
      encoded_comp = "0010101";
    else if (code == "M")
      encoded_comp = "1110000";
    else if (code == "!M")
      encoded_comp = "1110001";
    else if (code == "-M")
      encoded_comp = "1110011";
    else if (code == "M+1")
      encoded_comp = "1110111";
    else if (code == "M-1")
      encoded_comp = "1110010";
    else if (code == "D+M")
      encoded_comp = "1000010";
    else if (code == "D-M")
      encoded_comp = "1010011";
    else if (code == "M-D")
      encoded_comp = "1000111";
    else if (code == "D&M")
      encoded_comp = "1000000";
    else if (code == "D|M")
      encoded_comp = "1010101";
    else
      cout << "INVALID COMPUTATION: " << code;

    return encoded_comp;
  }
};

int ParserModule::line_num = 0;
int ParserModule::ram_num = 16;
int main() {

  // Main Loop (Symbol-less)
  // 1st Pass
  // Parse 1st command if exists and if it is C-instruction go to Code Module
  // if A-instruction convert decimal numbers into 0, 15-bits for instruction
  fstream input_stream;
  fstream output_stream;
  fstream input_stream2;

  string in_file = "pong/Pong.asm";
  string out_file = "Pong.hack";

  input_stream2.open(in_file);
  input_stream.open(in_file);
  output_stream.open(out_file, ios::out | ios::trunc);

  string line;
  string line2;
  int i = 0;

  // pass 1 - get all of labels and put them in symboltable as well as
  // initialise all pre-defined labels
  while (getline(input_stream, line)) {
    ParserModule parser(line);
    parser.advance();
    if (parser.command_type == A_COMMAND || parser.command_type == C_COMMAND) {
      parser.line_num++;
    } else if (parser.command_type == L_COMMAND) {
      parser.symbol_table.addEntry(parser.symbol, parser.line_num);
    }
  }

  // pass 2 - go through all code and put any variables found in @XXX  if it is
  // not a number then check if in talbe and return value or add it and map to
  // next memory address

  while (getline(input_stream2, line2)) {

    ParserModule parser2(line2);
    CodeModule code_module;
    parser2.second_pass = true;
    parser2.advance(); // has_more_commands, command_type and all fields
    // cout << parser2.has_more_commands();
    if (parser2.hasMoreCommands == true) { // TODO: FIX THIS
      // cout << "hello";
      string command = "";
      if (parser2.command_type == C_COMMAND) {
        command = "111";
        string command_comp = code_module.codeComp(parser2.comp);
        string command_dest = code_module.codeDest(parser2.dest);
        string command_jump = code_module.codeJump(parser2.jump);
        command += command_comp + command_dest + command_jump + '\n';
        output_stream << command;
      } else if (parser2.command_type == A_COMMAND) {
        command = "0";
        command += parser2.symbol + '\n';
        cout << parser2.symbol << '\n';
        output_stream << command;
      }
      // output_stream << command;
    }
  }

  input_stream.close();
  output_stream.close();
  input_stream2.close();
  return 0;
}

// symbols are labels and variables such as i=1 or pre-defined variables
