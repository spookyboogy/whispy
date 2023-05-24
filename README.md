## Checklist:
<br>
<details>
<summary> feb_07 </summary>

- [x] transcripts
    * [x] en 
    * [x] es
    * used ".m4a" instead of ".wav", might want to retry
- [x] diarization
- [x] merge transcripts with diarization
- [x] handle mixed language (none, 'en' script)
- [x] convert to csv
- [ ] listen/check/correct/finalize

</details>
<details>
<summary> mar_07 </summary>

- [x] transcripts
    * [x] en 
    * [x] es
- [x] diarization
- [x] merge transcripts with diarization
- [x] handle mixed language
- [x] listen/check/finalize
- [x] convert to joined csv

</details>
<details>
<summary> mar_21 </summary>

- [x] transcripts
    * [x] en 
    * [x] es
- [x] diarization
- [x] merge transcripts with diarization
- [x] handle mixed language
- [x] listen/check/finalize
- [x] convert to joined csv

</details>
<details>
<summary> mar_28 </summary>

- [x] transcripts
    * [x] en 
    * [x] es
- [x] diarization
- [x] merge transcripts with diarization
- [x] handle mixed language
- [x] listen/check/finalize

</details>
<details>
<summary> apr_18 </summary>

- [x] Meeting with teachers
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [x] merge transcripts with diarization
    - [x] handle mixed language
    - [x] listen/check/finalize 
    - [x] convert to csv
- [x] Session with kids (con ninos)
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [x] merge transcripts with diarization
    - [x] handle mixed language
    - [x] listen/check/finalize
    - [x] convert to csv

</details>
<details>
<summary> apr_25 </summary>

- [x] transcripts
    * [x] en 
    * [x] es
- [x] diarization
- [x] merge transcripts with diarization
- [x] handle mixed language (next to none, 99% eng)
- [x] listen/check/finalize
- [x] convert to csv, joined

</details>
<details>
<summary> may_02 </summary>

- [x] Part 1
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [x] merge transcripts with diarization
    - [x] handle mixed language
    - [x] listen/check/finalize
    - [x] convert to csv
- [x] Part 2
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [x] merge transcripts with diarization
    - [x] handle mixed language
    - [x] listen/check/finalize
    - [x] convert to csv

</details>

<br>

## Todo:
<details>
<summary>  </summary>

- [x] Join apr_18 session (session with children) pt1 and pt2 (check pt1 again)

- [x] implement diarization from pyannote/speaker-diarization
- [ ] test fine tuning with groundtruth using pytorch-lightning
- [ ] test num_speakers and other diarization hyperparameters
- [ ] test differnt beam_search values for transcriptions

- [x] write method for joining transcripts and diarizations (strip parts from yinrui_rip) 
- [ ] Make a requirements.txt installer 
- [ ] write a pipeline/cli which applies whispy/diarization/merging to an audio file (user-facing)

- [ ] make a good multilingual test .wav file for testing multilingual handling 

- [ ] find fast way to get language verification for audio segments:
        - test whisper transcription by
            - first diarizing the audio
            - loading audio using audio=whisper.load_audio(path)
            - use whisper.pad_or_trim(audio) according to the diarization time segments (joined for efficieny?)
            - per each segment, try transcribing using
                - lang=whisper.detect_language(segment)
                - res = whisper.decode(segment, lang=lang) 

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
- [ ] get a colab (or other) set up to run remotely/on better hardware/multiple at a time
- [ ] make portable installer (including dependencies if possible) and cli (which uses gpu if available)

</details>