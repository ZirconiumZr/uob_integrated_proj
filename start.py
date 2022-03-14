import subprocess
import pandas as pd
import os
import numpy as np
import re

# Run main.py to chunk audio file
# subprocess.run(["python","main.py"])


# Get chunk audio files 
from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(r"H:\UOB\integrate\uob_integrated_proj\stt") if isfile(join(r"H:\UOB\integrate\uob_integrated_proj\stt", f))]
print(onlyfiles)

# STT
output=[]
stt = pd.DataFrame(columns=['index', 'text'])
for i in onlyfiles:
    if ".wav" in i:
        text = subprocess.check_output(["python","ffmpeg.py",i], cwd= "./stt").decode("utf-8") 
        textNew = re.findall('"([^"]*)"', text)
        index = re.findall(r'\d+',i)[-1]
        stt.loc[len(stt)] = [index, textNew[1]]
        # output.append(textNew[1])
# stt = pd.DataFrame(output, columns= ['text'])
print(stt)
sd = pd.read_csv('009NTWY_U3_CL_Shopping_220310-155915.csv')
stt['index'] = stt['index'].astype(int)
# final = pd.merge(sd, stt, left_index=True, right_index=True)
final = pd.merge(sd, stt, on="index")
final.to_csv('output.csv')
