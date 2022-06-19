import os,json
import config
from config import AWS_BucketName , Azure_Storage_Name ,GCP_Storage_Name ,postgres_credentials ,Super_Admin_Access_Token
import urllib.request
from utils import *
from random import randint
from multiprocessing import Process
from threading import Thread
import datetime
from flask import send_file ,Response , session
#from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from flask import Flask, request, redirect, jsonify,render_template
from werkzeug.utils import secure_filename

from utils import * 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the random string'

db = DB(postgres_credentials)

@app.route('/',methods=['GET', 'POST'])
def main():
    return render_template('main.html')
@app.route('/super_admin',methods=['POST', 'GET'])
def register_main():
    return render_template('super_admin.html')
@app.route('/super_admin/register',methods=['POST'])
def register():
    if request.method == 'POST':
        admin_token = request.form.get('token')
        email  = request.form.get('email')
        password = request.form.get('password')
        salt = uuid.uuid4().hex
        if admin_token==Super_Admin_Access_Token:
            db.admin_insert(email,password,salt)
            return render_template('main.html')
        return {'message' : 'Registration NOT Allowed'}

@app.route('/upload_file/<token>',methods=['GET', 'POST'])
def index(token):
    val ,val_bool = db.validate_token(token)
    if val_bool:
        return render_template('home.html')
    return {'message': 'Enter Valid Token'}

@app.route('/login',methods=['GET', 'POST'])
def login():
    session['email'] = 'reddy'
    return render_template('admin.html')

@app.route('/login/admin/r/',methods=['GET', 'POST'])
def adr():
    if request.method == 'POST':
        return render_template('admin_token.html')
    return {'message': 'Please Login'}
@app.route('/login/admin/token' ,methods=['GET', 'POST'])
def token_login():
    
    if request.method == 'POST':
        token = request.form.get('token')
        token_un = token
        if token:
            token +=str(randint(1,100000000))
        file_name  = request.form.get('file_name')
        g = request.form.get('startDate' ,'2099-06-04 10:42')
        
        if len(g) == 0:
            g = '2099-06-04 10:42:00'

        else:
            g= g.replace('T',' ')
            g+=':00'
        #print(g)
        cur_date = datetime.datetime.now() 
        token_created = cur_date.strftime('%Y-%m-%d %H:%M:%S')
        

        
        hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
        if file_name:
            db.insert_to_tokens(token_un , hashed_token ,token_created,g,file_name)
        else:
            db.insert_to_tokens(token_un , hashed_token ,token_created,g,'ALL')
        url =f'get_file/{hashed_token}?search={file_name}'
        hashed_token = [hashed_token]
        
        

        return render_template('admin_token.html' ,data= hashed_token ,url= [url])
    
    return {'message' :'Please Login and generate token'}

@app.route('/admin/token',methods=['GET'])
def token_via_api():
    if request.method == 'GET':
        api_key = request.args.get('api')
        dt ,dt_bool = db.validate_api(api_key)
        if dt_bool:
            token = request.args.get('username')
            token_un = token
            if token:
                token +=str(randint(1,100000000))
            g = request.args.get('expirydate' ,'2099-06-04 10:42')
            file_name = request.args.get('filename')
            
            if len(g) == 0:
                g = '2099-06-04 10:42:00'
            # else:
            #     g= g.replace('T','')
            #     g+=':00'
            #print(g)
            cur_date = datetime.datetime.now() 
            token_created = cur_date.strftime('%Y-%m-%d %H:%M:%S')
            hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
            if file_name:
                db.insert_to_tokens(token_un , hashed_token ,token_created,g,file_name)
                url =f'get_file/{hashed_token}?search={file_name}'
                resp = jsonify({'token':hashed_token ,'expirydate' : g ,'url' : url})
                resp.status_code = 201

                return resp
            else:
                db.insert_to_tokens(token , hashed_token ,token_created,g,'ALL')
            
            
            
            resp = jsonify({'token':hashed_token ,'expirydate' : g})
            resp.status_code = 201

            return resp
        
        return {'message': 'Invalid API Key'}


@app.route('/login/admin',methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        email = request.form.get('email')
        session['email'] = 'reddy'
        password = request.form.get('password')
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        val ,val_bool = db.admin_validate(email, hashed_password)
        #print(val)
        if val_bool:
            return render_template('admin.html' , gft='b_click' ,api=[val])
        return {'error' : 'Invalid password or Email'}
    return {'message' : 'Please Login'}


@app.route('/login/admin/logout' , methods=['GET', 'POST'])
def logout():
    print(request.form)
    if request.method == 'POST':
        session.pop('email')
        
        return redirect('/')
@app.route('/data/<token>', methods=['GET','POST'])
def file_upload(token):
    val ,val_bool= db.validate_token(token)
    #print(val)
    if val_bool:
        if val[-1]!='ALL':
            return {'message' : 'You are not allowed to upload'}
    #print(request.files,request.form)
    


    if 'file' not in request.files :
       # print(request.form ,request.data)
        file_data = json.loads(request.data.decode('utf-8'))
        data = file_data.get('content').encode('utf-8')
        
        file_name  = file_data.get('file_name')
        CLOUD_PROVIDER = file_data.get('Cloud')
        if file_name:
            file_name = file_name.replace(' ','_').replace(')','').replace('(','')
            exists , exists_bool = db.get_objects(file_name ,token)
            if exists_bool:
                file_name = datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")+'_'+file_name

            file_path = f'{token}/{file_name}'

        if CLOUD_PROVIDER.upper()=='GCP':
            bucket_name = GCP_Storage_Name
            upload_to_gcp( data , bucket_name ,file_path)
        elif CLOUD_PROVIDER.upper()=='AZURE':
            bucket_name= Azure_Storage_Name
            upload_to_azure( data , bucket_name ,file_path)
        else:
            bucket_name= AWS_BucketName
            upload_to_s3( data , bucket_name ,file_path)

        dt = {'cloud_type' : CLOUD_PROVIDER ,'file_name' : file_name ,'bucket_name' : bucket_name ,'token' : token ,'file_path':file_path}
        #print(dt)
        db.insert_to_filestorage(dt)
        if exists_bool:
            resp = jsonify({'message' : 'Data Successfully Uploaded' ,'File_Name_exits':'true' ,'Updated_File_name':file_name})
        else:
            resp = jsonify({'message' : 'uploaded successfully'})
        resp.status_code = 201
        return resp
    files = request.files.getlist('file')
    CLOUD_PROVIDER = request.form.get('CLOUD')
    if files:
        files = request.files.getlist("file")
        for file in files:
            file_name = secure_filename(file.filename).replace(' ','_').replace(')','').replace('(','')
            exists , exists_bool = db.get_objects(file_name ,token)
            if exists_bool:
                file_name =datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")+'_'+file_name
            file_path = f'{token}/{file_name}'
            if CLOUD_PROVIDER.upper()=='GCP':
                bucket_name =GCP_Storage_Name
                # p = Thread(target=upload_to_gcp, args=(file , bucket_name ,file_path))
                # p.start()

                upload_to_gcp( file , bucket_name ,file_path)
            elif CLOUD_PROVIDER.upper()=='AZURE':
                bucket_name= Azure_Storage_Name
                # p1 = Thread(target=upload_to_azure, args=(file , bucket_name ,file_path))
                # p1.start()
                upload_to_azure( file , bucket_name,file_path)
            else:
                bucket_name= AWS_BucketName
                # p2 = Process(target=upload_to_s3, args=(file , bucket_name ,file_path))
                # p2.start()
                upload_to_s3( file , bucket_name,file_path)

            dt = {'cloud_type' : CLOUD_PROVIDER ,'file_name' : file_name ,'bucket_name' : bucket_name,'token': token,
            'file_path' : file_path}
            #print(dt)
            db.insert_to_filestorage(dt)
        
        #file.save(filename)
        if exists_bool:
            resp = jsonify({'message' : 'Data successfully uploaded' ,'File_Name_exits':'true' ,'Updated_File_name':file_name})
        else:
            resp = jsonify({'message' : 'uploaded successfully'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message' : 'Failed to Upload File'})
        resp.status_code = 400
        return resp

	# check if the post request has the file part
@app.route('/list_files/<token>', methods=['GET', 'POST'])
def list_files(token):
    val ,val_bool= db.validate_token(token)
    if not val_bool:
        return {'message' : 'Token Missing or EXpired'}
    if val_bool and val[-1]=='ALL':
        
        data = db.get_all_files(token)
        if request.method == 'POST':
            return render_template('home.html', data=data ,list_data=['table_yes'])
        headers=['ID','Cloud_Type','FileName','UploadTime']
        fi = []
        for de in data:
            fi.append(zip(headers, de))
        return {'data' : fi}
    pass
@app.route('/get_file/<token>' , methods=['GET'])

def get_file(token):
    val ,val_bool= db.validate_token(token)
    if not val_bool:
        return {'message' : 'Token Missing or EXpired'}
    
    #print(val)
    if val_bool and val[-1]=='ALL':
        #print(request.args)
        file_name = request.args.get('search')
        if file_name:
            file_name = file_name.replace(' ','_').replace(')','').replace('(','')

        dte ,dte_bool = db.validate_file_get_cloud_type(file_name ,token)
        #print(dte)
        
        if dte_bool:
            cloud_type = dte[1]
            bucket_name = dte[3]
            file_path = dte[2]
            if cloud_type.upper()=='AWS':
                file = download_from_s3(bucket_name, file_path)
            elif cloud_type.upper()=='GCP':
                file = download_from_gcp(bucket_name, file_path)
            else:
                file = download_from_azure(bucket_name, file_path)


            return Response(file,  headers={"Content-disposition":
                        f"attachment; filename={file_name}"})
        else:
            return {'message': 'File not found in any cloud'}

    file_name = request.args.get('search')
    if file_name:
        file_name = file_name.replace(' ','_').replace(')','').replace('(','')

    if val_bool and val[-1]==file_name:
        dte ,dte_bool = db.validate_file_get_cloud_type(file_name ,token)
    
        if dte_bool:
            cloud_type = dte[1]
            bucket_name = dte[3]
            file_path = dte[2]
            if cloud_type.upper()=='AWS':
                file = download_from_s3(bucket_name, file_path)
            elif cloud_type.upper()=='GCP':
                file = download_from_gcp(bucket_name, file_path)
            else:
                file = download_from_azure(bucket_name, file_path)


            return Response(file,  headers={"Content-disposition":
                        f"attachment; filename={file_name}"})
        else:
            return {'message': 'File not found in any cloud'}
    else:
        return {'message':'Not authorized for this file'}

    

if __name__ == "__main__":
    app.run(debug=True)