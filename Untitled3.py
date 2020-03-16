import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import cv2
import os
import math 
import boto3
from io import BytesIO

import shutil
    


#client = boto3.client('s3') #low-level functional API

#resource = boto3.resource('s3') #high-level object-oriented API
#my_bucket = resource.Bucket('my-bucket')

    
#obj = client.get_object(Bucket='capstone-training', Key='Dataset.mp4')
#obj = obj.get()['Body'].read()


#from moviepy.editor import *

#client = boto3.client('s3')
#VideoFileClip(BytesIO(obj['Body'].read()))




def get_frames():
    
    count = 0
    print ("I am here")
    videoFile = 'Dataset.mp4'
    cap = cv2.VideoCapture(videoFile)   # capturing the video from the given path
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


s3 = boto3.resource('s3')
bucket = s3.Bucket('capstone-training')
bucket.download_file('Dataset.mp4', 'Dataset.mp4')


get_frames()

entries = os.listdir('frame_images/')     
print (entries)

for a_entry in entries:
    client = boto3.client('s3', region_name='us-west-2')
    
    client.upload_file("./frame_images/" + a_entry, 'capstone-training', 'demo/a_entry')
    
dir_path = './frame_images/'
    
try:
    shutil.rmtree(dir_path)
except OSError as e:
    print("Error: %s : %s" % (dir_path, e.strerror))
    
for key in bucket.list(prefix='dataset/'):
    key.delete()
      


#import pandas as pd


    
#obj = client.get_object(Bucket='comparedataset', Key='frame2.jpg')

#import boto3

#client = boto3.client('s3', region_name='us-west-2')

#client.upload_file('geeks.jpg', 'capstone-training', 'demo/image_0.jpg')

