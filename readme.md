# Documention

### Admin Access

- Use Api key to generate token for User access
    - If User want's Full access    (Request-Type : GET)
        - Example :  http://dns/admin/token?api='qasedddf'&username='abcd'

- If User want's Limited access with expiry time (Request-Type : GET)
  -  Example : http://dns/admin/token?api='qasedddf'&username='abcd'&expirydate='2099-06-04 10:42:00'

- If User want's Limited access with singfile access with expiry time (Request-Type : GET)
    - Example : http://dns/admin/token?api='qasedddf'&username='abcd'&expirydate='2099-06-04 10:42:00'&filename='temp.jpg'

### User's Access

- If User want's to Upload a file  (Request-Type : POST)
    - Use Below Cloud-Provider Key Names For Uploading Files :
        * Amazon web Services(AWS)  : AWS
        * Google cloud provider(GCP) : GCP
        * Azure cloud provider(Azure) : Azure

    - Example :  http://dns/data/token  
                * use form to post request

                 parameters : {'Cloud' :  ,'file_name' :  , 'content:  }



- If User want's to download a file (Request-Type : GET)
    - Example : http://dns/get_file/token?search='temp.txt'

- If User want's to list files that are Uploaded (Request-Type : GET)
    - Example : http://dns/list_files/token

- Flow 
- ![alt text](https://github.com/Iamprashanth-1/cap/blob/main/images/Untitled%20Diagram.drawio%20(1).png)
