
import sqlite3
import hashlib, uuid
import boto3
import psycopg2
from config import gcp_credentials ,Azure_connection_url
from google.cloud import storage


from azure.storage.blob import BlobClient ,BlobServiceClient
#db = sqlite3.connect('test.db')

def upload_to_s3(file_data , bucket_name , file_name):
    #print(file_data , bucket_name, file_name)
    try:
        s3 = boto3.client('s3')
        s3.upload_fileobj(file_data, bucket_name, file_name) 
    except:
        s3 = boto3.resource('s3')
        content=file_data
        s3.Object(bucket_name, file_name).put(Body=content)

def download_from_s3( bucket_name ,file_name):
    
    s3 = boto3.client('s3')
    s3_object = s3.get_object(Bucket=bucket_name, Key=file_name)
    return s3_object['Body'].read()




def upload_to_gcp(contents ,bucket_name,  destination_file_name):
    """Uploads a file to the bucket."""
    #from oauth2client.service_account import ServiceAccountCredentials
    import os


    # credentials_dict = {
    #     'type': 'service_account',
    #     'client_id': os.environ['BACKUP_CLIENT_ID'],
    #     'client_email': os.environ['BACKUP_CLIENT_EMAIL'],
    #     'private_key_id': os.environ['BACKUP_PRIVATE_KEY_ID'],
    #     'private_key': os.environ['BACKUP_PRIVATE_KEY'],
    # }
    # cred = ServiceAccountCredentials.from_json_keyfile_dict(
    #     cred
    # )

    # The ID of your GCS object
    # destination_file_name = "storage-object-name"
    try:
        storage_client = storage.Client.from_service_account_info(gcp_credentials)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_file_name)
        try:
            content = contents.read()

            blob.upload_from_string(content)

            return 'Succesfully'
        except:
            blob.upload_from_string(contents)
            return 'Succesfully Uploaded'
    except Exception as e:
        raise Exception(f'Error uploading file {e}')

    print(
        f"{destination_file_name} with contents {contents} uploaded to {bucket_name}."
    )
    
from google.cloud import storage


def download_from_gcp(bucket_name, file_name):
    """Downloads a blob into memory."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # file_name = "storage-object-name"
    try:
        storage_client = storage.Client.from_service_account_info(gcp_credentials)

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        contents = blob.download_as_string()
        return contents
    except Exception as e:
        raise Exception(f'Error downloading file {e}')

    print(
        "Downloaded storage object {} from bucket {} as the following string: {}.".format(
            file_name, bucket_name, contents
        )
    )

def download_from_azure(bucket_name, file_name):
    
    conn_str=Azure_connection_url
    try:
        blob = BlobClient.from_connection_string(conn_str=conn_str,container_name=bucket_name, blob_name=file_name)
        data = blob.download_blob().readall()
        return data
    except Exception as e:
        raise Exception(f'Error downloading file {e}')
def upload_to_azure(file_data ,bucket_name, file_name):
    
    
    blob_client = BlobClient.from_connection_string(conn_str=Azure_connection_url,container_name=bucket_name, blob_name=file_name)

    try:
        blob_client.upload_blob(file_data.read())
        return 'uploaded successfully'
    except:
        blob_client.upload_blob(file_data)
        return 'uploaded successfully'
        


class DB:
    def __init__(self ,credntials):
        self.db = self.connect(credntials)
        self.admin_users()
        self.create_token_store_table()
        self.create_table()


        pass
    def connect(self ,credentials):
        self.con_  = psycopg2.connect(
            host = credentials.get('host'),
            port = credentials.get('port'),
            database = credentials.get('dbname'),
            user = credentials.get('username'),
            password = credentials.get('password')
        )
        
        self.db = self.con_.cursor()

        return self.db
    
    def create_token_store_table(self):
        q= '''
            CREATE TABLE IF NOT EXISTS tokens(
                id int GENERATED BY DEFAULT AS IDENTITY,
                user_name varchar(100),
                token varchar(255),
                token_created_date timestamp,
                token_expiry_data timestamp,
                single_file varchar(255),

                Primary key(id)
                )

            '''
        try:
            self.db.execute(q)
            self.con_.commit()
            return 'Succesfully created'
        except:
            return 'Failed to create'
    
    def insert_to_tokens(self, user_name , token , token_created_date ,token_expiry_data ,single_file='ALL'):
        q= f'''

        insert into tokens (user_name ,token , token_created_date ,token_expiry_data ,single_file) values(%s,%s,%s,%s,%s)
        '''
        self.db.execute(q ,(user_name ,token, token_created_date, token_expiry_data ,single_file))
        self.con_.commit()
        return 'Inserted successfully'
    
    def validate_token(self , token):
        q= f'''

        select * from tokens where token = '{token}' and LOCALTIMESTAMP < token_expiry_data;
        '''
        cursor = self.db.execute(q )
        cc= self.db.fetchall()
        for row in cc:
            #print(row)
            return row , True
        return 'Invalid credentials' , False



    def create_table(self):
        q = f'''

        CREATE TABLE IF NOT EXISTS blobstorage(
            id int GENERATED BY DEFAULT AS IDENTITY,
            cloud_type varchar(10),
            file_name varchar(255),
            bucket_name varchar(255),
            upload_time timestamp,
            token varchar(255),
            file_path varchar(555),

            Primary key(id)

        )
        '''
        try:
            self.db.execute(q)
            self.con_.commit()
            return 'Succesfully created'
        except:
            return 'Failed to create'
    
    def insert_to_filestorage(self, params):
        q= f'''
        insert into blobstorage(cloud_type , file_name ,bucket_name ,upload_time ,token ,file_path) values('{params.get('cloud_type')}' , 
        '{params.get('file_name')}' ,'{params.get('bucket_name')}' ,LOCALTIMESTAMP,'{params.get('token')}',
        '{params.get('file_path')}')
        '''
        try:
            self.db.execute(q)
            self.con_.commit()
            return 'Inserted successfully' ,True
        except:
            return 'Failed to insert' , False
    def validate_file_get_cloud_type(self , filename ,token):

        q= f'''
        select id ,cloud_type , file_path , bucket_name ,upload_time from blobstorage where file_name = '{filename}' and token = '{token}'
        '''
        cursor = self.db.execute(q )
        cc= self.db.fetchall()

        for row in cc:
            #print(row)
            return row , True
        return 'No file found', False
    def get_all_files(self ,token):
        q= f'''
        select id ,cloud_type , file_name ,upload_time  from blobstorage where token = '{token}';
        '''
        cursor = self.db.execute(q )
        cc= self.db.fetchall()
        
        return cc

    
    def get_objects(self,file_name ,token):
        q = f'''
        select * from blobstorage where file_name ='{file_name}' and token = '{token}'
        '''
        cursor = self.db.execute(q)
        cc= self.db.fetchall()
        try:
            #print(cc)
            if cc:
                for row in cc:
                    return row , True
            return 'Not Found' , False
        except:
            return 'Failed' , False

    def admin_users(self):
        q = f'''
        CREATE TABLE IF NOT EXISTS admin_users(
            user_name varchar(255),
            password varchar(255) ,
            api_key varchar(255)
        )
        
        '''
        self.db.execute(q)
        self.con_.commit()
    def admin_validate(self ,user_name ,password):
        q= f'''

        select api_key  from admin_users where user_name = '{user_name}' and password = '{password}';

        '''
        self.db.execute(q)
        cc= self.db.fetchone()
        #print(cc ,list(cc))
        try:
            if cc:
                for row in cc:
                    #print(row)
                    return row , True
            return 'api' , False
        except:
            return None , False
    def validate_api(self, api):
        q= f'''

        select api_key  from admin_users where api_key = '{api}';

        '''
        cursor = self.db.execute(q )
        cc= self.db.fetchall()
        try:
            for row in cc:
                #print(row)
                return row[0] , True
        except:
            return None , False

    def admin_insert(self ,user_names ,passwords ,api):
       # print(user_names , passwords)
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(passwords.encode('utf-8')).hexdigest()
        q= f'''

        insert into admin_users(user_name,password,api_key) VALUES (%s,%s,%s);
        '''
        try:
            self.db.execute(q ,(user_names , hashed_password ,api))
            self.con_.commit()
        except:
            return False

