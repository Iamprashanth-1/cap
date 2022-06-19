import boto3 ,json
s3 = boto3.client('s3')
s3_object = s3.get_object(Bucket='configinfobucket', Key='cred.json')
config_data = json.loads(s3_object['Body'].read())

### Loading all details ##
Super_Admin_Access_Token  = config_data.get('Super_Admin_Access_Token')
AWS_BucketName = config_data.get('AWS_BucketName') 
Azure_Storage_Name = config_data.get('Azure_Storage_Name')
GCP_Storage_Name = config_data.get('GCP_Storage_Name')


gcp_credentials = config_data.get('gcp_credentials')


postgres_credentials = config_data.get('postgres_credentials')
Azure_connection_url = config_data.get('Azure_connection_url')

