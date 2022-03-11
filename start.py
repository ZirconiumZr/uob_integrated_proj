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
for i in onlyfiles:
    if ".wav" in i:
        text = subprocess.check_output(["python","ffmpeg.py",i], cwd= "./stt").decode("utf-8") 
        textNew = re.findall('"([^"]*)"', text)
        output.append(textNew[1])
stt = pd.DataFrame({'text':output})
sd = pd.read_csv('009NTWY_U3_CL_Shopping_220310-155915.csv')
final = pd.merge(sd, stt, left_index=True, right_index=True)
final.to_csv('output.csv')
