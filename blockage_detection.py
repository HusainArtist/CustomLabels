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
    
model_arn='arn:aws:rekognition:us-east-1:812009147528:project/PSWW1/version/PSWW1.2020-03-18T18.06.31/1584569191868'
min_inference_units=1

walkway_additional_boundary = 50
maximum_threshold_value = 50

min_confidence=50
bucket = "techsquad2020"

text_array = []
pst = pytz.timezone('Canada/Eastern')
text_file_name = datetime.now(pst).strftime("%Y%m%d%H%M%S")

font_label = ImageFont.truetype('arial.ttf', 12)

blockage_color = "#ff0000"
blockage_box_assumption = 10
blockage_font = ImageFont.truetype('arial.ttf', 10)

blockage_width = blockage_height = 50 
blockage_text_left = 5
blockage_text_top = 20

frames_per_sec = 15

def start_model():
    
    client=boto3.client('rekognition') 
    
    try:
        # Start the model
        
        response=client.start_project_version(ProjectVersionArn=model_arn,
        MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        print('Model started !!!')
    except Exception as e:
        print('Model already running')
        
        


def stop_model():

    client=boto3.client('rekognition')
    print('Stopping model:' + model_arn)
    #Stop the model
    try:
        response=client.stop_project_version(ProjectVersionArn=model_arn)
        status=response['Status']
        print ('Status: ' + status)
    except Exception as e:
        print('Model already in a stopped state !!!')

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
         
    cap.release()
    
def show_custom_labels(corresponding_object):
    photo = corresponding_object["photo"]
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
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MinConfidence=min_confidence, ProjectVersionArn=model_arn)
    
    
    imgWidth, imgHeight = image.size ### gives the width and height of the image
    draw = ImageDraw.Draw(image) ### copies the same image

    #calculate and display bounding boxes for each detected custom label
    #('Detected custom labels for ' + photo)
    
    
    ### Defining global variables
    car_array = []  
    human_array = []
    walkway_array = []
    global_blockage = False
    
    for customLabel in response['CustomLabels']:
        
        labelname = str(customLabel['Name']).strip()
        
        
        ##Defining colors
        if labelname == "Car":
            color = '#33cc33' # green color
        elif labelname == "Human":
            color = '#663300' # brown color
        elif labelname == "Walkway":
            color = '#3333ff' # walkway color
        else:
            color = '#33cc33' # green color
            
        
        if 'Geometry' in customLabel:
            box = customLabel['Geometry']['BoundingBox']
            left = imgWidth * box['Left']
            top = imgHeight * box['Top']
            width = imgWidth * box['Width']
            height = imgHeight * box['Height']
        
            
            if labelname == "Human" or labelname == 'Human ':
                length = len(human_array) + 1
            elif labelname == "Car":
                length = len(car_array) + 1
            elif labelname == "Walkway":
                length = len(walkway_array) + 1
       
            
 
            
            ### This draws bounded boxes on the image
            draw.text((left,top), customLabel['Name'] + " " + str(length), fill='#000000', font=font_label)
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
    
    for a_car in car_array:
        
        blockage_details = detect_blockage(a_car, human_array, image)

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
    
        
        assumed_a_plot = {"x": a_walkway["a_plot"]["x"] - walkway_additional_boundary , "y" : a_walkway["a_plot"]["y"] - walkway_additional_boundary}
        assumed_b_plot = {"x": a_walkway["b_plot"]["x"] + walkway_additional_boundary , "y" : a_walkway["b_plot"]["y"] - walkway_additional_boundary}
        assumed_c_plot = {"x": a_walkway["c_plot"]["x"] + walkway_additional_boundary , "y" : a_walkway["d_plot"]["y"] + walkway_additional_boundary}
        assumed_d_plot = {"x": a_walkway["d_plot"]["x"] - walkway_additional_boundary , "y" : a_walkway["d_plot"]["y"] + walkway_additional_boundary}
        
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
    
    
    
def detect_blockage(label_details, array, image):
    blockage_instance = 0
    blockage_detected = False
    
    for a_array in array:

        distance = calculate_distane(a_array["center"], label_details["center"])
        status = detect_distance(distance)
        
        
        if status == True:
            blockage_instance+=1
            blockage_detected = True
            
            blockage_midpoint_x = (label_details["center"]["x"] + a_array["center"]["x"] / 2)
            blockage_midpoint_y = (label_details["center"]["y"] + a_array["center"]["y"] / 2)
            
            draw = ImageDraw.Draw(image)
            
            imgWidth, imgHeight = image.size
            
            left = blockage_midpoint_x - blockage_box_assumption
            top = imgHeight - (blockage_midpoint_y - blockage_box_assumption)
            width = blockage_width
            height = blockage_height
            
            draw.text((left + blockage_text_left, top + blockage_text_top), "Blockage", fill="#ff6666", font=blockage_font)
        
            points = ( 
                (left,top),
                (left + width, top),
                (left + width, top + height),
                (left , top + height),
                (left, top))
            draw.line(points, fill=blockage_color, width=3)


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
    
    if distance <= maximum_threshold_value:
        return True
    else:
        return False
    
        
    
def main():
    
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
        #urllib.request.urlretrieve(a_url, 'dataset/' + filename)
        
        
        
    dataset_file_names = os.listdir('dataset/')     
    
                

                
    for a_dataset_file in dataset_file_names:
        s3 = boto3.client('s3')
            
        blockage_instance = 0
        
        path_image = "OutputResult/ " + a_dataset_file + "_" + text_file_name
        if not os.path.isdir(path_image):
            os.mkdir(path_image)
        
        
        if not os.path.isdir('frame_images'):
            os.mkdir('frame_images')
        else:
            delete_frame_images_dir()
            os.mkdir('frame_images')
        
        corresponding_object = {
            "filename" : a_dataset_file, 
        }
        get_frames(corresponding_object)
        
        frame_images_dir = os.listdir('frame_images/')     
                
                
        for a_frame in frame_images_dir:
            with open("./frame_images/" + a_frame , "rb") as f:
                s3.upload_fileobj(f, bucket, a_dataset_file +"/frame_images/" + a_frame)
                
        for a_frame in frame_images_dir:
                
            corresponding_object = {
                "photo" : a_dataset_file +"/frame_images/" + a_frame, 
                "min_confidence" : min_confidence,
                "dataset_file_name" : a_dataset_file,
                "path_image" : path_image,
                "frame_name" : a_frame
            }
    
            response_object =show_custom_labels(corresponding_object)
            
            if response_object["global_blockage"] == True:
                blockage_instance+=1
           
        
        
        if blockage_instance > 0:
            
            blockage_duration = ((blockage_instance * 0.02)/frames_per_sec)
            statement = "Blockage scenario detected in " +a_dataset_file+ " with " +str(blockage_instance)+ " instances with blockage duration " +str(blockage_duration)+ " mins.\n"

        else: 
            statement = "No Blockage scenario detected in " +a_dataset_file+ ".\n"
        text_array.append(statement)
        
        
        delete_frame_images_dir()
        

            
        s3_resource = boto3.resource('s3')
        bucket_object = s3_resource.Bucket(bucket)
        bucket_object.objects.filter(Prefix=a_dataset_file).delete()
        
    f = open("OutputReport/"+text_file_name +".txt", "w")
    
    for a_text in text_array:
        f.write(a_text)
        
    f.close()
    
def delete_frame_images_dir():
    dir_path = './frame_images/'
    
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))
    
    
def custom_choice():
    
    
    print ("\nWelcome to Pedestrian Walkway Surveillance System ")
    print ("\nPress 1 to start the API\nPress 2 to detect the video \nPress 3 to stop the API\nPress 4 to Exit")
    option = input("Enter your choice : ") 
    
    if option == "1":
        start_model()
    elif option == "2":
        main()  
    elif option == "3":
        stop_model()
        
    elif option == "4":
        print("Bye !")
        
    
if __name__ == "__main__":
    custom_choice()