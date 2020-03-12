import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

client = boto3.client('s3') #low-level functional API

resource = boto3.resource('s3') #high-level object-oriented API
my_bucket = resource.Bucket('my-bucket')


import pandas as pd


    
obj = client.get_object(Bucket='comparedataset', Key='frame2.jpg')
im1 = Image.open(obj) 