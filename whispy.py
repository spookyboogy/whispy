import os
import time
import datetime
import torch
import whisper
import ffmpeg
import librosa
import warnings

def naive_merge(path, en_transcript, es_transcript):
    """ very naive (not used)"""

    merge_limit = min(len(en_transcript), len(es_transcript))
    f_out = os.path.splitext(path)[0] + '--naive-merge.txt'
    with open(f_out, 'w') as f:
        for i in range(merge_limit):
            f.write(f"________\
                    \n{en_transcript[i]}\
                    \n{es_transcript[i]}\n")


def print_timestamp(_lang, starting=False, return_time=False):
    _time = time.strftime("%H:%M:%S")
    start_or_end = ['Finished', 'Starting'][int(starting)]
    s = f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\
          \n {start_or_end} {_lang} transcription...\
          \n Time : {_time}\
          \n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"
    print(s)
    if return_time:
        return s, _time


def detect_lang(path, model=None):
    """
    path -> path to audio file
    model -> loaded whisper model (saves time to not load model twice)
    """
    if not model:
        model = whisper.load_model("medium")

    ## Creating a 30 second temp audio file of the provided audio 
    ## because whisper only uses the first 30 seconds of an audio file
    ## to get an accurately detect the spoken language, making it unneccesary
    ## to load the entire audio file
    ## Update this to skip this step if the audio file is shorter than 1min

    temp_audio = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if librosa.get_duration(path=path) > 60:
            f_name, ext = os.path.splitext(path)
            temp_audio = f_name + '--temp' + '.m4a' 
            ffmpeg.input(path, ss=0, t=30).output(temp_audio, loglevel="quiet").run()

    # Load audio, convert to mel spectrogram, load into model
    if temp_audio:
        audio = whisper.load_audio(temp_audio)
    else:
        audio = whisper.load_audio(path)
    # audio = whisper.load_audio(path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # Use whisper's detect_language function
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)

    print(f"\nDetected language: {lang}")
    if temp_audio:
        os.remove(temp_audio)
    return [lang]


def main(path, langs=['en', 'es'],  model_size="large-v2", print_line_nums=False, encoding='utf-8'):
    """ write me """

    print(f'\nfile: {path}\n')

    fp16 = torch.cuda.is_available()
    print(f"Using CUDA (GPU inference) : {fp16}\n\
          \nLoading model : {model_size}", end = ' ... ')
    model = whisper.load_model(model_size)
    print('Done loading.\n')

    if not langs:
        # no language set, guessing language with whisper
        try:
            print("Transcription language not specified.\
                 \nAttempting to detect language...")
            langs = detect_lang(path, model)
        except Exception as ex:
            print(ex)
            print('\nFailed to detect language. Using English.\n')
            langs = ['en']
     
    header = f"Audio File : {os.path.sep.join(path.split(os.path.sep)[-3:])}\
             \nModel size : {model_size}\n"
    
    transcripts = {lang : [] for lang in langs}
    files_out = {lang : None for lang in langs}

    for lang in langs:
        start_time, _  = print_timestamp(lang, starting=True, return_time=True)
        # best_of=best_of, beam_size=beam_size, temperature=temperature
        options = dict(language=lang, fp16=fp16, verbose=True)
        transcribe_options = dict(task="transcribe", **options)
        # start transcription
        result = model.transcribe(path, **transcribe_options)
        finish_time, _ = print_timestamp(lang, return_time=True)

        f_out = os.path.splitext(path)[0] + f'_{lang}_transcript.txt'
        files_out[lang] = f_out
        with open(f_out, 'w', encoding=encoding) as f:
            f.write(header)
            f.write(start_time)
            for i in result['segments']:
                line = f"{i['id']:4}"
                start = f"{i['start']:7}"
                end = f"{i['end']:7}"
                text = f"{i['text'].strip()}"

                start = str(datetime.timedelta(seconds=float(start))).split('.')[0]
                end = str(datetime.timedelta(seconds=float(end))).split('.')[0]
                
                segment = f"[{start} -> {end}] {text}"
                if print_line_nums:
                    segment = f"{line} " + segment

                transcripts[lang] += [segment]
                f.write(f'{segment}\n')

            f.write(finish_time)
        files_out[lang] = f_out
    
    for lang in langs:
        print(f'{lang} transcript written to:\n\t{files_out[lang]}\n')

    return [files_out, transcripts]


if __name__ == '__main__':
    
    
    folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\tests\\"
    files = ["test\\test_0307.m4a",]
    files = [os.path.join(folder, file) for file in files]
    # langs = ['en']
    # langs = None
    langs = []
   
    for file in files:
        files_out, transcripts = main(file, langs=langs, model_size='small')

# add print statement showing audio length and possibly estimated time to complete
# depending on audio length and hardware 
# 