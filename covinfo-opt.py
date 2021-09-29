import sys

class TestCaseInfo:
    def __init__(self):
        self.source_file_infos = []

    def __str__(self):
        result = "TN:\n" + "".join([str(x) for x in self.source_file_infos])
        return result

    def reverse(self):
        for x in self.source_file_infos:
            x.reverse()

    def combine(self, x):
        x_path_name_to_infos = {}
        
        for x_source_file in x.source_file_infos:
            x_source_file: SourceFileInfo = x_source_file
            x_path_name_to_infos[x_source_file.source_file_path] = \
                x_path_name_to_infos.get(x_source_file.source_file_path, [])
            x_path_name_to_infos[x_source_file.source_file_path].append(x_source_file)
        
        for self_source_file in self.source_file_infos:
            self_source_file: SourceFileInfo = self_source_file
            for x_source_file in x_path_name_to_infos.get(self_source_file.source_file_path, []):
                self_source_file.combine(x_source_file)


class SourceFileInfo:
    n_functions_found = 0   # FNF
    n_functions_hit = 0     # FNH
    n_branches_found = 0    # BRF
    n_branches_hit = 0      # BRH
    n_lines_executed = 0    # LH
    n_lines_inst = 0        # LF

    def __init__(self):
        self.source_file_path = ""
        self.function_infos = []
        self.branch_infos = []
        self.line_infos = []
    
    def __str__(self):
        sys.stderr.write("Working on file: %s\n" % self.source_file_path)

        functions_result = "".join([str(x) for x in self.function_infos])
        lines_result = "".join([str(x) for x in self.line_infos])

        result = """SF:{path}
{functions_result}FNF:{func_found}
FNH:{func_hit}
{lines_result}LF:{line_found}
LH:{line_execute}
end_of_record
""".format(path=self.source_file_path,
           functions_result=functions_result,
           func_found=self.n_functions_found,
           func_hit=self.n_functions_hit,
           lines_result=lines_result,
           line_found=self.n_lines_inst,
           line_execute=self.n_lines_executed)
        return result

    def reverse(self):
        self.n_branches_hit *= -1
        self.n_functions_hit *= -1
        self.n_lines_executed *= -1

        for x in self.function_infos:
            x.reverse()
        # for x in self.branch_infos:
        #     x.reverse()
        for x in self.line_infos:
            x.reverse()

    def combine(self, x):
        # sys.stderr.write("Current Source File: %s\n" % self.source_file_path)
        
        if self.source_file_path == x.source_file_path:
            self.n_functions_found = \
                max(self.n_functions_found, x.n_functions_found)
            self.n_functions_hit += x.n_functions_hit
            x.n_functions_hit = 0
            self.n_branches_found = \
                max(self.n_branches_found, x.n_branches_found)
            self.n_branches_hit += x.n_branches_hit
            x.n_branches_hit = 0
            self.n_lines_inst = \
                max(self.n_lines_inst, x.n_lines_inst)
            self.n_lines_executed += x.n_lines_executed
            x.n_lines_executed = 0

            x_func_name_to_infos = {}

            for x_func in x.function_infos:
                x_func: FunctionInfo = x_func
                x_func_name_to_infos[x_func.function_name] = x_func_name_to_infos.get(x_func.function_name, [])
                x_func_name_to_infos[x_func.function_name].append(x_func)
            
            for self_func in self.function_infos:
                self_func: FunctionInfo = self_func
                for x_func in x_func_name_to_infos.get(self_func.function_name, []):
                    self_func.combine(x_func)

            x_line_name_to_infos = {}

            for x_line in x.line_infos:
                x_line: LineInfo = x_line
                x_line_name_to_infos[x_line.line_number] = x_line_name_to_infos.get(x_line.line_number, [])
                x_line_name_to_infos[x_line.line_number].append(x_line)
            
            for self_line in self.line_infos:
                self_line: LineInfo = self_line
                for x_line in x_line_name_to_infos.get(self_line.line_number, []):
                    self_line.combine(x_line)


class FunctionInfo:
    function_name = ""                    # FN, FNDA
    execute_count = None                  # FNDA
    line_number_of_function_start = None  # FN

    def __str__(self):
        if self.execute_count is not None:
            return "FNDA:%s,%s\n" % (self.execute_count, self.function_name)
        elif self.line_number_of_function_start is not None:
            return "FN:%s,%s\n" % (self.line_number_of_function_start,
                                   self.function_name)
        else:
            assert False

    def reverse(self):
        if self.execute_count is not None:
            self.execute_count *= -1

    def combine(self, x):        
        if self.function_name == x.function_name and \
           self.line_number_of_function_start == \
           x.line_number_of_function_start and \
           self.execute_count is not None and \
           x.execute_count is not None:
            self.execute_count += x.execute_count
            x.execute_count = 0


class BranchInfo:
    line_number = -1        # BRDA
    block_number = -1       # BRDA
    branch_number = -1      # BRDA
    taken = -1              # BRDA


class LineInfo:
    line_number = -1        # DA
    execution_count = 0     # DA
    checksum = ""           # DA

    def __str__(self):
        return "DA:%s,%s\n" % (self.line_number, self.execution_count)

    def reverse(self):
        self.execution_count *= -1

    def combine(self, x):
        if self.line_number == x.line_number:
            self.execution_count += x.execution_count
            x.execution_count = 0


def parser_one_line(line_string: str, test_case_info: TestCaseInfo):
    if line_string == "end_of_record":
        pass
    else:
        flag = line_string.split(":")[0]
        arguments = line_string.split(":")[1].split(",")

        if flag == "TN":
            return
        elif flag == "SF":
            # SF <path>
            new_source_file: SourceFileInfo = SourceFileInfo()
            new_source_file.source_file_path = arguments[0]
            test_case_info.source_file_infos.append(new_source_file)
        elif flag == "FN":
            # FN <number> <function_name>
            new_function_info: FunctionInfo = FunctionInfo()
            new_function_info.line_number_of_function_start = int(arguments[0])
            new_function_info.function_name = arguments[1]

            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.function_infos.append(new_function_info)
        elif flag == "FNDA":
            # FNDA <number> <function_name>
            new_function_info: FunctionInfo = FunctionInfo()
            new_function_info.execute_count = int(arguments[0])
            new_function_info.function_name = arguments[1]

            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.function_infos.append(new_function_info)
        elif flag == "FNF":
            # FNF <number>
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.n_functions_found = int(arguments[0])
        elif flag == "FNH":
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.n_functions_hit = int(arguments[0])
        elif flag == "BRF":
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.n_branches_found = int(arguments[0])
        elif flag == "BRH":
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.n_branches_hit = int(arguments[0])
        elif flag == "LH":
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.n_lines_executed = int(arguments[0])
        elif flag == "LF":
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.n_lines_inst = int(arguments[0])
        elif flag == "BRDA":
            # new_branch_info: BranchInfo = BranchInfo()
            # new_branch_info.line_number = int(arguments
            pass
        elif flag == "DA":
            new_line_info: LineInfo = LineInfo()
            new_line_info.line_number = int(arguments[0])
            new_line_info.execution_count = int(arguments[1])
            cur_source_file_info: SourceFileInfo = test_case_info.source_file_infos[-1]
            cur_source_file_info.line_infos.append(new_line_info)
        else:
            assert False


def parser_whole_input(whole_input, test_case_info: TestCaseInfo):
    """Lalala."""
    for line_string in whole_input.splitlines():
        parser_one_line(line_string, test_case_info)


info_file_name1 = "/root/jingzhou_workspace/utils-for-fuzz/cases/create_table.info"
info_file_name2 = "/root/jingzhou_workspace/utils-for-fuzz/cases/create_table_and_insert.info"

if __name__ == "__main__":
    testcase_info1: TestCaseInfo = TestCaseInfo()
    testcase_info2: TestCaseInfo = TestCaseInfo()    

    with open(info_file_name1, "r") as f:
        parser_whole_input(f.read(), testcase_info1)

    with open(info_file_name2, "r") as f:
        parser_whole_input(f.read(), testcase_info2)

    testcase_info1.reverse()
    testcase_info1.combine(testcase_info2)

    print(testcase_info1)
