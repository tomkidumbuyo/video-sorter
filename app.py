
# import required module
import os
import pandas as pd 
import numpy as np
from pymediainfo import MediaInfo
from moviepy.editor import *
import re
import speech_recognition as sr
import multiprocessing.pool as mpool

def get_audio_from_video(location, name):
    base_name = os.path.splitext('audio/' + name)[0]
    file = base_name + '.wav'
    if not os.path.isfile(file):
        video = VideoFileClip(location) 
        audio = video.audio
        audio.write_audiofile(file, codec="pcm_s16le")
    return file

def speech_recognition(audio_file, name):
    print("speech: " + audio_file)
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    text = r.recognize_sphinx(audio)
    with open('transcript/' + name + '.txt', 'w') as f:
        f.write(text)


def file_type(location):
    fileInfo = MediaInfo.parse(location)
    for track in fileInfo.tracks:
        if track.track_type == 'Video':
            return True
    return False

def get_studio_name(location):
    m = ''
    pattern1 = r'\w+\.\d{2}\.\d{2}\.\d{2}'
    pattern2 = r'\[(.*?)\]'
    matches = re.findall(pattern1, location)
    for match in matches:
        m = match[0:-9].lower()

    if m == '':
        matches = re.findall(pattern2, location)
        for match in matches:
            m = match.lower() 
    return m
 
def process_video(location, _file):
    if file_type(location):
        print(location)
        audio = get_audio_from_video(location, _file)
        transcript = speech_recognition(audio, _file)
        fileObject = [_file, location ,get_studio_name(location), audio, transcript]
        filesArray.append(fileObject)

        if [get_studio_name(location)] not in studiosArray:
            studiosArray.append([get_studio_name(location)])


# assign directory
directory = 'G:\del'

filesArray = []
studiosArray = []

pool = mpool.ThreadPool(10)
for root, dirs, files in os.walk(directory):

    for _file in files:
        location = os.path.join(root, _file)
        pool.apply_async(process_video, args=(location, _file,))
    pool.close()    
    pool.join()
    arr = np.asarray(filesArray)
    pd.DataFrame(arr).to_csv('data/files.csv', index_label = "Index", header  = ['name', 'location','studio', 'audio_file', 'transcript'])  

    arr = np.asarray(studiosArray)
    pd.DataFrame(arr).to_csv('data/studios.csv', index_label = "Index", header  = ['name']) 


