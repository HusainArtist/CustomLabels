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

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MinConfidence=min_confidence, ProjectVersionArn=model)
    
    
    imgWidth, imgHeight = image.size ### gives the width and height of the image
    draw = ImageDraw.Draw(image) ### copies the same image
    
    
    #print (imgWidth, imgHeight)

    #calculate and display bounding boxes for each detected custom label
    #('Detected custom labels for ' + photo)
    
    
    ### Defining global variables
    car_array = []  
    human_array = []
    walkway_array = []
    global_blockage = False
    length = 0
    
    
    for customLabel in response['CustomLabels']:
        print('Label ' + str(customLabel['Name']))
        
        labelname = str(customLabel['Name']).strip()
        
        
        ##Defining colors
        if str(customLabel['Name']) == "Car":
            color = '#33cc33' #
        elif str(customLabel['Name']) == "Human":
            color = '#663300'
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
            
            print (labelname)
            if labelname == 'Human':
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
    
    print (human_array, "human_array")
            
    for a_car in car_array:
        
        blockage_details = detect_blockage(a_car, human_array, image)

        if blockage_details["blockage_detected"] == True:
           global_blockage = True
           
       
      
    print (global_blockage)
    if global_blockage == True:
        print("Blockage Detected in the given video")
            

    image.show
    image.save("geeks.jpg") 
    return len(response['CustomLabels'])


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
        
        print (a_walkway, "a_walkway")
        
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
            
            print (corresponding_object)
            
            status = box_logic_condition(corresponding_object)
            
            if status == True:
                if a_human not in validated_human_array:
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
                 if a_car not in validated_human_array:
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
    
    
    
def detect_blockage(label_details, array, image):
    blockage_instance = 0
    blockage_detected = False
    
    for a_array in array:
        
        
        distance = calculate_distane(a_array["center"], label_details["center"])
        print (distance, "distance")
        status = detect_distance(distance)
        
        
        if status == True:
            blockage_instance+=1
            blockage_detected = True
                
            blockage_midpoint_x = (label_details["center"]["x"] + a_array["center"]["x"] / 2)
            blockage_midpoint_y = (label_details["center"]["y"] + a_array["center"]["y"] / 2)
            
            draw = ImageDraw.Draw(image)
            
            imgWidth, imgHeight = image.size
            
            left = blockage_midpoint_x - 10
            top = imgHeight - (blockage_midpoint_y - 10)
            width = 50
            height = 50
            
            fnt = ImageFont.truetype('arial.ttf', 10)
            blockage_color = "#ff0000"
            draw.text((left + 5, top + 20), "Blockage", fill="#ff6666", font=fnt)
        
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
    
    if distance <= 50:
        return True
    else:
        return False
    
        
    
def main():
    bucket="husainbucket"
    photo="frame10.jpg"
    model='arn:aws:rekognition:us-east-1:812009147528:project/PWSS/version/PWSS.2020-03-17T16.24.46/1584476684777'
    min_confidence=70
    
    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    print("Custom labels detected: " + str(label_count))
    
if __name__ == "__main__":
    main()