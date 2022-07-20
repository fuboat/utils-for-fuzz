from typing import List, Tuple
import time
import datetime

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

def date_to_timestamp_YYYYMMDDhhmmss(date_str: str) -> float:
    date_timestamp = time.mktime(datetime.datetime.strptime(date_str[0:8], "%Y%m%d").timetuple())
    
    hours = int(date_str[8:10])
    minutes = int(date_str[10:12])
    seconds = int(date_str[12:14])

    return date_timestamp + hours * 3600 + minutes * 60 + seconds

def coverage_log_content_to_x_time_y_branch_data(content: str) -> Tuple[List, List]:

    x = []
    y = []

    lines = content.splitlines()

    if len(lines) == 0:
        return ([], [])
    
    timestamp_start = None
    branch_count_hit_last = 0

    for line in lines:
        attrs = line.split()
        
        if len(attrs) != 14:
            continue

        date_YYYYMMDDhhmmss: str = attrs[0]
        timestamp = date_to_timestamp_YYYYMMDDhhmmss(date_YYYYMMDDhhmmss)

        if timestamp_start is None:
            timestamp_start = timestamp

        time_delta_second: float = timestamp - timestamp_start
        branch_count_total: int = int(attrs[11])
        branch_count_missing: int = int(attrs[12])
        branch_count_hit: int = branch_count_total - branch_count_missing
        branch_count_hit_last = max(branch_count_hit_last, branch_count_hit)

        x.append(time_delta_second)
        y.append(branch_count_hit_last)

    return (x, y)

def coverage_log_file_to_x_time_y_branch_data(file_name_path: str) -> Tuple[List, List]:
    
    with open(file_name_path, 'r') as f:
        return coverage_log_content_to_x_time_y_branch_data(f.read())

if __name__ == '__main__':
    (x, y) = coverage_log_file_to_x_time_y_branch_data('log')
    
    fig: Figure = plt.figure(figsize=(9,7))
    ax: Axes = fig.add_subplot(1, 1, 1)
    ax.set_xscale('log')

    ax.plot(x, y)
    plt.savefig("show.png")