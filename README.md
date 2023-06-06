Whispy consists of three main modules:
- whispy.py : A wrapper for [openAI-whisper](https://openai.com/research/whisper), which transcribes audio
- diarize.py : A wrapper for [Pyannote-audio](https://github.com/pyannote/pyannote-audio#neural-speaker-diarization-with-pyannoteaudio)'s [speaker-diarization model](https://huggingface.co/pyannote/speaker-diarization)
- merge_diarization.py : A handful of scripts and helper functions which stitch the transcript and diarization together to create a [diarized transcript](https://www.rev.com/blog/transcription-blog/what-is-speaker-diarization)

See [/notebooks](https://github.com/spookyboogy/whispy/tree/master/notebooks) for [colab notebook](https://research.google.com/colaboratory/faq.html) recipes and usage examples. 


## Todo:
<details>
<summary>  </summary>

- [ ] replace notebook image resources with links to notebooks/resources 
- [ ] write a single module which applies whispy/diarize/merge to a given audio file (notebooks do this but a module for local use is lacking)
- [ ] solve GPU non-usage problem with the diarization pipeline in colab notebook
- [x] implement diarization from pyannote/speaker-diarization
- [ ] test fine tuning with groundtruth using pytorch-lightning
- [ ] test num_speakers and other diarization hyperparameters
- [ ] test differnt beam_search values for transcriptions
- [x] write method for joining transcripts and diarizations (strip parts from yinrui_rip) 
- [ ] Make a requirements.txt installer 
- [ ] write a pipeline/cli which applies whispy/diarization/merging to an audio file (user-facing)
- [ ] make a good multilingual test .wav file for testing mixed language handling 
- [ ] find fast way to get language verification for audio segments
    - test whisper transcription by
        - first diarizing the audio
        - loading audio using audio=whisper.load_audio(path)
        - use whisper.pad_or_trim(audio) according to the diarization time segments (joined for efficieny?)
        - per each segment, try transcribing using
            - lang=whisper.detect_language(segment)
            - res = whisper.decode(segment, lang=lang) 
<br> </br>
- [ ] write a method which takes a diarized transcript with 
        [t0 -> t1] [speaker] [lang /start] and [t2 -> t3] [speaker] [lang /stop]
        markups which preserves the transcript timeline while substituing the
        marked section with the equivalent section of the diarized transcript in the indicated language (should try to use consistent/matching names or preserve name of primary transcript) 
- [ ] write a similar method for stitching transcripts up with retranscriptions of inaccurate segments
        - appropriately offsets times
        - preserves diarized names (if names)

- [ ] test effect on runtime and quality of using input wav vs m4a vs mp3 (original audio is m4a so converting to wav might waste time/space) 
- [x] revisit and diarize everything with large-v2 and pyannote/speaker-diarization
- [ ] test whisper.cpp
- [x] get a colab (or other) set up to run remotely/on better hardware/multiple at a time
- [ ] make portable installer (including dependencies if possible) and cli (which uses gpu if available)

</details>