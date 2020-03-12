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
    bucket="comparedataset"
    photo="frame2.jpg"
    model='arn:aws:rekognition:us-east-1:332403273915:project/Capstone_Training_model/version/Capstone_Training_model.2020-03-11T21.58.27/1583978307349'
    min_confidence=50
    
    label_count=show_custom_labels(model,bucket,photo, min_confidence)
    #print("Custom labels detected: " + str(label_count))
    
if __name__ == "__main__":
    main()
