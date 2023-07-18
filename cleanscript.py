import os
import datetime
import csv
from pyannote.core import Segment

def add_lines(path):
    """ accidentally saved some transcripts without line separation """

    with open(path, 'r') as f:
        script = f.read()
    lines = []
    for i in range(len(script)):
        if script[i] == '[':
            lines += [i-4]
    newscript = []
    for i in range(len(lines)-1):
        newscript += [script[lines[i]:lines[i+1]]]
    # the padding was only 3, so trailing 1's pop up after line 999, fixing that
    for i in range(len(newscript)-1):
        if newscript[i].endswith('1'):
            newscript[i] = newscript[i][:-1]
            newscript[i+1] = '1' + newscript[i+1]
    newfile = os.path.splitext(path)[0] + '--splitlines.txt'
    with open(newfile, 'w') as f:
        for i in newscript:
            f.write(f'{i}\n')


def convert_timestamps(path):
    """Converts transcript timestamps from XXXX.XXs to HH:MM:SS"""

    with open(path, 'r') as f:
        txt = f.read().splitlines()
    newscript=[]
    for line in txt:
        if '[' not in line:
            newscript += [line]
            continue
        i = line.index('[')
        j = line.index(']')
        text = line[j+1:]
        times = [s.strip() for s in line[i+1:j].split('->')]
        start = str(datetime.timedelta(seconds=float(times[0])))
        end = str(datetime.timedelta(seconds=float(times[1])))
        newscript += [f"[{start} -> {end}] {text}"]

    f_out = os.path.splitext(path)[0] + '-converted.txt'
    with open(f_out, 'w') as f:
        for line in newscript:
            f.write(f'{line}\n')
    return newscript


def convert_weirdstamp(path, time_divider='-->'):
    """ 
    why did I timestamp it this way originally... 
    eg: [01:04.000 --> 01:08.000] --> [00:01:04 -> 00:01:08]

    Warning: check time_divider in case your file is using -> or --->. 
             (may eventually fix this so that it checks for the divider being used)
    Warning: will fail after time exceeds 60 minutes, appends 0:MM:SS 
    """

    with open(path, 'r') as f:
        txt = f.read().splitlines()

    newscript=[]
    for line in txt:
        if '[' not in line:
            newscript += [line]
            continue
        print(line)
        i, j = line.index('['), line.index(']')
        text = line[j+1:]
        times = [f"0:{i.strip()[:-4]}" for i in line[i+1:j].split(time_divider)]
        start= times[0]
        end= times[1] 
        newscript += [f"[{start} -> {end}] {text}"]

    f_out = os.path.splitext(path)[0] + '-converted.txt'
    with open(f_out, 'w') as f:
        for line in newscript:
            f.write(f'{line}\n')


def convert_weirderstamp(path, remove_line_nums=True):
    """
    why: timestamp precision is helpful for diarization but not for reading
    eg: [0:01:09.760000 -> 0:01:12.720000] --> [0:01:09 -> 0:01:12]
    """

    with open(path, 'r') as f:
        txt = f.read().splitlines()

    newscript = []
    for line in txt:
        if '[' not in line:
            newscript += [line]
            continue
        print(line)
        i, j = line.index('['), line.index(']')
        text = line[j+1:]
        times=[s.split('.')[0] for s in line[i+1:j].split('->')]
        start, end = times[0], times[1]
        if remove_line_nums:
            newscript += [f"[{start} -> {end}] {text}"]
        else:
            line_num = line[:i]
            newscript += [f"{line_num} [{start} -> {end}] {text}"]

    f_out = os.path.splitext(path)[0] + '--converted.txt'
    with open(f_out, 'w') as f:
        for line in newscript:
            f.write(f'{line}\n')


def fix_offset(path, offset=10):
    """
    specifically made for adjusting timestamps of a transcript 
    where times had reset to 0 after 10 minutes. 
    Uses hard coded dividor, not for general use atm 
    """
    with open(path, 'r') as f:
        txt = f.read().splitlines()

    divide = txt.index("// begining of apr_18_pt2-transcript-converted.txt")
    keeping = txt[:divide]
    lines_to_offset = txt[divide+1:]

    fixes=[*keeping]
    for line in lines_to_offset:
        if '[' not in line:
            fixes += [line]
            continue
        i, j = line.index('['), line.index(']')
        text = line[j+1:]
        times = [s.strip() for s in line[i+1:j].split('->')]
        adjusted_times = [f"{t[:1]}:{str(int(t[2:4])+offset)}:{t[5:]}" for t in times]
        start, end = adjusted_times[0], adjusted_times[1]
        fixes += [f"[{start} -> {end}] {text}"]

    f_out = os.path.splitext(path)[0] + '--fix-offset.txt'
    with open(f_out, 'w') as f:
        for line in fixes:
            f.write(f'{line}\n')


def remove_line_numbers(path):
    """Removes the leading line numbers from a transcript"""

    with open(path, 'r') as f:
        txt = f.read().splitlines()
    newscript=[]
    for line in txt:
        if '[' not in line:
            newscript += [line]
            continue
        newscript += [line[line.index('['):]]
    f_out = os.path.splitext(path)[0] + '--remove-line-nums.txt'
    with open(f_out, 'w') as f:
        for line in newscript:
            f.write(f'{line}\n')



    # name = None
    # line_buffer = []
    # newscript = []
    # for r in range(len(script)):
    #     row = script[r]


def write_csv(rows, precision = 0):
    pass


if __name__ == "__main__":

    pass
    # folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\apr_18\\meeting\\"
    # f_in = folder + "041823_meeting.csv"
    # condense_csv(f_in)


    


