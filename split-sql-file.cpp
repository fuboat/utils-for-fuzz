#include <cstdio>
#include <string>
#include <fstream>
#include <iostream>

using namespace std;

int main() {
  string input_file = "client_log.txt";
  string split_flag = "UNLOCK TABLES; COMMIT;";
  
  string line_string;

  int current_file_id = 0;
  string current_statements;

  ifstream f(input_file);

  while (true) {
    getline(f, line_string);
    
    if ((!f || line_string.substr(0, split_flag.length()) == split_flag) && !current_statements.empty()) {
      // Match the split flag.
      // Split Here.

      ofstream of(input_file + "." + to_string(current_file_id));

      of << current_statements;
      of.close();
      
      ++ current_file_id;
      current_statements = "";
    }
    
    current_statements += line_string;

    if (!f) {
      break;
    }
  }

  return 0;
}
