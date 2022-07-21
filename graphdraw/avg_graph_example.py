from matplotlib import pyplot as plt
from examples.llvmCoverage import *
from utils.utils import *

if __name__ == '__main__':

    fig: Figure = plt.figure(figsize=(9,7))
    ax: Axes = fig.add_subplot(1, 1, 1)
    ax.set_xscale('log')

    tool_names = [('squirrel', 'r', '--', 'SQUIRREL'), 
                  ('sqlancer', 'g', '-.', 'SQLancer'), 
                  ('sqlmix',   'b', ':', 'GRIFFIN')]

    for (tool_name, c, ls, label_name) in tool_names:

        p = PointConvertForFillBetween()

        # squirrel

        for i in range(1, 6):
            (x, y) = coverage_log_file_to_x_time_y_branch_data('data/%s/log%s' % (tool_name, i))

            if len(x) == 0:
                continue

            p.add_plot(x, y)

        ax.plot(p.x, p.y_avg, label=label_name, ls=ls, c=c)
        ax.fill_between(p.x, p.y_min, p.y_max, alpha=0.2, facecolor=c)
        ax.set_xlim(left=50, right=86400)
    
    fig.legend()

    fig.savefig("show.pdf", bbox_inches='tight')
    fig.savefig("show.png")