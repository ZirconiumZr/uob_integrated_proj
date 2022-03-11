# import main
import subprocess
import pandas as pd


# # Run main.py to chunk audio file
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
        output.append(subprocess.check_output(["python","ffmpeg.py",i]))
df = pd.DataFrame({'text':output})
df.to_csv('output.csv')