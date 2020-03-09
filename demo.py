"""
Your module description
"""
import boto3
import io
import json
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

def show_custom_labels(model,bucket,photo, min_confidence):

    client=boto3.client('rekognition')
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()
    stream = io.BytesIO(s3_response['Body'].read())
    
    image=Image.open(stream)
    image.show()
            
    x = 10
    y = 12
    width_image = 4
    height_image = 7

            
            
            
            
         
            
            
            
    ##### Husain Code
    
    
        
    a_plot = {"x": x, "y" : y}
    b_plot = {"x": x+ width_image, "y" : y}
    c_plot = {"x": x+ width_image, "y": y + height_image}
    d_plot = {"x": x, "y": y + height_image}
    
    car_array = []  
    human_array = []
    walkway_array = []
    global_blockage = False
 
          
    label_details = {
        "a_plot" : a_plot,
        "b_plot" : b_plot,
        "c_plot" : c_plot,
        "d_plot" : d_plot,
        "label" : labelname
    }
    
    label_details = calculate_midpoints(label_details)
    
    if labelname == "Human":
        labelname = "Car"
        human_array.append(label_details)
    if labelname == "Car":
        car_array.append(label_details)
        
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
        blockage_details = detect_blockage(a_car, human_array)

        if blockage_details["blockage_detected"] == True:
           global_blockage = True
           
       
       
    if global_blockage == True:
        print("Blockage Detected in the given video")
            
            
            
            
            
            
            
            
    
    #image.show
    #image.save("geeks.jpg") 
    #return len(response['CustomLabels'])
    
    return 1
    
    
    
def validate_labels(corresponding_object):
    walkway_array = corresponding_object["walkway_array"]
    human_array = corresponding_object["human_array"]
    car_array = corresponding_object["car_array"]
    
    
    validated_human_array = []
    validated_car_array = []
    
    
    for a_walkway in walkway_array:
    
        
        assumed_a_plot = {"x": a_walkway["a_plot"]["x"] + 50 , "y" : a_walkway["a_plot"]["y"] + 50}
        assumed_b_plot = {"x": a_walkway["b_plot"]["x"] + 50 , "y" : a_walkway["b_plot"]["y"] + 50}
        assumed_c_plot = {"x": a_walkway["c_plot"]["x"] + 50 , "y" : a_walkway["d_plot"]["y"] + 50}
        assumed_d_plot = {"x": a_walkway["d_plot"]["x"] + 50 , "y" : a_walkway["d_plot"]["y"] + 50}
        
        for a_human in human_array:
            
            print (a_human)
            
            corresponding_object = {
                "assumed_a_plot" : assumed_a_plot,
                "assumed_b_plot" : assumed_b_plot,
                "assumed_c_plot" : assumed_c_plot,
                "assumed_d_plot" : assumed_d_plot,
                
                "label_a_plot" : a_human["a_plot"],
                "label_b_plot" : a_human["a_plot"],
                "label_c_plot" : a_human["a_plot"],
                "label_d_plot" : a_human["a_plot"],
                
            }
            
            status = box_logic_condition(corresponding_object)
            
            print (status)
            if status == True:
                validated_human_array.append(a_human)
                
        for a_car in car_array:
            
            corresponding_object = {
                "assumed_a_plot" : assumed_a_plot,
                "assumed_b_plot" : assumed_b_plot,
                "assumed_c_plot" : assumed_c_plot,
                "assumed_d_plot" : assumed_d_plot,
                
                "label_a_plot" : a_car["a_plot"],
                "label_b_plot" : a_car["a_plot"],
                "label_c_plot" : a_car["a_plot"],
                "label_d_plot" : a_car["a_plot"],
                
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
    
    label_a_plot["x"] = 6
    label_a_plot["y"] = 7
    
    assumed_a_plot["x"] = 5
    assumed_a_plot["y"] = 6
    
    label_b_plot["x"] = 7
    label_b_plot["y"] = 7
    
    assumed_b_plot["x"] = 9
    assumed_b_plot["y"] = 6
    
    label_c_plot["x"] = 7
    label_c_plot["y"] = 8
    
    assumed_c_plot["x"] = 9
    assumed_c_plot["y"] = 10
    
    label_d_plot["x"] = 6 
    label_d_plot["y"] = 8 
    
    assumed_d_plot["x"] = 5
    assumed_d_plot["y"] = 10
    
    if label_a_plot["x"] >= assumed_a_plot["x"] and label_a_plot["y"] >= assumed_a_plot["y"] and label_b_plot["x"] <= assumed_b_plot["x"] and label_b_plot["y"] >= assumed_b_plot["y"] and label_c_plot["x"] <= assumed_c_plot["x"] and label_c_plot["y"] <= assumed_c_plot["y"] and label_d_plot["x"] >= assumed_d_plot["x"] and label_d_plot["y"] <= assumed_d_plot["y"]:
        print("I am here")
        return True
     
    else:
        return False
     
    

def calculate_midpoints(plots):
    midpoint_x = (plots["a_plot"]["x"] + plots["b_plot"]["x"] / 2)
    midpoint_y = (plots["a_plot"]["y"] + plots["d_plot"]["y"] / 2)
    
    plots["center"] = {"x": midpoint_x, "y" : midpoint_y}
    return plots
    
    
    
def detect_blockage(plots, array):
    blockage_instance = 0
    blockage_detected = False
    
    for a_array in array:
        distance = calculate_distane(a_array["center"], plots["center"])
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
    x_diff = q["y"] - p["x"]
    distance = abs(((y_diff)*2 + (x_diff)*2)/2)
    return distance
   
    
def detect_distance(distance):
    
    if distance <= 25:
        return True
    else:
        return False
    
    

    
def main():
    bucket="comparedataset"
    photo="frame22.jpg"
    model='arn:aws:rekognition:us-east-1:821691753366:project/TechSquadDemo/version/TechSquadDemo.2020-03-05T06.47.44/1583408864257'
    min_confidence=50
    
    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    #print("Custom labels detected: " + str(label_count))
    
if __name__ == "__main__":
    main()
