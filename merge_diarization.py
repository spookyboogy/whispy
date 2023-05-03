import os
from pyannote.core import Segment, Timeline, Annotation


def transcript_to_segments(transcript_file):
    """
    Reads a transcript file and returns a list of transcript lines
    where the timestamps has been converted into pyannote Segments.
    """

    transcript = []
    with open(transcript_file, 'r') as f:
        for line in f.read().splitlines():
            if ('[' not in line) or ('~' in line) or ('/' in line):
                continue
            transcript += [line]

    for l in range(len(transcript)):
        line = transcript[l]
        i, j = line.index('['), line.index(']')
        # adapt to handle different formats and separators
        times = [t.strip() for t in line[i+1:j].split('->')]
        times = [convert_to_seconds(t) for t in times]
        txt = line[j+1:].strip()
        transcript[l] = (times, txt)
    
    segmented_transcript = []
    for line in transcript:
        start = line[0][0]
        end = line[0][1]
        txt = line[1]
        segmented_transcript += [(Segment(start, end), txt)]
    return segmented_transcript


def convert_to_seconds(timestamp):
    """
    Converts "HH:MM:SS.SS" to seconds, returns float.
    Should expand or improve to handle other formats or broken formats.
    """
    t = [float(i) for i in timestamp.split(':')]
    return t[0]**60 + t[1]*60 + t[2]


def reconstruct_diarization(diarization_file):
    """
    Reads a diarization file and returns a list of (Segment, speaker_id) tuples
    and a reconstruction of the original pyannote Annotation object.

    A more flexible approach would be possible if the 'raw' results of the 
    diarization pipeline were handled immediately after they're generated instead
    of doing it this way, post-diarization, because the pipeline offers additional methods.
    """
    
    diary = []
    with open(diarization_file, 'r') as f:
        for line in f.read().splitlines():
            if ('[' not in line) or ('~' in line) or ('/' in line): 
                continue
            diary += [line]
    speaker_segs = []
    ann = Annotation()
    for line in diary:
        i, j = line.index('['), line.index(']')
        # adapt to handle different formats and separators
        # diarization and whispy default format uses --> instead of ->
        times = [t.strip() for t in line[i+1:j].split('-->')]
        times = [convert_to_seconds(t) for t in times]
        seg = Segment(times[0], times[1])
        speaker = line[j+1:].split()[1].strip()
        speaker_segs += [(seg, speaker)]
        ann[seg] = speaker
    return speaker_segs, ann


def add_speaker_info_to_text(timestamp_texts, ann):
    spk_text = []
    for seg, text in timestamp_texts:
        print()
        s = ann.crop(seg)
        spk = s.argmax()
        print(f'trnscript seg : {seg}\
              \nannotation seg: {s}\
              \nargmax (spkr) : {spk}')
        spk_text.append((seg, spk, text))
    return spk_text


def merge_cache(text_cache):
    sentence = ''.join([item[-1] for item in text_cache])
    spk = text_cache[0][1]
    start = text_cache[0][0].start
    end = text_cache[-1][0].end
    return Segment(start, end), spk, sentence


PUNC_SENT_END = ['.', '?', '!']


def merge_sentence(spk_text):
    merged_spk_text = []
    pre_spk = None
    text_cache = []
    for seg, spk, text in spk_text:
        if spk != pre_spk and pre_spk is not None and len(text_cache) > 0:
            merged_spk_text.append(merge_cache(text_cache))
            text_cache = [(seg, spk, text)]
            pre_spk = spk

        elif text[-1] in PUNC_SENT_END:
            text_cache.append((seg, spk, text))
            merged_spk_text.append(merge_cache(text_cache))
            text_cache = []
            pre_spk = spk
        else:
            text_cache.append((seg, spk, text))
            pre_spk = spk
    if len(text_cache) > 0:
        merged_spk_text.append(merge_cache(text_cache))
    return merged_spk_text


def write_to_txt(spk_sent, file):
    with open(file, 'w') as fp:
        for seg, spk, sentence in spk_sent:
            line = f'{seg.start:.2f} {seg.end:.2f} {spk} {sentence}\n'
            fp.write(line)


if __name__ == "__main__":

    folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\test2\\"
    script = folder + "test2_transcript.txt"
    diary = folder + "test2_diarization.txt"

    segscript = transcript_to_segments(script)
    print('\n'.join(repr(i) for i in segscript))

    spk_segs, annotation = reconstruct_diarization(diary)
    print('\n'.join(repr(i) for i in spk_segs))

    timeline1 = Timeline(i[0] for i in segscript)
    timeline2 = Timeline(i[0] for i in spk_segs)

    tst = add_speaker_info_to_text(segscript, annotation)
    print('\n'.join(repr(i) for i in tst))

    with open(folder + 'res.txt', 'w') as f:
        for seg, spk, txt in tst:
            f.write(f"{str(seg)} [{spk}] {txt}\n")


    # attempt = diarize_text(script, diary)
    # for i in attempt: print(i)

    f_out = folder + "attempt.txt"

