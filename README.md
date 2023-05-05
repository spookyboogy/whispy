Checklist:
- [ ] feb_07 
    - [x] transcripts
        * [x] en 
        * [x] es
        * used ".m4a" instead of ".wav", might want to retry
    - [x] diarization
    - [x] merge transcripts with diarization
    - [x] handle mixed language (none, 'en' script)
    - [x] convert to csv
    - [ ] listen/check/correct/finalize
- [ ] mar_07 
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [ ] merge transcripts with diarization
    - [ ] handle mixed language
    - [ ] listen/check/finalize
- [ ] mar_21 
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [ ] merge transcripts with diarization
    - [ ] handle mixed language
    - [ ] listen/check/finalize
- [ ] mar_28 
    - [x] transcripts
        * [x] en 
        * [x] es
    - [x] diarization
    - [ ] merge transcripts with diarization
    - [ ] handle mixed language
    - [ ] listen/check/finalize
- [ ] apr_18 
    - [ ] Meeting with teachers
        - [x] transcripts
            * [x] en 
            * [x] es
        - [x] diarization
        - [x] merge transcripts with diarization
        - [x] handle mixed language
        - [x] listen/check/finalize 
            * not technically 100% human check but >75% checked
        - [x] convert to csv
    - [ ] Session with kids (con ninos)
        - [x] transcripts
            * [x] en 
            * [x] es
        - [x] diarization
        - [ ] merge transcripts with diarization
        - [ ] handle mixed language
        - [ ] listen/check/finalize


Todo: 
- [x] Join apr_18 session (session with children) pt1 and pt2 (check pt1 again)

- [x] implement diarization from pyannote/speaker-diarization
- [ ] test fine tuning with groundtruth using pytorch-lightning
- [ ] test num_speakers and other diarization hyperparameters
- [ ] test differnt beam_search values for transcriptions

- [ ] write method for joining transcripts and diarizations (strip parts from yinrui_rip) 

- [ ] test translation task for dealing with mixed language
- [ ] find fast way to get language verification for audio segments

- [ ] test effect on runtime and quality of using input wav vs m4a vs mp3 (original audio is m4a) 
- [x] revisit and diarize everything with large-v2 and pyannote/speaker-diarization
- [ ] test whisper.cpp
- [ ] get a colab (or other) set up to run remotely/on better hardware/multiple at a time
- [ ] make portable installer (including dependencies if possible) and cli (which uses gpu if available)