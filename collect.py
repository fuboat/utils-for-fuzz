import re
import shelve
from contextlib import closing
import pprint
import numpy as np 
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib

def number_with_suffix_to_number(number_expr: str) -> float:
    x = float(number_expr.rstrip("kM"))    
    if number_expr.endswith("k"):
        base_number = 1000
    elif number_expr.endswith("M"):
        base_number = 1000000
    else:
        base_number = 1

    return x * base_number


pattern_str = r"([^\s:]+):?.*:?(\d+)\s*days,\s*(\d+)\s*hrs,\s*(\d+)\s*min,\s*(\d+)\s*sec:?\s*(\d+\.\d+)%\s*/\s*(\d+\.\d+)%:?\s*(\d+(?:\.\d+)?[Mk]?):?\s*(\d+(?:\.\d+)?[Mk]?):?\s*(\d+(?:\.\d+)?[Mk]?)\s*\(.*\):?\s*(\d+(?:\.\d+)?[Mk]?)\s*\(.*\):?\s*(\d+):?\s*(\d+)\s*"
pattern = re.compile(pattern_str)

pattern_simple_str = r"(?:.*:\s)?([^\s:]+)\s*:?(?:.*:?)?(\d+)\s*days,\s*(\d+)\s*hrs,\s*(\d+)\s*min,\s*(\d+)\s*sec\s*:?\s*(\d+\.\d+)%\s*/\s*(\d+\.\d+)%\s*:?\s*(\d+(?:\.\d+)?[Mk]?)\s*:?\s*(\d+(?:\.\d+)?[Mk]?)\s*:?\s*(\d+(?:\.\d+)?[Mk]?)\s*\(.*\)\s*"
pattern_simple = re.compile(pattern_simple_str)

class Recorder:
    container_name = None
    run_time_day = None
    run_time_hr = None
    run_time_min = None
    run_time_sec = None
    current_map = None
    map_density = None
    total_execs = None
    total_paths = None
    cycle_done = None
    total_crashes = None

    def parser(self, content: str) -> bool:
        m = pattern.match(content)

        if m == None:
            return False
        else:
            (self.container_name, self.run_time_day, self.run_time_hr, self.run_time_min, self.run_time_sec, self.current_map, self.map_density, self.total_execs, self.total_paths, self.new_edges_on, self.now_processing, self.cycles_done, self.total_crashes) = m.groups()
            return True

        
    def parser_simple(self, content: str) -> bool:
        m = pattern_simple.match(content)

        if m == None:
            return False
        else:
            (self.container_name, self.run_time_day, self.run_time_hr, self.run_time_min, self.run_time_sec, self.current_map, self.map_density, self.total_execs, self.total_paths, self.new_edges_on) = m.groups()
            self.container_name = self.container_name.rstrip("*-")
            return True
        

    def get_time_sec(self):
        return ((int(self.run_time_day) * 24 + int(self.run_time_hr)) * 60 + int(self.run_time_min)) * 60 + int(self.run_time_sec)

    
    def get_map_density_float(self):
        return float(self.map_density)

    
    def get_total_paths(self):
        return number_with_suffix_to_number(self.total_paths)

    
    def get_new_edges_on(self):
        return number_with_suffix_to_number(self.new_edges_on)

    
    def get_cycle_done(self):
        return number_with_suffix_to_number(self.cycles_done)

    
    def get_total_crashes(self):
        return number_with_suffix_to_number(self.total_crashes)

    
    def get_total_execs(self):
        return number_with_suffix_to_number(self.total_execs)

    
    def get_container_name(self):
        return self.container_name

    
    def get_all(self):
        return {
            "container_name" : self.get_container_name(),
            "time_sec" : self.get_time_sec(),
            "map_density" : self.get_map_density_float(),
            "total_paths" : self.get_total_paths(),
            "total_execs" : self.get_total_execs(),
            "new_edges_on" : self.get_new_edges_on(),
            "cycle_done" : self.get_cycle_done(),
            "total_crashes" : self.get_total_crashes(),
            "new paths": 0 # HINT: This will be calc when load file.
        }

    def get_all_simple(self):
        return {
            "container_name" : self.get_container_name(),
            "time_sec" : self.get_time_sec(),
            "map_density" : self.get_map_density_float(),
            "total_paths" : self.get_total_paths(),
            "total_execs" : self.get_total_execs(),
            "new_edges_on" : self.get_new_edges_on(),
            "new paths": 0 # HINT: This will be calc when load file.
        }


log_file_path = "/root/tmux_status.log"
log_file_path_sqlite = "/root/tmux_status_log_new.txt"
log_file_path_sqlite2 = "/root/tmux_status_log_new_rnd2.txt"
log_file_path_sqlite3 = "/root/tmux_status_log_new_rnd3.txt"

container_data_map = {}
container_cur_time_map = {}
container_start_path_map = {}

def load_from_log_file():
    """
    This Function will load data EXCEPT sqlite
    into variable $container_data_map and $container_cur_time_map 
    by parsing the file $log_file_path.
    """
    with open(log_file_path) as f:
        while True:
            text_line = f.readline()

            if not text_line:
                break

            if "sqlite" in text_line:
                # SKIP SQLITE.
                continue
            
            x = Recorder()

            if not x.parser_simple(text_line):
                continue
        
            # parser success! record the data.
            if container_data_map.get(x.get_container_name()) == None:
                container_data_map[x.get_container_name()] = []
                container_cur_time_map[x.get_container_name()] =  -1
                container_start_path_map[x.get_container_name()] = x.get_total_paths()
            
            if container_cur_time_map.get(x.get_container_name()) > x.get_time_sec():
                container_data_map[x.get_container_name()] =  []
                container_start_path_map[x.get_container_name()] = x.get_total_paths()

            data = x.get_all_simple()
            data["new_paths"] = x.get_total_paths() - container_start_path_map[x.get_container_name()]
            
            container_cur_time_map[x.get_container_name()] = x.get_time_sec()
            container_data_map.get(x.get_container_name()).append(data)

    with closing(shelve.open("tmux_status_log_python", "c")) as shelf:
        shelf["data"] = container_data_map
        shelf["time"] = container_cur_time_map


def fix_data():
    """
    This function is used to fix some unfound or broken data.
    Just use the latest data to fill the unfound data.
    """

    for container_name in container_data_map:
        data = container_data_map[container_name]

        # when time is fewer than 48h:
        # fill data.
        while data[-1]["time_sec"] < 72 * 3600:
            new_data = dict(data[-1])
            new_data["time_sec"] += 60
            data.append(new_data)

    with closing(shelve.open("tmux_status_log_python", "c")) as shelf:
        shelf["data"] = container_data_map
        shelf["time"] = container_cur_time_map
            
        
def load_from_log_file_sqlite(file_path: str):
    """
    This Function will load data. HINT: sqlite only. Because the format of sqlite is a little bit different.
    into variable $container_data_map and $container_cur_time_map 
    by parsing the file $log_file_path.
    """
    with open(file_path) as f:
        while True:
            text_line = f.readline()

            if not text_line:
                break

            if not ("sqlite" in text_line):
                # SKIP all records except sqlite.
                continue
            
            x = Recorder()

            if not x.parser_simple(text_line):
                continue

            # print("parser SQLITE success! container_name:{container}".format(container=x.get_container_name()))
        
            # parser success! record the data.
            if container_data_map.get(x.get_container_name()) == None:
                container_data_map[x.get_container_name()] = []
                container_cur_time_map[x.get_container_name()] =  -1
                container_start_path_map[x.get_container_name()] = x.get_total_paths()
            
            if container_cur_time_map.get(x.get_container_name()) > x.get_time_sec():
                container_data_map[x.get_container_name()] =  []
                container_start_path_map[x.get_container_name()] = x.get_total_paths()

            data = x.get_all_simple()
            data["new_paths"] = x.get_total_paths() - container_start_path_map[x.get_container_name()]
            
            container_cur_time_map[x.get_container_name()] = x.get_time_sec()
            container_data_map.get(x.get_container_name()).append(data)

    with closing(shelve.open("tmux_status_log_python", "c")) as shelf:
        shelf["data"] = container_data_map
        shelf["time"] = container_cur_time_map
        
def load_from_old():
    global container_data_map
    global container_cur_time_map

    with closing(shelve.open("tmux_status_log_python", "r")) as shelf:
        container_data_map = shelf["data"]
        container_cur_time_map = shelf["time"]


def formatnum(x, pos):
    return '$%.0f$k' % (x/1000)

        
def main(x_label, y_label, options, line_labels, title, x_label_text, y_label_text, map_size, ax):
    global container_data_map
    global container_cur_time_map
    
    #################################################################
    ### the x label and y label decide what relationship to show. ###
    #################################################################
    
    ### option: time_sec, map_density, total_paths, new_edges_on, total_execs, new_paths, coverage

    # EXAMPLE:
    
    # x_label = "time_sec"
    # y_label = "map_density"


    #############################
    ### Set the data to show. ###
    #############################
    
    ### option:
    ### mariadb_full_1tmin, mariadb_full_1seq_2cmin_2, mariadb_full_1tmin-2seq, mariadb_full_1tmin-2seq-3cmin, mariadb_full_1seq_2random68307
    ### mysql_full_1tmin, mysql_full_1seq_2cmin_2, mysql_full_1tmin-2seq, mysql_full_1tmin-2seq-3cmin, mysql_full_1seq_2random68307
    ### pg_full_1seq_2cmin_2, pg_full_1seq_2random40727, pg_full_1tmin, pg_full_1tmin_2seq, pg_full_1tmin_2seq_3tmin, pg_full_in_format, pg_full_squirrel-default

    # EXAMPLE:
    
    # options = [ "mariadb_full_1seq_2cmin_2",
    #             "mariadb_full_1tmin",
    #             "mariadb_full_1tmin-2seq-3cmin",
    #             "mariadb_full_in_format",
    #             "mariadb_full_squirrel-default"]

    # options = ["pg_full_1seq_2cmin_2",
    #            "pg_full_1tmin",
    #            "pg_full_1tmin_2seq_3tmin",
    #            "pg_full_in_format",
    #            "pg_full_squirrel-default"]
    
    # options = [ "mysql_full_1seq_2cmin_2",
    #             "mysql_full_1tmin",
    #             "mysql_full_1tmin-2seq-3cmin",
    #             "mysql_full_in_format",
    #             "mysql_full_squirrel-default"]

    ###########################################################################
    ### The label of each. Please keep the order to match the correct line. ###
    ###########################################################################

    # EXAMPLE:

    # line_labels = ["Quarry",
    #                "tmin only",
    #                "tmin + Quarry",
    #                "original data",
    #                "squirrel default"]

    ################
    ### drawing. ###
    ################


    for option in options:
        for data in container_data_map[option]:
            data["coverage"] = data["map_density"] / 100 * map_size
    
    for option, line_label in zip(options, line_labels):
        x = [data[x_label] for data in container_data_map[option]]
        y = [data[y_label] for data in container_data_map[option]]
        ax.plot(x, y, label=line_label)

    #################################
    ### Set title and label text. ###
    #################################

    # EXAMPLE

    # title = "mariadb"
    # x_label_text = "time / s"
    # y_label_text = "coverage"
    
    ax.set_title(title)
    ax.set_xlabel(x_label_text)
    ax.set_ylabel(y_label_text)

    #######################
    ### Set axis range. ###
    #######################
    
    ax.set_xlim(xmin=200)
    ax.set_ylim(ymin=0)
    formatter = FuncFormatter(formatnum)
    ax.yaxis.set_major_formatter(formatter)
    #ax.set_xscale('log')
    
    # plt.grid(True,which="both", linestyle='--')

    ### Save.
    
    # plt.savefig("show.png")
    
            
if __name__ == "__main__":
    ######################
    #     load data      #
    ######################
    
    # load_from_log_file()
    # load_from_log_file_sqlite(log_file_path_sqlite)
    # load_from_log_file_sqlite(log_file_path_sqlite2)
    # load_from_log_file_sqlite(log_file_path_sqlite3)
    # fix_data()

    load_from_old()
    
    fig = plt.figure(figsize=(9, 7))
    # matplotlib.rc('xtick', labelsize=8) 
    # matplotlib.rc('ytick', labelsize=8)
    
    main(
        x_label='time_sec',
        y_label='coverage',
        options=['mariadb_full_1seq_2cmin_2', 'mariadb_full_1tmin', 'mariadb_full_1tmin-2seq-3cmin', 'mariadb_full_in_format', 'mariadb_full_squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel'],
        title='MariaDB Coverage',
        x_label_text='time/s',
        y_label_text='coverage',
        map_size=2**20,
        ax=fig.add_subplot(3, 4, 1))
    
    main(
        x_label='time_sec',
        y_label='coverage',
        options=['mysql_full_1seq_2cmin_2', 'mysql_full_1tmin', 'mysql_full_1tmin-2seq-3cmin', 'mysql_full_in_format', 'mysql_full_squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel'],
        title='MySQL Coverage',
        x_label_text='time/s',
        y_label_text='coverage',
        map_size=2**20,
        ax=fig.add_subplot(3, 4, 2))

    main(
        x_label='time_sec',
        y_label='coverage',
        options=['pg_full_1seq_2cmin_2', 'pg_full_1tmin', 'pg_full_1tmin_2seq_3tmin', 'pg_full_in_format', 'pg_full_squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel'],
        title='PostgreSQL Coverage',
        x_label_text='time/s',
        y_label_text='coverage',
        map_size=2**20,
        ax=fig.add_subplot(3, 4, 3))

    ############
    ##        ##
    ## SQLITE ##
    ##        ##
    ############

    main(
        x_label='time_sec',
        y_label='coverage',
        options=['unittest-seq', 'unittest_tmin', 'unittest_tmin', 'unittest', 'squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin only', 'original data', 'Squirrel'],
        title='SQLite Coverage',
        x_label_text='time/s',
        y_label_text='coverage',
        map_size=2**18,
        ax=fig.add_subplot(3, 4, 4))

    ################
    ##            ##
    ## SQLITE END ##
    ##            ##
    ################
    
    main(
        x_label='time_sec',
        y_label='new_paths',
        options=['mariadb_full_1seq_2cmin_2', 'mariadb_full_1tmin', 'mariadb_full_1tmin-2seq-3cmin', 'mariadb_full_in_format', 'mariadb_full_squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel'],
        title='MariaDB Paths',
        x_label_text='time/s',
        y_label_text='new paths',
        map_size=2**20,
        ax=fig.add_subplot(3, 4, 5))
        
    main(
        x_label='time_sec',
        y_label='new_paths',
        options=['mysql_full_1seq_2cmin_2', 'mysql_full_1tmin', 'mysql_full_1tmin-2seq-3cmin', 'mysql_full_in_format', 'mysql_full_squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel'],
        title='MySQL Paths',
        x_label_text='time/s',
        y_label_text='new paths',
        map_size=2**20,
        ax=fig.add_subplot(3, 4, 6))

    main(
        x_label='time_sec',
        y_label='new_paths',
        options=['pg_full_1seq_2cmin_2', 'pg_full_1tmin', 'pg_full_1tmin_2seq_3tmin', 'pg_full_in_format', 'pg_full_squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel'],
        title='PostgreSQL Paths',
        x_label_text='time/s',
        y_label_text='new paths',
        map_size=2**20,
        ax=fig.add_subplot(3, 4, 7))

    ############
    ##        ##
    ## SQLITE ##
    ##        ##
    ############

    main(
        x_label='time_sec',
        y_label='new_paths',
        options=['unittest-seq', 'unittest_tmin', 'unittest_tmin', 'unittest', 'squirrel-default'],
        line_labels=['Quarry', 'tmin only', 'tmin only', 'original data', 'Squirrel'],
        title='SQLite Paths',
        x_label_text='time/s',
        y_label_text='new paths',
        map_size=2**18,
        ax=fig.add_subplot(3, 4, 8))

    ################
    ##            ##
    ## SQLITE END ##
    ##            ##
    ################



    labels = ['Quarry', 'tmin only', 'tmin + Quarry', 'original data', 'Squirrel']
    plt.subplots_adjust(bottom=0.5)
    fig.legend(labels, loc='lower right', ncol=3, bbox_to_anchor=(1, 0.18))
    plt.tight_layout()
    
    plt.savefig("show.png")

