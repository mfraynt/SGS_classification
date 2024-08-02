import pandas as pd
from datetime import datetime
import requests
import json
import os
from PyPDF2 import PdfReader
from tkinter import filedialog as fd

# Download railway bill list from the API
def get_rwb_list():
    curr_date = datetime.now().strftime("%Y-%m-%d")
    beg_date = datetime(datetime.now().year, 1,1).date().strftime("%Y-%m-%d")
    url = f"http://#######:8080/ords/hr/rest-nds/CHINA_MAILING/{beg_date}/{curr_date}" #the server name should be corrected
    raw = requests.get(url)
    rwb=pd.DataFrame(json.loads(raw.content.decode())['items'])
    rwb.iloc[:,0]=pd.to_datetime(rwb.iloc[:,0])
    return rwb

# Read the first page of the certificate and find the car number 
def get_car_number(file):
    pdf = PdfReader('./certificates/'+file)
    text = pdf.pages[0].extract_text()
    #print(text)
    start = text.find("for inspection:")+15
    end = start + 9
    car_num = text[start:end].split()[0]
    return car_num

# Clean the file name according to OS rules
def sanitize_str(str):
    sanitized=[]
    for ch in str:
        if ch.isalnum():
            sanitized.append(ch)
        else:
            sanitized.append(" ")
    return "".join(sanitized)

if __name__=="__main__":

    rwb = get_rwb_list()

    target_dir = fd.askdirectory(title="Select folder with certificates")

    for main, folders, files in os.walk(target_dir):
        print(files)
    
    for file in files:
        car = get_car_number(file)
        receiver = rwb[rwb["вагон"]==car].sort_values('дата отправления', ascending=False)['получатель'].values[0]
        receiver = sanitize_str(receiver).replace("  ", " ")
        os.rename(os.path.join(target_dir, file), os.path.join(target_dir, "".join([file[:-4]," ",receiver,".pdf"])))
        print(file, receiver)
