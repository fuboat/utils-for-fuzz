#include <fstream>
#include <iostream>
#include <map>
#include <unordered_map>
#include <cassert>
#include <vector>

using namespace std;

int main(int argc, char ** argv) {

  if (argc != 3) {

    cerr << "need $1 for input file and $2 for output dir" << endl;
    
    return 1;
    
  }

  string output_dir(argv[2]);
  ifstream f(argv[1]);
  string line_string;
  unsigned long long db_ptr_v_prev = 0;
  string cur_statement;
  map<unsigned long long, vector<string> > id_to_sub_testcase;
  map<unsigned long long, string> id_to_whole_statement;
  while (true) {
    
    unsigned long long db_ptr_v;

    getline(f, line_string);
    
    if (!f || sscanf(line_string.c_str(), "<<<%llu>>>", & db_ptr_v) == 1) {

      /* GET WHOLE CUR STATEMENT! */

      string & all_statement_this_testcase = id_to_whole_statement[db_ptr_v_prev];
      
      if (cur_statement.find("sqlite3_close") == string::npos) {
	if (!cur_statement.empty() && cur_statement.find("SELECT*FROM\"main\".sqlite_master") == string::npos) {
	  all_statement_this_testcase += cur_statement + ";";
	} else {
	  // we ingore statement which is empty or contains select * from main.sqlite_master.
	  cur_statement = "";
	}
	// cerr << "|||" << cur_statement;	
      } else {
	if (!all_statement_this_testcase.empty()) {
	  id_to_sub_testcase[db_ptr_v_prev].push_back(all_statement_this_testcase);
	  all_statement_this_testcase = "";
	}
      }

      cur_statement = "";
      
      /* HANDLE! */
      
      if (!f || db_ptr_v_prev != db_ptr_v) {
	// cerr << "<<<" << db_ptr_v << ">>>" << endl;
	// cerr << "------------------------" << endl;
	// cerr << all_statement_this_testcase;
	cur_statement = "";
	// all_statement_this_testcase = "";
      }
      
      db_ptr_v_prev = db_ptr_v;
    } else {
      cur_statement += line_string;
      cur_statement += "\n";
    }

    if (!f) {
      break;
    }
  }

  for (const auto & id_stmts_p : id_to_whole_statement) {
    if (!id_stmts_p.second.empty()) {
      id_to_sub_testcase[id_stmts_p.first].push_back(id_stmts_p.second);
    }
  }

  system(("mkdir -p " + output_dir).c_str());
  
  for (const auto & id_cases_p : id_to_sub_testcase) {
    const auto & id = id_cases_p.first;
    int index = 0;
    for (const auto & testcase : id_cases_p.second) {
      ofstream of(output_dir + "/" +
		  to_string(id) + ".sql." +
		  to_string(index));
      ++ index;
      of << testcase;
    }
  }
  
  return 0;
  
}
