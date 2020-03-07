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
    print(image)
    image.show()

    
    

    labelname = "Human"

            
            
    x = 10
    y = 12
    width_image = 4
    height_image = 7

            
            
            
            
         
            
            
            
    ##### Husain Code
    
    
        
    a_plot = {x: x, y : y}
    b_plot = {x: x+ width_image, y : y}
    c_plot = {x: x+ width_image, y: y + height_image}
    d_plot = {x: x, y: y + height_image}
    

    print (a_plot[x])
        
        
        
    car_plot.append(a)
        
            
            
            
            
            
            
            
            
            
            
    
    #image.show
    #image.save("geeks.jpg") 
    #return len(response['CustomLabels'])
    
    return 1 
    
def main():
    bucket="comparedataset"
    photo="frame22.jpg"
    model='arn:aws:rekognition:us-east-1:821691753366:project/TechSquadDemo/version/TechSquadDemo.2020-03-05T06.47.44/1583408864257'
    min_confidence=50
    
    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    #print("Custom labels detected: " + str(label_count))
    
if __name__ == "__main__":
    main()
