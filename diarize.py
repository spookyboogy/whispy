import os
import time
import datetime
import ffmpeg
import torch
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


def convert_to_wav(path_to_audio, wav_path_out):
    """
    pyannote requires .wav input
    """
    # temp_audio = f_name + '--temp' + '.m4a' 
    # ffmpeg.input(path, ss=0, t=30).output(temp_audio, loglevel="quiet").run()
    try:
        input_stream = ffmpeg.input(path_to_audio)
        output_stream = ffmpeg.output(input_stream, wav_path_out, loglevel="quiet")
        ffmpeg.run(output_stream)
        return True
    except:
        print('failed to convert.')
        return False


def handle_audio_formatting(path_to_audio):
    """
    Check if audio is .wav, if not, check if .wav is in same directory,
    if not, convert to wav and return new .wav path.
    """

    if os.path.splitext(path_to_audio)[1] != '.wav':
        print(f'\nConverting {path_to_audio} to .wav\n')
    else:
        return path_to_audio
    
    audio_directory = os.path.sep.join(path_to_audio.split(os.path.sep)[:-1])
    audio_fname = os.path.splitext(path_to_audio.split(os.path.sep)[-1])[0]
    audio_out = audio_fname + '.wav'
    wav_path_out = os.path.join(audio_directory, audio_out)

    if audio_out not in os.listdir(audio_directory):
        success = convert_to_wav(path_to_audio, wav_path_out)
    else:
        print(f'{audio_out} already exists.')
        return wav_path_out

    if success:
        print(f'\nSuccessfully converted audio file : ')
        print('\n\t' + f'{path_to_audio} ---> {wav_path_out}\n')
        return wav_path_out
    else:
        print(f'\nFailed to convert to .wav? u_u\n')
        return None


def main(path, testing=False, write_to_file=True):
    """
    Runs the pyannote/speaker-diarization pipeline 
    """

    print(f'\nfile: {path}\n')
    path = handle_audio_formatting(path)

    print('\nLoading Pipeline...\n')
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@develop",
                                        use_auth_token=use_auth_token)
    print('\nDone loading.')

    # Send the pipeline to torch device to ensure GPU is used, if available
    if torch.cuda.is_available():
        device = torch.device('cuda')
        pipeline = pipeline.to(device)
        print("Devices:")
        for i in range(torch.cuda.device_count()):
            print(f"\t{i} : {torch.cuda.get_device_name(i)}")

    start_time, startstamp = print_timestamp(starting=True, return_time=True)
    # test num_speakers
    diarization = pipeline(path)

    print(f"Diarization: \n{diarization}")
    end_time, endstamp = print_timestamp(return_time=True)
    total_runtime = str(datetime.timedelta(seconds=end_time-start_time)).split('.')[0]
    runtime_stamp = print_runtime(total_runtime, return_stamp=True)
    header = f"Audio File : {os.path.sep.join(path.split(os.path.sep)[-3:])}\
             \nPipeline : pyannote/speaker-diarization\n"
    
    if testing:
        print(f'overlap:{diarization.get_overlap()}')
        _overlap = diarization.get_overlap()
        print(f'timeline:{diarization.get_timeline()}')
        _timeline = diarization.get_timeline()

    f_out = None
    if write_to_file:
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
    return [f_out, diarization]


if __name__ == '__main__':
    
    # Change this path to whatever your test directory path is
    # Will update soon to or make an --audio_path command line arg

    root_folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\tests\\test\\"
    files_in = ["test_0207.wav"]
    
    for f_in in files_in:
        path = os.path.join(root_folder, f_in)
        diarization_file, diarization = main(path)
