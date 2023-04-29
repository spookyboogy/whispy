import os
import time
import datetime

from pyannote.audio import Pipeline
# from huggingface_hub import login
# login()
use_auth_token="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"


def print_runtime(t, return_stamp=False):
    s = (f"\n~~~~~~~~~~~~~~~~~~~~~~~\
           \n Total runtime: {t}\
           \n~~~~~~~~~~~~~~~~~~~~~~~\n")
    print(s)
    return s

def print_timestamp(starting=False, return_HMS=False, return_time=False, quiet=False):
    """
    Prints current timestamp unless quiet and return values and timestamp (str)
    return_HMS: returns str time in HH:MM:SS format when true
    return_time: returns time.time() for time comparisons
    Returns additional str of formatted timestamp if either return case is true  
    """

    _time = time.strftime("%H:%M:%S")
    start_or_end = ['Finished', 'Starting'][int(starting)]
    s = f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\
          \n {start_or_end} diarization...\
          \n Time : {_time}\
          \n ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    if starting:
        s += '\n'
    else:
        s = '\n' + s
    if not quiet:
        print(s)
    if return_time:
        return time.time(), s
    elif return_HMS:
        return _time, s


def main(path, testing=True):

    print('Loading Pipeline...\n')
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                        use_auth_token=use_auth_token)
    print('\nDone loading.')

    start_time, startstamp = print_timestamp(starting=True, return_time=True)
    # test num_speakers
    diarization = pipeline(path)
    end_time, endstamp = print_timestamp(return_time=True)
    total_runtime = str(datetime.timedelta(seconds=end_time-start_time)).split('.')[0]
    runtime_stamp = print_runtime(total_runtime, return_stamp=True)
    header = f"Audio File : {os.path.sep.join(path.split(os.path.sep)[-3:])}\
             \nPipeline : pyannote/speaker-diarization\n"
    
    print(f'overlap:{diarization.get_overlap()}')
    _overlap = diarization.get_overlap()
    print(f'timeline:{diarization.get_timeline()}')
    _timeline = diarization.get_timeline()

    if testing:
        for i in _overlap:
            print(type(i), i)
        for i in _timeline:
            print(type(i), i)

    f_out = os.path.splitext(path)[0] + '--diarization.txt'
    with open(f_out, 'w') as f:
        f.write(f"{header}\
                  {startstamp}\
                \n{diarization}\
                  {endstamp}\
                  {runtime_stamp}")
        if testing:
            f.write(f"\ntesting...\n\
                    \nOverlap : \n\t{_overlap}\n\
                    \nTimeline: \n\t{_timeline}")  

    print(diarization)
    dr = '\n'.join(i for i in dir(diarization) if not i.startswith('__'))
    print(f'\ndir...\n{dr}')

    discrete = diarization.discretize()
    print(discrete)


if __name__ == '__main__':
    
    # Change this path to whatever your test directory path is
    # Will update soon to or make an --audio_path command line arg
    # and/or check os.getcwd() assuming user is running in /whispy
    # path = "C:\\Users\\mattt\\Desktop\\CS\\test\\"
    # f_in = "test_0207.wav"
    # path = os.path.join(path, f_in)
    # print(f'\nfile: {path}\n')
    # main(path)

    # path = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\apr_18\\"
    # f_in = "april_18_session.wav"
    # path = os.path.join(path, f_in)
    # print(f'\nfile: {path}\n')
    # main(path)

    # path = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\mar_28\\"
    # f_in = "032823_meeting.wav"
    # path = os.path.join(path, f_in)
    # print(f'\nfile: {path}\n')
    # main(path)

    path = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\mar_21\\"
    f_in = "032123_meeting.wav"
    path = os.path.join(path, f_in)
    print(f'\nfile: {path}\n')
    main(path)

    # path = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\mar_07\\"
    # f_in = "030723_meeting.wav"
    # path = os.path.join(path, f_in)
    # print(f'\nfile: {path}\n')
    # main(path)

    # path = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\feb_07\\"
    # f_in = "020723_meeting.wav"
    # path = os.path.join(path, f_in)
    # print(f'\nfile: {path}\n')
    # main(path)
