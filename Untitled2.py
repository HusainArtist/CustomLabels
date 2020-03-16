"""
Your module description
"""
import boto3
import io
import json
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont
import cv2
import os
import math 
from io import BytesIO
import urllib.request


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

def show_custom_labels(corresponding_object):
    
    model = corresponding_object["model"]
    bucket = corresponding_object["bucket"]
    photo = corresponding_object["photo"]
    min_confidence = corresponding_object["min_confidence"]
    dataset_file_name = corresponding_object["dataset_file_name"]

    client=boto3.client('rekognition')
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()
    stream = io.BytesIO(s3_response['Body'].read())
    
    image=Image.open(stream)
    image.show()
            
    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MinConfidence=min_confidence, ProjectVersionArn=model)
    
    
    imgWidth, imgHeight = image.size ### gives the width and height of the image
    draw = ImageDraw.Draw(image) ### copies the same image

    #calculate and display bounding boxes for each detected custom label

    for customLabel in response['CustomLabels']:

        
        labelname = str(customLabel['Name'])
        
        
        ##Defining colors
        if str(customLabel['Name']) == "Car":
            color = '#33cc33'
        elif str(customLabel['Name']) == "Human":
            color = '#ff3300'
        elif str(customLabel['Name']) == "Walkway":
            color = '#3333ff'
        else:
            color = '#33cc33'
            
        
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']
            

            #fnt = ImageFont.load_default()
            #fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
            fnt = ImageFont.truetype('arial.ttf', 5)
            
            
            ### This draws bounded boxes on the image
            draw.text((left,top), customLabel['Name'], fill='#00d400', font=fnt)
            #print('Left: ' + '{0:.0f}'.format(left))
            #print('Top: ' + '{0:.0f}'.format(top))
            #print('Face Width: ' + "{0:.0f}".format(width))
            #print('Face Height: ' + "{0:.0f}".format(height))
            points = (
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill=color, width=2)         
            
            
         
            
            

            
            
            
            
            
    print (response['CustomLabels'])        
    
    
    image.show
    image.save("geeks.jpg") 
    return response['CustomLabels']
    
    
    

     
    
    


    
    

    
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
        if not os.path.isdir('dataset'):
            os.mkdir('frame_images')
        get_frames(corresponding_object)
        
        
        entries = os.listdir('frame_images/')     
    
        for a_entry in entries:
            client = boto3.client('s3', region_name='us-west-2')
        
            client.upload_file("./frame_images/" + a_entry, bucket , 'frame_images/' + a_entry)
            
            corresponding_object = {
                "model" : model,
                "bucket" : bucket,
                "photo" : "frame_images/" + a_entry, 
                "min_confidence" : min_confidence,
                "dataset_file_name" : a_dataset_file
            }
    
            label_count=show_custom_labels(corresponding_object)
    
if __name__ == "__main__":
    main()
