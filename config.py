import boto3 ,json

## ADD Secret key below ###
aws_access_key_id = ''
aws_secret_access_key = ''


if aws_access_key_id and aws_secret_access_key:
    s3_client = boto3.client('s3',aws_access_key_id=aws_access_key_id ,aws_secret_access_key=aws_secret_access_key)
    s3_resource = boto3.client('s3',aws_access_key_id=aws_access_key_id ,aws_secret_access_key=aws_secret_access_key)
else:
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
AWS_CONFIG_BUCKET_NAME = 'configinfobucket' 
AWS_CONFIG_BUCKET_PATH = 'cred.json'

s3_object = s3_client.get_object(Bucket= AWS_CONFIG_BUCKET_NAME, Key=AWS_CONFIG_BUCKET_PATH)
config_data = json.loads(s3_object['Body'].read())

### Loading all details ##
Super_Admin_Access_Token  = config_data.get('Super_Admin_Access_Token')
AWS_BucketName = config_data.get('AWS_BucketName') 
Azure_Storage_Name = config_data.get('Azure_Storage_Name')
GCP_Storage_Name = config_data.get('GCP_Storage_Name')


gcp_credentials = config_data.get('gcp_credentials')


postgres_credentials = config_data.get('postgres_credentials')
Azure_connection_url = config_data.get('Azure_connection_url')

