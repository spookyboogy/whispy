#####################################################################################
#####################################################################################
#####################################################################################
####### Not using this at the moment, should look into it now that GPU runtimes #####
####### are possibe. Not sure                                                   #####
#####################################################################################
#####################################################################################
#####################################################################################


from faster_whisper import WhisperModel
import torch
# from pathlib import Path
import datetime
import time
import os 

use_auth_token="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"
from huggingface_hub import login
login()

# import pandas as pd
# import numpy as np
# from sklearn.cluster import AgglomerativeClustering
# from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
# from pyannote.audio import Audio
# from pyannote.core import Segment
# from transformers import pipeline
# import wave

def main():

    model = WhisperModel(model_size, device=device)
    options = dict(language=None, beam_size=5, best_of=5)
    transcribe_options = dict(task="transcribe", **options)

    result, info = model.transcribe(path, **transcribe_options)
    #result = list(result)
    print(f"\nDetected language {info.language} with probability {info.language_probability:.2f}\n")

    transcript = []
    i = 0
    for seg in result:
        start = seg.start
        end = seg.end
        text = seg.text
        segment = f"{i:4} [{start:7.2f} -> {end:7.2f}] {text}"
        print(segment)
        transcript += [segment]
        i += 1

    f_out = os.path.splitext(path) + '_auto_transcript.txt'
    with open(f_out, 'w') as f:
        for i in transcript:
            f.write(f'{i}\n')

    end_time = time.time()
    print(f'\nend time : {end_time}\n')
    print(info)
    total_time = end_time - start_time
    print(f'\nTotal runtime: {total_time}s\n')



if __name__ == '__main__':
    
    langs = ['en', 'es']

    path = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\apr_18\\meeting"
    f_in = "apr_18_meeting.wav"
    path = os.path.join(path, f_in)

    model_size = "large-v2"
    device = 0 if torch.cuda.is_available() else "cpu"

    print(f'\nfile: {path}\n')
    start_time = time.time()
    print(f'start time : {start_time}\n')

    main()


# stealing from https://github.com/yinruiqing/pyannote-whisper/

# from pyannote.audio import Pipeline
  
# pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

# # inference on the whole file
# pipeline("file.wav")

# # inference on an excerpt
# from pyannote.core import Segment
# excerpt = Segment(start=2.0, end=5.0)

# from pyannote.audio import Audio
# waveform, sample_rate = Audio().crop("file.wav", excerpt)
# pipeline({"waveform": waveform, "sample_rate": sample_rate})