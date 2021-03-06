# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
''' Logging
Version     Date    Change_by   Description
#00     2022-Feb-28     Zhao Tongtong   Initial version  


'''
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


import os
from datetime import datetime
import pandas as pd

# import filetype # to check file type

import malaya_speech
from pyannote.audio import Pipeline as pa_Pipeline
from pydub import AudioSegment


import uob_audiosegmentation, uob_noisereduce, uob_speakerdiarization, uob_mainprocess


# TODO: get uploaded file name from Front-End




#### TODO: Convert to .wav / Resampling
#### * Check if an Audio file
# kind = filetype.guess('Bdb001_interaction_first60s.wav')
# if kind is None:
#     print('Cannot guess file type!')

# print('File extension: %s' % kind.extension)
# print('File MIME type: %s' % kind.mime)


#### * Convert to .wav
# audioname1='speech.mp3'
# audiopath_from1='uob/from'
# audiopath_to1='uob/to'
# audiofile1 = os.path.join(audiopath_from1,audioname1)
# AudioSegment.from_file(audiofile1).export(os.path.join(audiopath_to1,audioname1),format='wav')  # TODO: param setup - codec 



#### * Declare variables
AUDIO_NAME = 'Bdb001_interaction_first60s.wav' #'Bdb001_interaction_first60s.wav' #'The-Singaporean-White-Boy.wav'
AUDIO_PATH = './wav/'
AUDIO_FILE = os.path.join(AUDIO_PATH,AUDIO_NAME)
SAMPLE_RATE = 44100
num_audio_files = 1

starttime = datetime.now()




#### * Load audio file
y, sr = malaya_speech.load(AUDIO_FILE, SAMPLE_RATE)
audio_duration = len(y) / sr
print('*' * 30)
print('length:',len(y), 'sample rate:', sr, 'duration(s):',audio_duration)
print('*' * 30)



#### * Load models
## Noise reduce models
# nr_model = uob_noisereduce.load_noisereduce_model(quantized=False)
nr_model = uob_noisereduce.load_noisereduce_model_local(quantized=False)
## Load malaya vad model
# vad_model_vggvox2 = uob_speakerdiarization.load_vad_model(quantized=False)
vad_model_vggvox2 = uob_speakerdiarization.load_vad_model_local(quantized=False)
## Load malaya speaker vector model 
# sv_model_speakernet, sv_model_vggvox2 = uob_speakerdiarization.load_speaker_vector_model(quantized=False)
sv_model_speakernet, sv_model_vggvox2 = uob_speakerdiarization.load_speaker_vector_model_local(quantized=False)
## Load pyannote.audio pipeline for sd
pa_pipeline = None
pa_pipeline = pa_Pipeline.from_pretrained('pyannote/speaker-diarization')  # TODO: uncomment for Pyannote.audio model. !!specturalcluster package needs to be updated.
print('Pretrained Models Loading Done!!!')
print('*' * 30)


#### * Segmentation
chunksfolder = ''
if audio_duration > 300:  # segment if longer than 5 min=300s
    totalchunks, nowtime = uob_audiosegmentation.audio_segmentation(name=AUDIO_NAME,file=AUDIO_FILE)
    print('  Segmentation Done!!!\n','*' * 30)
    chunksfolder = 'chunks_'+AUDIO_NAME[:5]+'_'+nowtime  #'./chunks'+nowtime 
    chunksfolder = os.path.join(AUDIO_PATH, chunksfolder)
    print('chunksfolder: ', chunksfolder)
    # num_audio_files = len([n for n in os.listdir(chunksfolder+"/") if n.endswith(".wav")])
    num_audio_files = totalchunks

    
print('Number of audio files to process: ', num_audio_files)
print('*' * 30)


#### * Process
# chunksfolder = 'chunks_The-S_20220228_162841'   # * for test
tem_sd_result = []
if chunksfolder != '':
    for filename in os.listdir(chunksfolder+"/"):
        if filename.endswith(".wav"): 
            # print(os.path.join(chunksfolder, filename))
            ### * Load chunk file
            file = os.path.join(chunksfolder, filename)
            y, sr = malaya_speech.load(file, SAMPLE_RATE)
                       
            ### * Process: reduce noise + vad + scd + ovl + sd
            sd_result = uob_mainprocess.sd_process(y, sr, 
                                                audioname=filename,
                                                audiopath=chunksfolder,
                                                audiofile=file,
                                                nr_model=nr_model,   # ?: [nr_model, nr_quantized_model]
                                                vad_model=vad_model_vggvox2,
                                                sv_model=sv_model_speakernet,    # ?: sv_model_speakernet, sv_model_vggvox2
                                                pipeline=pa_pipeline,
                                                chunks=True,
                                                reducenoise=False,
                                                sd_proc='malaya')  # ?: [pyannoteaudio, malaya]
            tem_sd_result.append(sd_result[1:])
            
            # TODO: ....................... STT .........................
            
            # TODO: .......concatenation if breakdown into chunks........
    


else:
    ### * Load single file
    y, sr = malaya_speech.load(AUDIO_FILE, SAMPLE_RATE)

    ### * Process: reduce noise + vad + scd + ovl + sd
    sd_result = uob_mainprocess.sd_process(y, sr, 
                                        audioname=AUDIO_NAME,
                                        audiopath=AUDIO_PATH,
                                        audiofile=AUDIO_FILE,
                                        nr_model=nr_model,   # ?: [nr_model, nr_quantized_model]
                                        vad_model=vad_model_vggvox2,
                                        sv_model=sv_model_speakernet,    # ?: sv_model_speakernet, sv_model_vggvox2
                                        pipeline=pa_pipeline,
                                        chunks=False,
                                        reducenoise=False, 
                                        sd_proc='malaya')  # ?: [pyannoteaudio, malaya]
    tem_sd_result.append(sd_result[1:])


final_sd_result = pd.DataFrame(tem_sd_result.reverse(), columns=['index','starttime','endtime','duration','speaker_label'])
### * Cut audio by SD result
# namef, namec = os.path.splitext(AUDIO_NAME)
slices_path = './stt'
# slices_path = os.path.join(AUDIO_PATH, namef, 'slices').replace('\\','/')
if not os.path.exists(slices_path):
    os.mkdir(slices_path)
uob_mainprocess.cut_audio_by_timestamps(start_end_list=sd_result, audioname=AUDIO_NAME, audiofile=AUDIO_FILE, part_path=slices_path)
print('*'*30, 'Cut')

# ....................... STT .........................
# Get chunk audio files 
from os import listdir
from os.path import isfile, join
import numpy as np
onlyfiles = [f for f in listdir(r"E:\EBAC\Internship\UOB\Projects\UOB_Call_Center_SD\uob_integrated_proj-main_ZR\stt") if isfile(join(r"E:\EBAC\Internship\UOB\Projects\UOB_Call_Center_SD\uob_integrated_proj-main_ZR\stt", f))]
print(onlyfiles)

# STT
import subprocess
import re
output=[]
stt = pd.DataFrame(columns=['index', 'text'])
for i in onlyfiles:
    if ".wav" in i:
        text = subprocess.check_output(["python","ffmpeg.py",i], cwd= "./stt").decode("utf-8") 
        textNew = re.findall('"([^"]*)"', text)
        index = re.findall(r'\d+',i)[-1]
        stt.loc[len(stt)] = [index, textNew[1]]
sd = pd.read_csv('009NTWY_U3_CL_Shopping_220310-155915.csv')
stt['index'] = stt['index'].astype(int)
final = pd.merge(sd, stt, on="index")
final.to_csv('output.csv')


endtime = datetime.now()

print('*' * 30,'\n  Finished!!',)
print('start from:', starttime) 
print('end at:', endtime) 
print('duration: ', endtime-starttime)


