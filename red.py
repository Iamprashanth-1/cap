# gg ='dd'
# f = gg.replace(' ','_').replace(')','').replace('(','')

# print(f)

# k='ser.pkl;pnh.kl'
# p=k.split(';')
# print(p)

# g= ['gg','ii','ll']

# p=[(1,2,3,44),(45,6,7)]
# fi=[] 
# for i in p:
#     fi.append(dict(zip(g,i)))
# print(fi)
# import uuid
# print( uuid.uuid4().hex)

# import datetime
# dd  = datetime.datetime.now()
# f= dd.strftime("%Y-%m-%d%H:%M:%S")
# jj = 'hi'+f
# print(type(f),f,jj)
import random
from random import randint
l = random.randint(1,100000000)
print(l)

import boto3 ,json
s3 = boto3.client('s3')
result = s3.list_objects(Bucket='objectinfo',Prefix='32ad3682eba13d9c192d9f6e6b3d5689fc1fed88356d2665290d7ddf6fd840f1/')
for item in result['Contents']:
    print(item)
    if item['Key'] == 'blah.txt':
        print('lyr')
# s3_object = s3.get_object(Bucket='airbuss3bucket', Key='cloud_agnostic/cred.json')
# s = s3_object['Body'].read()
# j = json.loads(s)
# print(j.get('postgres_credentials'))
# #print(s)
#import hashlib
#ggg = hashlib.sha512('abcd###'.encode('utf-8')).hexdigest()
#print(ggg)