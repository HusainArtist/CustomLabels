import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import cv2
import os
import math 
import boto3
from io import BytesIO
import datetime
from datetime import datetime
import shutil
    
import urllib.request

import pytz

def show_custom_labels(model,bucket,photo, min_confidence):
    print ("Hello")

def get_frames(corresponding_object):
    filename = corresponding_object["filename"]
    
    count = 0
    print ("I am here")
    cap = cv2.VideoCapture('dataset/' + filename)   # capturing the video from the given path
    frameRate = cap.get(5)  #frame rate
    x=1
    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % math.floor(frameRate) == 0):
            filename ="frame%d.jpg" % count;count+=1
            path = './frame_images/'
            cv2.imwrite(os.path.join(path , filename), frame)
            #cv2.imwrite(filename, frame)
         
    cap.release()

def main():
    bucket="capstone-training"
    model='arn:aws:rekognition:us-east-1:332403273915:project/Capstone_Training_model/version/Capstone_Training_model.2020-03-11T21.58.27/1583978307349'
    min_confidence=50
    
    if not os.path.isdir('dataset'):
        os.mkdir('dataset')
    
    links_to_download = [
    'http://techslides.com/demos/sample-videos/small.mp4',
    ]
    for a_url in links_to_download:
        filename = a_url[a_url.rfind("/")+1:]
        print (filename)
        urllib.request.urlretrieve(a_url, 'dataset/' + filename)
        
        
        
    dataset_file_names = os.listdir('dataset/')     
    
    
    for a_dataset_file in dataset_file_names:
        corresponding_object = {
            "filename" : a_dataset_file, 
        }
        os.mkdir('frame_images')
        get_frames(corresponding_object)
        
        
        entries = os.listdir('frame_images/')     
    
        for a_entry in entries:
            client = boto3.client('s3', region_name='us-west-2')
        
            client.upload_file("./frame_images/" + a_entry, bucket , 'frame_images/a_entry')
    
            label_count=show_custom_labels(model,bucket,'frame_images/' +a_entry, min_confidence)
            
    #print("Custom labels detected: " + str(label_count))
    
if __name__ == "__main__":
    #main()
    

    #now = datetime.datetime.now()
    #print (str(now.isoformat()))
    pst = pytz.timezone('Canada/Eastern')
    print(datetime.now(pst).strftime("%Y%m%d%H%M%S"))
    
    #os.makedirs("demo")
    #path = "demo/husain1/"
    #os.makedirs(path)
    bucket = "capstone-training"
    #for key in bucket.list(prefix='bucket'):
        #key.delete()
        
    f = open("text_file_name.txt", "w")     
    statement = "Blockage scenario detected in instances.\n"
    f.write(statement)
    statement = "No Blockage scenario detected in .\n"
    f.write(statement)
   
    
    f.close()