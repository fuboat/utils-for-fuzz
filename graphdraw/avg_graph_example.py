from os import path
from matplotlib import pyplot as plt
from examples.llvmCoverage import *
from utils.utils import *
import numpy

# dbname = 'mariadb'
# fix_index = 10
# tool_names = [
#     ('squirrel', 'r', '--', 'SQUIRREL'),
#     ('sqlancer', 'g', '-.', 'SQLancer'),
#     ('sqlmix',   'b', ':', 'GRIFFIN'),
#     # ('sqlsmith', 'purple', '-', 'SQLsmith')
# ]

# dbname = 'sqlite'
# fix_index = 10
# tool_names = [
#     ('squirrel', 'r', '--', 'SQUIRREL'),
#     ('sqlancer', 'g', '-.', 'SQLancer'),
#     ('sqlmix',   'b', ':', 'GRIFFIN'),
#     ('sqlsmith', 'purple', '-', 'SQLsmith')
# ]

# dbname = 'postgres'
# fix_index = 12
# tool_names = [
#     ('squirrel', 'r', '--', 'SQUIRREL'),
#     ('sqlancer', 'g', '-.', 'SQLancer'),
#     ('sqlmix',   'b', ':', 'GRIFFIN'),
#     ('sqlsmith', 'purple', '-', 'SQLsmith')
# ]

dbname = 'duckdb'
fix_index = 266
tool_names = [
    # ('squirrel', 'r', '--', 'SQUIRREL'),
    ('sqlancer', 'g', '-.', 'SQLancer'),
    ('sqlmix',   'b', ':', 'GRIFFIN'),
    ('sqlsmith', 'purple', '-', 'SQLsmith')
]

if __name__ == '__main__':

    fig: Figure = plt.figure(figsize=(4,4))
    ax: Axes = fig.add_subplot(1, 1, 1)
    ax.set_xscale('log')

    for (tool_name, c, ls, label_name) in tool_names:

        p = PointConvertForFillBetweenV2()

        # squirrel

        for i in range(1, 6):

            file_name = '/root/jingzhou_workspace/exp-data/Griffin-ASE2022/unformat/%s_%s-%s.llvm.log' % (tool_name, dbname, i)

            if not path.isfile(file_name):
                print("file not found: %s" % file_name)
                continue

            (x, y) = coverage_log_file_to_x_time_y_branch_data(file_name)

            if len(x) == 0:
                continue

            p.add_plot(x, y)

        p.format_data()
        ax.plot(list(numpy.array(p.x) - fix_index), p.y_median, label=label_name, ls=ls, c=c)
        ax.fill_between(list(numpy.array(p.x) - fix_index), p.y_95confidence_interval_min, p.y_95confidence_interval_max, alpha=0.2, facecolor=c)
        ax.set_xlim(left=1, right=43200)
    
    fig.legend()

    fig.savefig("show-%s.pdf" % dbname, bbox_inches='tight')
    fig.savefig("show-%s.png" % dbname)
