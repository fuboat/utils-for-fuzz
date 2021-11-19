import re


pattern_str = r"\s*(\d+)\s*Query\s*(.*)"
pattern = re.compile(pattern_str)


def analysis_log_file_content_line(log_content_line: str) -> (str, str):
    m = pattern.match(log_content_line)
    if m is None:
        return None
    else:
        return m.groups()


def analysis_log_file_content(log_content: str) -> list:
    content_lines = log_content.splitlines(keepends=False)
    query_id_to_stmts = {}

    cur = 0
    tot = len(content_lines)
    
    for line in content_lines:
        result = analysis_log_file_content_line(line)

        cur += 1
        
        print("[current: %s / %s]..." % (cur, tot))

        if result is not None:
            (query_id, stmt) = result

            query_id_to_stmts[query_id] = query_id_to_stmts.get(query_id, "")
            query_id_to_stmts[query_id] += stmt + "\n"

    return query_id_to_stmts.values()


def analysis_log_file(file_name: str) -> list:
    content = ""

    with open(file_name, "r") as f:
        content = f.read()

    testcases = analysis_log_file_content(content)

    return testcases


input_file_name = "/tmp/mysql_general.log"
output_file_name_prefix = "/root/mysql-tmin/sqlancer-testcases/sqlancer"

if __name__ == "__main__":
    testcases = analysis_log_file(input_file_name)

    index = 0

    for testcase in testcases:
        index += 1

        with open(output_file_name_prefix + str(index) + ".sql", "w") as f:
            f.write(testcase)
