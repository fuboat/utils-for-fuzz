#include <string>
#include <iostream>
#include <fstream>

using namespace std;

string replace_char(string const & stmt, char old_char, char new_char) {

    string res;

    for (char c : stmt) {
        if (c == old_char) {
            res.push_back(new_char);
        } else {
            res.push_back(c);
        }
    }

    return res;

}

int main(int argc, char ** argv) {

    if (argc != 3) {

        cerr << "need $1 for input file and $2 for output file" << endl;

    }

    ofstream out_f(argv[2]);
    ifstream in_f(argv[1]);

    string line_string;
    string command;

    bool command_start = false;

    int line_number = 0;

    while (getline(in_f, line_string)) {
        
        ++ line_number;

        cerr << "current line: " << line_number << endl;

        if (line_string.find('[') != string::npos &&
            line_string.find(']') != string::npos) {
            
            line_string = line_string.substr(line_string.find(']') + 1);
        }

        if (!command_start &&
            line_string.find("db.runCommand") != string::npos) {
            command_start = true;
            command = "";
        }

        if (command_start)
            command += line_string;

        if (command_start && line_string.find(");") != string::npos) {
            command_start = false;
            command = replace_char(command, '\t', ' ');
            command = replace_char(command, '\r', ' ');
            command = replace_char(command, '\n', ' ');
            out_f << command << endl;
            out_f.flush();
            command = "";
        }
    }

    out_f << command << endl;
    out_f.flush();

    return 0;
}