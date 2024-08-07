import os
from pyannote.core import Segment, Timeline, Annotation
import csv
from datetime import timedelta


def read_file(transcript_or_diarization_file, encoding='utf-8'):
    """
    Reads in a transcript or diarization and returns a list of relevant lines only.
    """
    container = []
    with open(transcript_or_diarization_file, 'r', encoding=encoding) as f:
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


def read_csv(csv_file, encoding='utf-8'):
    """
    Takes a csv of a diarized transcript (timestamps and names), and converts
    it such that long comments by a single speaker are condensed into one line.

    nvm just reading it in for now
    """

    script = []
    with open(csv_file, 'r', encoding=encoding) as f:
        f = f.read().splitlines()[1:]
        for row in f:
            start = row[:row.index(',')]
            row = row[row.index(',')+1:]
            end = row[:row.index(',')]
            row = row[row.index(',')+1:]
            name = row[:row.index(',')]
            text = row[row.index(',')+1:]
            script += [[start, end, name, text]]
    return script


def get_transcripts_and_dia_from_directory(path_to_directory):
    """returns -> [[transcripts in directory], diarization]"""

    transcripts = []
    diarization = None
    for f in os.listdir(path_to_directory):
        fname, ext = os.path.splitext(f)
        if ext == '.txt':
            if fname.split('_')[-1] == 'transcript':
                transcripts += [os.path.join(path_to_directory, f)]
            elif fname.split('--')[-1] == 'diarization':
                diarization = os.path.join(path_to_directory, f)
    return transcripts, diarization


def transcript_to_segments(transcript_file, encoding='utf-8'):
    """
    Reads a transcript file and returns a list of transcript lines
    where the timestamps has been converted into pyannote Segments.

    Currently assumes transcript lines in the following format (should be expanded):
    <optional line num> [HH:MM:SS -> HH:MM:SS] <text>
    """

    transcript = read_file(transcript_file, encoding=encoding)
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


### this version was causing an issue with timestamp overflow at the hour mark
# def convert_to_seconds(timestamp):
#     """
#     Converts "HH:MM:SS.SS" to seconds, returns float.
#     Should expand or improve to handle other formats or broken formats.
#     """
#     t = [float(i) for i in timestamp.split(':')]
#     return t[0]**60 + t[1]*60 + t[2]

def convert_to_seconds(timestamp):
    t = [float(i) for i in timestamp.split(':')]
    if len(t) == 2:  # If only minutes and seconds are provided
        return t[0] * 60 + t[1]
    elif len(t) == 3:  # If hours, minutes, and seconds are provided
        return t[0] * 3600 + t[1] * 60 + t[2]
    else:
        raise ValueError(f"Unexpected timestamp format: {timestamp}")


def convert_segment_to_hms(segment):
    """
    takes a pyannote.core.Segment object whose str() format is as follows:
        [ 00:00:02.219 -->  00:00:02.320] to 
    Returns a list of two H:MM:SS formatted strings.
    Another method: use/convert segment.start and segment.end 

    Updated not to return None when segment start == segment end. 
    when start == end , str(segment) returns None
    """
    # print(f'in convert_to_hms : segment = {segment}')
    start = str(segment.start)
    end = str(segment.end)
    if start == end:
        start = str(timedelta(seconds=float(start)))
        end = str(timedelta(seconds=float(end)))
        # print(f'returning {[start, end]}')
        return [start, end]
    else:
        s = str(segment).strip('[').strip(']').split('-->')
        l = [i.split('.')[0].strip() for i in s]
        l = [i[1:] for i in l]
        # print(f'returning {l}')
        return l


def reconstruct_diarization(diarization_file):
    """
    Reads a diarization file and returns a list of (Segment, speaker_id) tuples
    and a reconstruction of the original pyannote Annotation object.

    Example format of a diarization.txt line:
        [ 00:00:02.219 -->  00:00:02.320] A SPEAKER_00 
    
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


def convert_txt_to_csv(f_in, encoding='utf-8'):
    """
    Converts a diarized transcript from .txt to .csv. Input should
    have a timestamp of some format and a name enclosed in '[ ]', else name
    is None. 
    Tested on format: 
        "[ 00:00:06.120 -->  00:00:09.760] [Speaker_00] '...'"
    Currently chopping off decimals of timestamps for readability
    
    encoding='latin-9' or 'ISO-8859-15' for spanish files
    encoding='latin-1' might actually just be best

    for future:
        csv format could allow for inclusion of columns containing the other
        speakers returned by pyannote.core.Annotation.crop(Segment).
        Annotation.crop(Segment).argmax() is currently being used to pick a single speaker,
        but having these columns could make it easier to manually check/edit.

    todo: 
        - reconfigure so that the work is done outside of the open() call to simplify encoding 
    """

    seps = ['--->','-->','->']
    rows = [('Start', 'End', 'Speaker', 'Text'),]
    with open(f_in, 'r', encoding=encoding) as f:
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
    with open(f_out, 'w', encoding=encoding, newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(rows)


def merge_sentences(cache):
    """ 
    cache -> [[Segment(start,end), speaker, text]] 
    Returns the text of all cache items joined into one string.

    Needs to be updated to better handle empty dialogue lines
    """
    # print(cache)
    punct = ['.', '...', '!', '?']
    text = [cache[i][-1].strip() for i in range(len(cache))]
    # print(f'text:{text}')
    if text[0][0] == '"' and text[0][-1] == '"':
        text[0] = text[0][1:-1] 
    res = str(text[0][0].upper() + text[0][1:])
    for i in range(len(text)-1):
        s1, s2 = text[i], text[i+1]
        # print(f's1: {s1}\ns2: {s2}')
        if not s2:
            continue
        if s2[0] == '"' and s2[-1] == '"':
            s2 = s2[1:-1]  
        if s1[-1].islower() and s2[0].islower():
            res += ' ' + s2
            continue
        if s1[-1].islower() and s2[0].isupper() and s1[-1] != 'I':
            # avoiding the worst case where a new line causes
            # a capitalization
            # might want to try comma or period
            res += ' ' + s2[0].lower() + s2[1:]
            continue
        if s1[-1] in punct and s2[0] not in punct:
            # capitalize what we assume is a new sentence
            # unless it's an ellipsis (favors run-ons)
            # caution ¡ and ¿
            if s1[-2:] == '..':
                res += ' ' + s2[0].lower() + s2[1:]
            else:
                res += ' ' + s2[0].upper() + s2[1:]
            continue
        res += ' ' + s2
    return res


def condense_csv_lines(csv_file, f_name=None, encoding='utf-8'):
    """
    Reads a csv file of a diarized transcript and creates a new converted version
    where multiple-line segments with a single given speaker are put on a single line.

    If not reading from file, input may be provided as a list of [seg, spk, txt] lists
    csv_file -> [[Segment(start,end), speaker_id, text], ...]
    In that case, specify the name of the input/ouput file name by setting f_name.
    """

    if type(csv_file) != list:
        # Read in the diarized transcript csv file
        script = read_csv(csv_file, encoding=encoding)
        # Convert the timestamps into seconds and replace them with a single Segment object 
        for i in range(len(script)):
            times = [convert_to_seconds(script[i][0]), convert_to_seconds(script[i][1])]
            time_segment = Segment(times[0], times[1])
            script[i] = [time_segment, script[i][2], script[i][3]]
    else:
        script = csv_file

    # Create container to hold condensed transcript, set loop variables
    condensed, cache, cur_speaker = [], [], None
    i, eof = 0, len(script)
    while i < eof:
        seg, speaker, txt = script[i]
        if speaker and cur_speaker == None:
            cur_speaker = speaker

        if speaker != cur_speaker and cur_speaker != None:
            # new speaker
            # add current cache to condensed container
            _start, _end = cache[0][0].start, cache[-1][0].end
            # merge sentences in cache into single string
            long_line = merge_sentences(cache)
            condensed += [[Segment(_start, _end), cur_speaker, long_line]]
            #refresh cache with new speaker's first line
            cache = [script[i]]
            #change current speaker to new speaker
            cur_speaker = speaker
        elif speaker == cur_speaker:
            # keep adding to cur_speaker's cache
            cache += [script[i]]
        
        if i+1 == eof and cache:
            # flush cache at end of file
            _start, _end = cache[0][0].start, cache[-1][0].end
            long_line = merge_sentences(cache)
            condensed += [[Segment(_start, _end), cur_speaker, long_line]]
        i += 1

    # Create and fill new csv container, convert timestamps back to human readable format
    csv_container = [['Start', 'End', 'Speaker', 'Text']]
    for i in range(len(condensed)):
        line = condensed[i]
        times = [f'{line[0].start:.0f}', f'{line[0].end:.0f}']
        _start = str(timedelta(seconds=int(times[0])))
        _end = str(timedelta(seconds=int(times[1])))
        speaker, text = line[1], line[2]
        csv_container += [[_start, _end, speaker, text]]

    # Write to file
    if f_name:
        # not sure what f_name was usually meant to be used for, but
        # but going with the assumption that f_name specifies base audio file name 
        f_out = os.path.splitext(f_name)[0] + "--joined.csv"
    else:
        f_out = os.path.splitext(csv_file)[0] + "--joined.csv"

    with open(f_out, 'w', encoding=encoding, newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(csv_container)

    return f_out


def diarize_transcript(transcript_file, diarization_file, encoding='utf-8'):
    """
    transcript_file -> txt file of transcript
    diarization_file -> txt file of diarization

    file formats : see transcript_to_segments and reconstruct_diarization

    - Reads a transcript in, converts timestamps to pyannote.core.Segment objects 
    - Reads a diarization in, Reconstructs a pyannote.core.Annotation (diarization) object
        and a simple [(Segment, speaker_id),] container
    - Goes through transcript timeline (intervals set by whisper) and uses the Annotation
        argmax method to get the highest likelihood speaker for the given cropped segment,
        building a diarized transcript along the way
    - Writes to file "yourfile--merged.txt"
    - Converts and writes to csv "yourfile--merged.csv" 
    - Writes condensed dialogue version of script to csv "yourfile--joined.csv"

    Reconfigure this such that it can take a raw transcription result (precise timestamps)
    as well as the raw diarization (annotation), for use in the whole whisper + speaker
    diarization pipeline.
    """

    # Bulk of work done here
    segscript = transcript_to_segments(transcript_file, encoding=encoding)
    spk_segs, annotation = reconstruct_diarization(diarization_file)
    merger = add_speaker_info_to_text(segscript, annotation)
    # for i in segscript: 
    #     print(i) 
    # print(type(segscript))
    # print(type(merger))
    # for i in merger: 
    #     print(i) 

    # The rest is formatting and file io
    formatted_merger = []
    for seg, spk, txt in merger:
        times = convert_segment_to_hms(seg)
        # if seg == [] or spk == None:
        #     print(f'seg, spk, txt : {seg}, {spk}, {txt}')
        #     print(f'times : {times}')
        formatted_merger += [[times[0], times[1], spk, txt]]
    # Write to txt and csv
    f_name = os.path.splitext(transcript_file)[0]
    txt_out = f_name + "--merged.txt"
    with open(txt_out, 'w', encoding=encoding) as f:
        # todo: write header
        for t0, t1, spk, txt in formatted_merger:
            f.write(f'[{t0} -> {t1}] [{spk}] {txt}\n')
    # These should be wrapped into their own functions bc it reoccurs in other functions, 
    # But format checking and standard formatting haven't been fully implemented
    csv_out = f_name + "--merged.csv"
    csv_header = ['Start', 'End', 'Speaker', 'Text']
    with open(csv_out, 'w', encoding=encoding, newline='') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(csv_header)
        csvwriter.writerows(formatted_merger)

    # Write an additional csv with joined (condensed) dialogue lines
    csv_f_out = condense_csv_lines(merger, f_name=f_name, encoding=encoding)

    files_out = [txt_out, csv_out, csv_f_out]
    return files_out


def merge_and_join_batch(encoding):
    """Just a script for applying diarize_transcript to a batch of local files."""

    root_folder = "C:\\Users\\mattt\\Desktop\\New_Audios\\"
    subfolders = ['012423', '022823', '050523_whatsapp', '102522',
                  '110122', '111522', '112222', '120622\\b', '120622\\a', '121322']
    folders = [os.path.join(root_folder, subfolder) for subfolder in subfolders]
    files_out = {folder : [] for folder in folders}

    for folder in files_out:
        transcript_files, diarization_file = get_transcripts_and_dia_from_directory(folder)
        if not (transcript_files and diarization_file):
            print(f'{folder} is missing files\n')
            if transcript_files:
                files_out[folder] = [transcript_files, 'missing diarization']
            else:
                files_out[folder] = ['missing transcripts', diarization_file]
            continue

        files_out[folder] = [transcript_files, diarization_file]
        for transcript in transcript_files:
            diarized_transcript_files = diarize_transcript(transcript, 
                                                        diarization_file, 
                                                        encoding=encoding)
            files_out[folder] += [diarized_transcript_files]
    
    print('\nAll results:')
    for f in files_out:
        print(f'\n____________\n{f}\n')
        if len(files_out[f]) > 2:
            for lang in range(len(files_out[f][2:])):
                print('\n'.join(files_out[f][2 + lang]) + '\n')
            continue
        if type(files_out[f][0]) != list:
            print(files_out[f][0])
        else:
            print('\n'.join(files_out[f][0]))
        print(files_out[f][1])
    print()


if __name__ == "__main__":

    # #  latin-1 encoding seems to accomodate both en and es transcripts well
    encoding = "utf-8"

    # folder = "C:\\Users\\mattt\\Desktop\\CS\\whispy\\test_11\\"
    # transcript_files = ["test_022823_es_transcript.txt",]
    #                     #"032123_meeting_es_transcript.txt",]
    #                     #"032123_meeting_fin.txt"]
    # transcript_files = [folder + f for f in transcript_files]
    # diarization_file = folder + "test_022823--diarization.txt"

    # for transcript in transcript_files:
    #     diarized_transcript_files = diarize_transcript(transcript, 
    #                                                    diarization_file, 
    #                                                    encoding=encoding)
    #     #diarize_transcript(transcript, diarization_file, encoding=encoding)

    folder = "/home/spooky/CS/whispy/tests/testing_here_2"
    transcript_files = ["/GMT20240613-170728_Recording_en_transcript.txt",]
    transcript_files = [folder + f for f in transcript_files]
    diarization_file = folder + "/GMT20240613-170728_Recording--diarization.txt"

    for transcript in transcript_files:
        diarized_transcript_files = diarize_transcript(transcript, 
                                                       diarization_file, 
                                                       encoding=encoding)
    #diarize_transcript(transcript, diarization_file, encoding=encoding)

    # merge_and_join_batch(encoding)

