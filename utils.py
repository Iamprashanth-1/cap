
import hashlib, uuid
import boto3
import psycopg2
from boto3.s3.transfer import TransferConfig
from config import gcp_credentials ,Azure_connection_url ,s3_client ,s3_resource
from google.cloud import storage


from azure.storage.blob import BlobClient ,BlobServiceClient


def upload_to_s3(file_data , bucket_name , file_name):
    #print(file_data , bucket_name, file_name)
    config = TransferConfig(multipart_threshold=1024*25, max_concurrency=10,
                        multipart_chunksize=1024*25, use_threads=True)
    try:
       
        s3_client.upload_fileobj(file_data, bucket_name, file_name ,Config = config)
    except:
        
        content=file_data
        s3_resource.Object(bucket_name, file_name).put(Body=content)

def get_total_bytes(s3 ,bucket_name ,file_path ,prefix):
    result = s3.list_objects(Bucket=bucket_name ,Prefix=prefix)
    for item in result['Contents']:
        if item['Key'] == file_path:
            return item['Size']


def get_object(s3, total_bytes ,bucket_name ,file_path):
    if total_bytes > 1000000:
        return get_object_range(s3, total_bytes ,bucket_name ,file_path)
    return s3.get_object(Bucket=bucket_name, Key=file_path)['Body'].read()


def get_object_range(s3, total_bytes ,bucket_name ,file_path):
    offset = 0
    while total_bytes > 0:
        end = offset + 999999 if total_bytes > 1000000 else ""
        total_bytes -= 1000000
        byte_range = 'bytes={offset}-{end}'.format(offset=offset, end=end)
        offset = end + 1 if not isinstance(end, str) else None
        yield s3.get_object(Bucket=bucket_name, Key=file_path, Range=byte_range)['Body'].read()


def download_from_s3( bucket_name ,file_path , file_name):
    prefix = file_path.split('/')[0]
    total_bytes = get_total_bytes(s3_client ,bucket_name, file_path ,prefix)
    if total_bytes > 1000000:
        return get_object_range(s3_client, total_bytes ,bucket_name ,file_path)
    return s3_client.get_object(Bucket=bucket_name, Key=file_path)['Body'].read()

    
#### GCP #################################
def get_object_range_gcp(blob, total_bytes ):
    offset = 0
    while total_bytes > 0:
        end = offset + 999999 if total_bytes > 1000000 else ""
        total_bytes -= 1000000
        byte_range = 'bytes={offset}-{end}'.format(offset=offset, end=end)
        offset = end + 1 if not isinstance(end, str) else None
        #yield blob.get_object(Bucket=bucket_name, Key=file_path, Range=byte_range)['Body'].read()
        yield blob.download_as_string(start=offset,end=end)



def upload_to_gcp(contents ,bucket_name,  destination_file_name):
    """Uploads a file to the bucket."""
    #from oauth2client.service_account import ServiceAccountCredentials
    

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

    
    


def download_from_gcp(bucket_name, file_name):
    """Downloads a blob into memory."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # file_name = "storage-object-name"
    try:
        storage_client = storage.Client.from_service_account_info(gcp_credentials)

        bucket = storage_client.bucket(bucket_name)
        bucket_c = storage_client.get_bucket(bucket_name)

        size_in_bytes = bucket_c.get_blob(file_name).size
        total_bytes = size_in_bytes
        blob = bucket.blob(file_name)

        if total_bytes > 1000000:
            return get_object_range_gcp(blob, total_bytes)
        return blob.download_as_string()
        
    except Exception as e:
        raise Exception(f'Error downloading file {e}')

    
#### AZURE #################################

def get_object_range_azure(blob, total_bytes ):
    offset = 0
    while total_bytes > 0:
        end = offset + 999999 if total_bytes > 1000000 else ""
        total_bytes -= 1000000
        byte_range = 'bytes={offset}-{end}'.format(offset=offset, end=end)
        offset = end + 1 if not isinstance(end, str) else None
        #yield blob.get_object(Bucket=bucket_name, Key=file_path, Range=byte_range)['Body'].read()
        yield blob.download_blob(offset=offset ,length=end).readall()

def download_from_azure(bucket_name, file_name):
    
    conn_str=Azure_connection_url
    try:
        blob_list = BlobServiceClient.from_connection_string(conn_str=conn_str).get_container_client(bucket_name).list_blobs()
        total_bytes =0
        for blob in blob_list:
            if blob.name == file_name:
                total_bytes = blob.size
                break

        blob = BlobClient.from_connection_string(conn_str=conn_str,container_name=bucket_name, blob_name=file_name)
        
            
        
        #total_bytes = BlockBlobService.get_blob_properties(conn_str,bucket_name,file_name).properties.content_length
        #print(total_bytes)

        if total_bytes > 1000000:
            return get_object_range_azure(blob ,total_bytes)
        data = blob.download_blob().readall()
        return data
    except Exception as e:
        raise Exception(f'Error downloading file {e}')
def upload_to_azure(file_data ,bucket_name, file_name):
    
    
    blob_client = BlobClient.from_connection_string(conn_str=Azure_connection_url,container_name=bucket_name, blob_name=file_name)
    chunk_size=10*1024*1024 
    try:
        stream = file_data.readbytes()
        while True:
            read_data = stream.read(chunk_size)
            if not read_data:
                break 
            blob_client.append_block(read_data)
        #blob_client.upload_blob(file_data.read())
        #blob_client.append_block
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
                token_expiry_date timestamp,
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
    
    def insert_to_tokens(self, user_name , token , token_created_date ,token_expiry_date ,single_file='ALL'):
        q= f'''

        insert into tokens (user_name ,token , token_created_date ,token_expiry_date ,single_file) values(%s,%s,%s,%s,%s)
        
        '''
        self.db.execute(q ,(user_name ,token, token_created_date, token_expiry_date ,single_file))
        self.con_.commit()
        return 'Inserted successfully'
    
    def validate_token(self , token):
        q= f'''

        select * from tokens where token = '{token}' and LOCALTIMESTAMP < token_expiry_date;
        '''
        cursor = self.db.execute(q )
        cc= self.db.fetchall()
        for row in cc:
            #print(row)
            return row , True
        return 'Invalid credentials' , False
    
    def validate_token_user_name(self , user_name):
        q= f'''

        select * from tokens where user_name = '{user_name}' and 19800+EXTRACT(EPOCH FROM (LOCALTIMESTAMP - token_created_date  )) >60;
        '''
        cursor = self.db.execute(q )
        cc= self.db.fetchall()
        if cc:
            return cc , True
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
        select * from blobstorage where file_name ='{file_name}' and token = '{token}' order by upload_time desc
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
            user_id INT GENERATED BY DEFAULT AS IDENTITY,
            user_name varchar(255),
            password varchar(255) ,
            api_key varchar(255) ,
            auth_token varchar(255),

            primary key(user_id)
        )
        
        '''
        self.db.execute(q)
        self.con_.commit()
    def admin_check_users(self ,user_name):
        q= f'''

        select user_name from admin_users where user_name = '{user_name}'
        '''
        self.db.execute(q)
        cc= self.db.fetchone()
        
        try:
            if cc:
                for row in cc:
                    #print(row)
                    return row , True
            return 'exists' , False
        except:
            return None , False
    def admin_check_users_with_token(self ,auth_token):
        q= f'''

        select auth_token from admin_users where auth_token = '{auth_token}'
        '''
        self.db.execute(q)
        cc= self.db.fetchone()
        
        try:
            if cc:
                
                    #print(row)
                return cc , True
            return 'Not exists' , False
        except:
            return None , False
    def admin_validate(self ,user_name ,password):
        q= f'''

        select api_key,auth_token  from admin_users where user_name = '{user_name}' and password = '{password}';

        '''
        self.db.execute(q)
        cc= self.db.fetchone()
        #print(cc ,list(cc))
        try:
            if cc:
                #for row in cc:
                    #print(row)
                return list(cc) , True
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

    def admin_insert(self ,user_names ,passwords ,api ,auth_key):
       # print(user_names , passwords)
        
        hashed_password = hashlib.sha512(passwords.encode('utf-8')).hexdigest()
        q= f'''

        insert into admin_users(user_name,password,api_key ,auth_token) VALUES (%s,%s,%s,%s);
        '''
        try:
            self.db.execute(q ,(user_names , hashed_password ,api ,auth_key))
            self.con_.commit()
        except:
            return False

