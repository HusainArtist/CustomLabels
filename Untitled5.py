import boto3

def start_model(project_arn, model_arn, version_name, min_inference_units):
    client=boto3.client('rekognition') 
    
    try:
        # Start the model
        print('Starting model: ' + model_arn)
        response=client.start_project_version(ProjectVersionArn=model_arn,
        MinInferenceUnits=min_inference_units)
        # Wait for the model to be in the running state
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn,
        VersionNames=[version_name])
        #Get the running status
        describe_response=client.describe_project_versions(ProjectArn=project_arn,
        VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)
        
        print('Done...') 
        
        


def stop_model(model_arn):
    client=boto3.client('rekognition')
    print('Stopping model:' + model_arn)
    #Stop the model
    try:
        response=client.stop_project_version(ProjectVersionArn=model_arn)
        status=response['Status']
        print ('Status: ' + status)
    except Exception as e:
        print(e)
        print('Done...')
    

 
        
        
        
def main():
    project_arn='arn:aws:rekognition:us-east-1:812009147528:project/PWSS.2020-03-17T16.24.46/1584476684777'
    model_arn='arn:aws:rekognition:us-east-1:812009147528:project/PWSS/version/PWSS.2020-03-17T16.24.46/1584476684777'
    min_inference_units=1
    version_name='1584476684777'
    #start_model(project_arn, model_arn, version_name, min_inference_units)
    #stop_model(model_arn)
    print ("\nWelcome to Pedestrian Walkway Surveillance System ")
    print ("\nPress 1 to start the API\nPress 2 to detect the video \nPress 3 to stop the API\n")
    option = input("Enter your choice : ") 
    
    if option == "1":
       start_model(project_arn, model_arn, version_name, min_inference_units)
    elif option == "2":
        print ("Hello")    
    elif option == "3":
        stop_model(model_arn)
        
if __name__ == "__main__":
    main() 