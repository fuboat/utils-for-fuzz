from os import path
import os
import sys
from turtle import left
from matplotlib import pyplot as plt
from examples.llvmCoverage import *
from utils.utils import *
import numpy
import pickle
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import LogLocator, NullFormatter

graph_configs = [
    {
        "dbname": "sqlite",
        "dbname_label": r'$\bf{(a)}$' + " SQLite",
        "fix_index": 10,
        "tool_names": [
            ('squirrel', 'r', '--', 'SQUIRREL'),
            ('sqlancer', 'g', '-.', 'SQLancer'),
            ('sqlmix',   'b', ':', 'GRIFFIN'),
            ('sqlsmith', 'purple', '-', 'SQLsmith')
        ]
    },

    {
        'dbname': 'duckdb',
        "dbname_label": r'$\bf{(b)}$' + " DuckDB",
        'fix_index': 266,
        'tool_names': [
            ('sqlancer', 'g', '-.', 'SQLancer'),
            ('sqlmix',   'b', ':', 'GRIFFIN'),
            ('sqlsmith', 'purple', '-', 'SQLsmith')
        ]
    },

    {
        "dbname":    "mariadb",
        "dbname_label": r'$\bf{(c)}$' + " MariaDB",
        "fix_index": 10,
        "tool_names": [
            ('squirrel', 'r', '--', 'SQUIRREL'),
            ('sqlancer', 'g', '-.', 'SQLancer'),
            ('sqlmix',   'b', ':', 'GRIFFIN'),
        ]
    },

    {
        'dbname': 'postgres',
        'dbname_label': r'$\bf{(d)}$' + ' PostgreSQL',
        'fix_index': 15,
        'tool_names': [
            ('sqlsmith', 'purple', '-', 'SQLsmith'),
            ('sqlancer', 'g', '-.', 'SQLancer'),
            ('sqlmix',   'b', ':', 'GRIFFIN'),
            ('squirrel', 'r', '--', 'SQUIRREL'),
        ]
    },
]

if __name__ == '__main__':

    x_shrink = 1
    y_shrink = 1

    def formatnum(x, pos):
        return '$%.0f$k' % (x/1000)

    width = 2
    height = 2

    ii = 0

    # fig: Figure = plt.figure(figsize=(5,4.5), constrained_layout=True)
    fig: Figure = plt.figure(figsize=(6.4,5.76), constrained_layout=True)

    for graph_config in graph_configs:

        ii += 1

        ax: Axes = fig.add_subplot(width, height, ii)
        ax.set_xscale('log')

        tool_names = graph_config['tool_names']
        fix_index = graph_config['fix_index']
        dbname = graph_config['dbname']
        dbname_label = graph_config['dbname_label']

        for (tool_name, c, ls, label_name) in tool_names:
            
            pickle_filename = "./data/%s_%s.llvm.log.pickle" % (tool_name, dbname)
            if os.path.exists(pickle_filename):
                with open(pickle_filename, "rb") as infile:
                    p = pickle.load(infile)
            else:
                # start calculation
                p = PointConvertForFillBetweenV2()
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
                # till here, p finished all calculation.

            os.makedirs("./data", exist_ok=True)

            with open(pickle_filename, "wb") as outfile:
                pickle.dump(p, outfile)

            ax.plot((numpy.array(p.x) - fix_index) / x_shrink, numpy.array(p.y_median) / y_shrink, label=label_name, ls=ls, c=c, rasterized=True)
            # ax.plot(list(numpy.array(p.x) - fix_index), p.y_avg, label=label_name, ls=ls, c=c)
            ax.fill_between((numpy.array(p.x) - fix_index) / x_shrink, numpy.array(p.y_99confidence_interval_min) /
                            y_shrink, numpy.array(p.y_99confidence_interval_max) / y_shrink, alpha=0.2, facecolor=c, rasterized=True)
            ax.set_xlim(left=1 / x_shrink, right=43200 / x_shrink)
            ax.set_xlabel(dbname_label)

            formatter = FuncFormatter(formatnum)
            ax.yaxis.set_major_formatter(formatter)

            index_12h = bisect_left(p.x, 43200 + fix_index, lo=0, hi=len(p.x))
            print(tool_name, dbname, [y_format[min(index_12h, len(y_format) - 1)] for y_format in p.ys_format])

            # start, end = ax.get_xlim()
            # ax.xaxis.set_ticks([1, 10, 100, 1000, 10000])
            # logmaj = LogLocator(base=10.0)
            # ax.xaxis.set_major_locator(logmaj)
            ax.xaxis.get_ticklocs(minor=True)
            ax.minorticks_on()
            # ax.tick_params(axis='x', which='minor', bottom=True)
            ax.tick_params(axis='y', which='minor', left=False)
            # ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.1,0.2,0.4,0.6,0.8,1,2,4,6,8,10]))
            # ax.xaxis.set_minor_formatter(NullFormatter())

    handles, labels = ax.get_legend_handles_labels()
    # fig.legend(labels, loc='lower center', ncol=2, borderaxespad=-0.5)
    leg = fig.legend(labels, loc='upper center', fancybox=True, ncol=4, bbox_transform=fig.transFigure, bbox_to_anchor=(0.5,-0))
    leg.get_frame().set_edgecolor('black')
    leg.get_frame().set_linewidth(0.25)
    # fig.legend().get_frame().set_edgecolor('b')
    # fig.legend(labels, loc='upper right')
    # fig.supxlabel("Time(s)")
    fig.supylabel('Number of Branches')
    fig.savefig("show.pdf", bbox_inches='tight', dpi=400)
    fig.savefig("show.png")
