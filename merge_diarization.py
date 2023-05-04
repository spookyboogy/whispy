import os
from pyannote.core import Segment, Timeline, Annotation
import csv


def read_file(transcript_or_diarization_file):
    """
    Reads in a transcript or diarization and returns a list of relevant lines only.
    """
    container = []
    with open(transcript_or_diarization_file, 'r') as f:
        for line in f.read().splitlines():
            # naively assume that anything with '[ ->' is a desired line
            if '[' in line and ('->' in line or '-->' in line):
                container += [line]
            else:
                if line.strip().startswith('Finished'):
                    break
                if ('~' in line) or ('/' in line): 
                    continue
    return container


def transcript_to_segments(transcript_file):
    """
    Reads a transcript file and returns a list of transcript lines
    where the timestamps has been converted into pyannote Segments.
    """

    transcript = read_file(transcript_file)
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
    
    diary = read_file(diarization_file)
    speaker_segs = []
    ann = Annotation()
    for line in diary:
        i, j = line.index('['), line.index(']')
        # adapt to handle different formats and separators
        # diarization and whispy default format uses --> instead of ->
        times = [convert_to_seconds(t.strip()) for t in line[i+1:j].split('-->')]
        seg = Segment(times[0], times[1])
        speaker = line[j+1:].split()[1].strip()
        speaker_segs += [(seg, speaker)]
        ann[seg] = speaker
    return speaker_segs, ann


def add_speaker_info_to_text(timestamp_texts, ann, quiet=True):
    spk_text = []
    for seg, text in timestamp_texts:
        s = ann.crop(seg)
        spk = s.argmax()
        if not quiet:
            print(f'\ntrnscript seg : {seg}\
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



def convert_txt_to_csv(f_in):
    """
    Converts a diarized transcript from .txt to .csv. Input should
    have a timestamp of some format and a name enclosed in '[ ]', else name
    is None. 
    Tested on format: 
        "[ 00:00:06.120 -->  00:00:09.760] [Speaker_00] '...'"
    Currently chopping off decimals of timestamps for readability
    
    for future:
        csv format could allow for inclusion of columns containing the other
        speakers returned by pyannote.core.Annotation.crop(Segment).
        Annotation.crop(Segment).argmax() is currently being used to pick a single speaker,
        but having these columns could make it easier to manually check/edit.
    """

    seps = ['--->','-->','->']
    rows = [('Start', 'End', 'Speaker', 'Text'),]
    with open(f_in, 'r') as f:
        for line in f.read().splitlines():
            row = []
            sep_test = [i in line for i in seps]
            separator = seps[sep_test.index(max(sep_test))] if sum(sep_test) > 0 else None
            if not separator:
                # line isn't a transcript dialogue line 
                if line.strip().startswith('Finished'):
                    break
                continue
            if '[' in line and ']' in line:
                # Assuming times come before (optional) names 
                i, j = line.index('['), line.index(']')
                times = [t.strip() for t in line[i+1:j].split(separator)]
                times = [t.split(':') for t in times]
                # fix this for when dealing with transcripts longer than an hour!
                for t in times:
                    hrs = '0'
                    mins = t[1]
                    secs = t[2].split('.')[0]
                    time = ':'.join([hrs, mins, secs])
                    row += [time]
                line = line[j+1:]
            if '[' in line and ']' in line:
                # Assuming a speaker name is here
                i, j = line.index('['), line.index(']')
                speaker = line[i+1:j]
                row += [speaker]
                line = line[j+1:]
            else:
                row += [None]
            row += [line.strip()]
            rows += [row]
            
    
    f_out = os.path.splitext(f_in)[0] + '.csv'
    with open(f_out, 'w', newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(rows)


if __name__ == "__main__":


    # folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\apr_18\\meeting\\"
    # script = folder + "0418_meeting_fin.txt"
    # diary = folder + "apr_18_meeting--diarization.txt"

    # segscript = transcript_to_segments(script)
    # #print('\n'.join(repr(i) for i in segscript))
    # spk_segs, annotation = reconstruct_diarization(diary)
    # #print('\n'.join(repr(i) for i in spk_segs))
    # merger = add_speaker_info_to_text(segscript, annotation)
    # #print('\n'.join(repr(i) for i in tst))

    # with open(folder + 'merged_diarization.txt', 'w') as f:
    #     for seg, spk, txt in merger:
    #         f.write(f"{str(seg)} [{spk}] {txt}\n")

    folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\apr_18\\meeting\\"
    csv_file = folder + "merged_diarization.txt"
    convert_txt_to_csv(csv_file)