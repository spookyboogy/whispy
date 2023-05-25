import whisper
import os
import time
import datetime


def naive_merge(path, en_transcript, es_transcript):
    """ very naive """

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


def log_mel(path):
    """copypasta from whisper readme, not implemented or working atm"""
    model = whisper.load_model("large-v2")
    audio = whisper.load_audio(path)
    audio = whisper.pad_or_trim(audio)

    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    print(f"\nDetected language: {lang}")

    options = whisper.DecodingOptions(fp16=False, language=lang)
    print(f'\noptions = {options}\n')
    result = whisper.decode(model, mel, options)

    res = result.text
    print(f'res = \n{res}\n')

    f_out = path + '_transcript.txt'
    with open(f_out, 'w') as f:
        f.write(res)
    return res


def main(path, langs=['en', 'es'],  model_size="large-v2", print_line_nums=False, fp16=False):
    """ write me """

    print(f'\nfile: {path}\n')
    print(f'Loading model : {model_size}', end=' ... ')
    model = whisper.load_model(model_size)
    print('Done loading.\n')

    header = f"Audio File : {os.path.sep.join(path.split(os.path.sep)[-3:])}\
             \nModel size : {model_size}\n" #if model_size!="large-v2" else None
    
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
        with open(f_out, 'w') as f:
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

                print(f'segment = {segment}')
                transcripts[lang] += [segment]
                f.write(f'{segment}\n')

            f.write(finish_time)
        files_out[lang] = f_out
    
    for lang in langs:
        print(f'\n{lang} transcript written to:\n\t{files_out[lang]}\n')

    return [files_out, transcripts]


if __name__ == '__main__':
    
    folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\"
    # files = ["test\\test_0207.wav",]
    # m4a takes less time to load bc lower quality
    files = ["test\\test_0207.m4a",]
    files = [os.path.join(folder, file) for file in files]
    langs = ['en']
   
    for file in files:
        files_out, transcripts = main(file, langs=langs)

        




    