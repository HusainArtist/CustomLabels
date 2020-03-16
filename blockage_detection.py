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
import datetime
from datetime import datetime
import pytz
import urllib.request
import shutil
    
# split the dataset into the frames    
def get_frames(corresponding_object):
    filename = corresponding_object["filename"]
    
    count = 0
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
    path_image = corresponding_object["path_image"]
    frame_name = corresponding_object["frame_name"]

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
    
    
    print (imgWidth, imgHeight)

    #calculate and display bounding boxes for each detected custom label
    #('Detected custom labels for ' + photo)
    
    
    ### Defining global variables
    car_array = []  
    human_array = []
    walkway_array = []
    global_blockage = False
    
    
    
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        
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
            fnt = ImageFont.truetype('arial.ttf', 12)
            
            if labelname == "Human":
                length = len(human_array) + 1
            elif labelname == "Car":
                length = len(car_array) + 1
            elif labelname == "Walkway":
                length = len(walkway_array) + 1
            
            
            #print (box['Left'], left, length, labelname)
            #print (box['Top'], top, length, labelname)
            #print (box['Width'], width, length, labelname)
            #print (box['Height'], height, length, labelname)
            
            ### This draws bounded boxes on the image
            draw.text((left,top), customLabel['Name'] + " " + str(length), fill='#000000', font=fnt)
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
            
            y_point = imgHeight - (top + height)
            a_plot = {"x": left, "y" : y_point}
            b_plot = {"x": left + width, "y" : y_point}
            c_plot = {"x": left + width, "y": y_point + height}
            d_plot = {"x": left, "y": y_point + height}
            
            print (a_plot, length, labelname)
            print (b_plot, length, labelname)
            print (c_plot, length, labelname)
            print (d_plot, height, length, labelname)
            
            
            ### Making an object of details obtained from above
            label_details = {
                "a_plot" : a_plot,
                "b_plot" : b_plot,
                "c_plot" : c_plot,
                "d_plot" : d_plot,
                "label" : labelname,
                "length" : length
            }
            
            if labelname == "Human" or labelname == "Car":
                label_details = calculate_midpoints(label_details)
            
                if labelname == "Human":
                    human_array.append(label_details)
                elif labelname == "Car":
                    car_array.append(label_details)
                    
            if labelname == "Walkway":
                walkway_array.append(label_details)
            

    corresponding_object = {
        "walkway_array" : walkway_array,
        "human_array" : human_array,
        "car_array" : car_array
    }
    
    response_object = validate_labels(corresponding_object)
    human_array = response_object["human_array"]
    car_array = response_object["car_array"]
    
    print (car_array)
            
    for a_car in car_array:
        
        blockage_details = detect_blockage(a_car, human_array)

        if blockage_details["blockage_detected"] == True:
           global_blockage = True
           
       
      
    print (global_blockage)
    if global_blockage == True:
        image.save(path_image+"/"+frame_name) 
            

    response_object = {
        "global_blockage" : global_blockage
    }
    return response_object


def validate_labels(corresponding_object):
    walkway_array = corresponding_object["walkway_array"]
    human_array = corresponding_object["human_array"]
    car_array = corresponding_object["car_array"]
    
    
    validated_human_array = []
    validated_car_array = []
    
    
    for a_walkway in walkway_array:
    
        
        assumed_a_plot = {"x": a_walkway["a_plot"]["x"] - 150 , "y" : a_walkway["a_plot"]["y"] - 150}
        assumed_b_plot = {"x": a_walkway["b_plot"]["x"] + 150 , "y" : a_walkway["b_plot"]["y"] - 150}
        assumed_c_plot = {"x": a_walkway["c_plot"]["x"] + 150 , "y" : a_walkway["d_plot"]["y"] + 150}
        assumed_d_plot = {"x": a_walkway["d_plot"]["x"] - 150 , "y" : a_walkway["d_plot"]["y"] + 150}
        
        for a_human in human_array:
            
            corresponding_object = {
                "assumed_a_plot" : assumed_a_plot,
                "assumed_b_plot" : assumed_b_plot,
                "assumed_c_plot" : assumed_c_plot,
                "assumed_d_plot" : assumed_d_plot,
                
                "label_a_plot" : a_human["a_plot"],
                "label_b_plot" : a_human["b_plot"],
                "label_c_plot" : a_human["c_plot"],
                "label_d_plot" : a_human["d_plot"],
                
            }
            
            status = box_logic_condition(corresponding_object)
            
            if status == True:
                validated_human_array.append(a_human)
                
        for a_car in car_array:
            
            corresponding_object = {
                "assumed_a_plot" : assumed_a_plot,
                "assumed_b_plot" : assumed_b_plot,
                "assumed_c_plot" : assumed_c_plot,
                "assumed_d_plot" : assumed_d_plot,
                
                "label_a_plot" : a_car["a_plot"],
                "label_b_plot" : a_car["b_plot"],
                "label_c_plot" : a_car["c_plot"],
                "label_d_plot" : a_car["d_plot"],
                
            }
            
            if a_car["length"] == 1:
                print (assumed_a_plot)
                print (assumed_b_plot)
                print (assumed_c_plot)
                print (assumed_d_plot)
                
                print (a_car["a_plot"])
                print (a_car["b_plot"])
                print (a_car["c_plot"])
                print (a_car["d_plot"])
            
            status = box_logic_condition(corresponding_object)
            if status == True:
                validated_car_array.append(a_car)
                
        
    response_object = {
        "car_array" : validated_car_array,
        "human_array" : validated_human_array
    }       
        
            
            
    
    return response_object
     
    
    

def box_logic_condition(corresponding_object):
    assumed_a_plot = corresponding_object["assumed_a_plot"]
    assumed_b_plot = corresponding_object["assumed_b_plot"]
    assumed_c_plot = corresponding_object["assumed_c_plot"]
    assumed_d_plot = corresponding_object["assumed_d_plot"]
    
    label_a_plot = corresponding_object["label_a_plot"]
    label_b_plot = corresponding_object["label_b_plot"]
    label_c_plot = corresponding_object["label_c_plot"]
    label_d_plot = corresponding_object["label_d_plot"]
    
    #label_a_plot["x"] = 6
    #label_a_plot["y"] = 7
    
    #assumed_a_plot["x"] = 5
    #assumed_a_plot["y"] = 6
    
    #label_b_plot["x"] = 7
    #label_b_plot["y"] = 7
    
    #assumed_b_plot["x"] = 9
    #assumed_b_plot["y"] = 6
    
    #label_c_plot["x"] = 7
    #label_c_plot["y"] = 8
    
    #assumed_c_plot["x"] = 9
    #assumed_c_plot["y"] = 10
    
    #label_d_plot["x"] = 6 
    #label_d_plot["y"] = 8 
    
    #assumed_d_plot["x"] = 5
    #assumed_d_plot["y"] = 10
    
    if label_a_plot["x"] >= assumed_a_plot["x"] and label_a_plot["y"] >= assumed_a_plot["y"] and label_b_plot["x"] <= assumed_b_plot["x"] and label_b_plot["y"] >= assumed_b_plot["y"] and label_c_plot["x"] <= assumed_c_plot["x"] and label_c_plot["y"] <= assumed_c_plot["y"] and label_d_plot["x"] >= assumed_d_plot["x"] and label_d_plot["y"] <= assumed_d_plot["y"]:
        return True
     
    else:
        return False
     
    
#### This function calculates coordinate between two coordinates
def calculate_midpoints(label_details):
    midpoint_x = (label_details["a_plot"]["x"] + label_details["b_plot"]["x"] / 2)
    midpoint_y = (label_details["a_plot"]["y"] + label_details["d_plot"]["y"] / 2)
    
    label_details["center"] = {"x": midpoint_x, "y" : midpoint_y}
    return label_details
    
    
    
def detect_blockage(label_details, array):
    blockage_instance = 0
    blockage_detected = False
    
    for a_array in array:
        
        
        distance = calculate_distane(a_array["center"], label_details["center"])
        print (a_array["label"], a_array["length"])
        if ((a_array["label"] == "Human" and a_array["length"] == 22) and (label_details["label"] == "Car" and label_details["length"] == 3)):
            print (distance, "distance")
        status = detect_distance(distance)
        
        
        if status == True:
            blockage_instance+=1
            blockage_detected = True


    blockage_details = {
            "blockage_instance" : blockage_instance,
            "blockage_detected" : blockage_detected
    }
    return blockage_details
            
    
def calculate_distane(p,q):
    y_diff =  q["y"] - p["y"]
    x_diff = q["x"] - p["x"]
    distance = abs(((y_diff)*2 + (x_diff)*2)/2)
    return distance
   
    
def detect_distance(distance):
    
    if distance <= 50:
        return True
    else:
        return False
    
        
    
def main():
    bucket="capstone-training"
    model='arn:aws:rekognition:us-east-1:332403273915:project/Techsquad1/version/Techsquad1.2020-03-15T15.49.52/1584301790310'
    min_confidence=80
    
    text_array = []
    
    
    pst = pytz.timezone('Canada/Eastern')
    text_file_name = datetime.now(pst).strftime("%Y%m%d%H%M%S")
    if not os.path.isdir('dataset'):
        os.mkdir('dataset')
        
    if not os.path.isdir('OutputReport'):
        os.mkdir('OutputReport')
    
    if not os.path.isdir('OutputResult'):
        os.mkdir('OutputResult')
        
    links_to_download = [
    'http://techslides.com/demos/sample-videos/small.mp4',
    ]
    for a_url in links_to_download:
        filename = a_url[a_url.rfind("/")+1:]
        print (filename)
        #urllib.request.urlretrieve(a_url, 'dataset/' + filename)
        
        
        
    dataset_file_names = os.listdir('dataset/')     
    
                

                
    for a_dataset_file in dataset_file_names:
        s3 = boto3.client('s3')
        bucket_name = "capstone-training"
        #try:
            #bucket_name = a_dataset_file.lower()
            #s3.create_bucket(Bucket=bucket_name)
        #except:
            #bucket_name = text_file_name
            #s3.create_bucket(Bucket=text_file_name)
            
        blockage_instance = 0
        
        path_image = "OutputResult/ " + a_dataset_file + "_" + text_file_name
        if not os.path.isdir(path_image):
            os.mkdir(path_image)
        
        if not os.path.isdir('frame_images'):
            os.mkdir('frame_images')
        
        
        corresponding_object = {
            "filename" : a_dataset_file, 
        }
        get_frames(corresponding_object)
        
        entries = os.listdir('frame_images/')     
        print (len(entries))
                
                
        for a_entry in entries:
            with open("./frame_images/" + a_entry , "rb") as f:
                s3.upload_fileobj(f, bucket_name, a_dataset_file +"/frame_images/" + a_entry)
                
        for a_entry in entries:
                
            corresponding_object = {
                "model" : model,
                "bucket" : bucket_name,
                "photo" : a_dataset_file +"/frame_images/" + a_entry, 
                "min_confidence" : min_confidence,
                "dataset_file_name" : a_dataset_file,
                "path_image" : path_image,
                "frame_name" : a_entry
            }
    
            response_object =show_custom_labels(corresponding_object)
            
            if response_object["global_blockage"] == True:
                blockage_instance+=1
           
        
        
        if blockage_instance > 0:
            statement = "Blockage scenario detected in " +a_dataset_file+ " with " +str(blockage_instance)+ " instances.\n"

        else: 
            statement = "No Blockage scenario detected in " +a_dataset_file+ ".\n"
            

        text_array.append(statement)
        
        
        dir_path = './frame_images/'
    
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))
        

            
        s3_resource = boto3.resource('s3')
        bucket_object = s3_resource.Bucket(bucket_name)
        bucket_object.objects.filter(Prefix=a_dataset_file).delete()
        
    f = open("OutputReport/"+text_file_name +".txt", "w")
    
    for a_text in text_array:
        f.write(a_text)
        
    f.close()
    
if __name__ == "__main__":
    main()