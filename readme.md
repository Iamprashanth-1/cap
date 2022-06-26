# Documention

### Postman Collection Details
- https://documenter.getpostman.com/view/19885814/UzBsGjHs
### How to Run in Local Environment
- Install Python 3 from https://www.python.org/downloads/
- Clone the Repository
- Run this command to install dependencies

    ```bash
    pip install -r requirements.txt
    ```
- Make sure aws credentials are configured if not use below command to configure
    ```bash
    aws configure --profile 'profileName'
    ```
    Or Add   `ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in config.py
    
- Add all credentials in cred.json file see sample file on current working directory
    - Upload cred.json to s3 bucket
    - Look for config.py file and replace the bucket name and path for cred.json file

    - We can use Secret Manager to fetch credentials but it cost's so we are using s3 to fetch credentials
    - Credentials were retrieved in run time Environment so there are no hardcoded credentials available in project

- Run this command to test in local environment : 
    ```bash
    python app.py
    ```
### Platform Flow   
- ![alt text](https://github.com/Iamprashanth-1/cap/blob/main/images/overall_flow.png)
### User Flow  
- ![alt text](https://github.com/Iamprashanth-1/cap/blob/main/images/flow.png)

### Schema  
- ![alt text](https://github.com/Iamprashanth-1/cap/blob/main/images/schema.png)


### Super Admin Access
- Use this api to create admin credentials
    - If credentials are generated using UI please route to below endpoint
        - Example : http://127.0.0.1:5000/super_admin
        - P.S Enter token that was configured in cred.json file
    - Else use this api to create admin credentials
        - Example : http://127.0.0.1:5000/super_admin/register  (Request-Type : POST)
            - Form parameters keys :
                - email : 
                - password : 
                - token :

### Admin Access

- Use Api key to generate token for User access
    - If User want's Full access    (Request-Type : GET)
        - Example :  http://127.0.0.1:5000/admin/token?api=qasedddf&username=abcd

- If User want's Limited access with expiry time (Request-Type : GET)
  -  Example : http://127.0.0.1:5000/admin/token?api=qasedddf&username=abcd&expirydate=2023-06-04 10:42:00

- If User want's Limited access with single file access with expiry time (Request-Type : GET)
    - Example : http://127.0.0.1:5000/admin/token?api=qasedddf&username=abcd&expirydate=2023-06-04 10:42:00&filename=temp.jpg

### User's Access

- If User want's to Upload a file  (Request-Type : POST)
    - Use Below Cloud-Provider Key Names For Uploading Files :
        * Amazon web Services(AWS)  : AWS
        * Google cloud provider(GCP) : GCP
        * Azure cloud provider(Azure) : Azure

    - Example :  http://127.0.0.1:5000/data/token  
                Use form to post request

                 parameters : {'CLOUD' :  , 'file':  }
     - Choose respective file for key-value 'file' 

        ( This Image is Just for reference copied from Internet)
    - ![alt text](https://i.stack.imgur.com/GGm4I.png)



- If User want's to download a file (Request-Type : GET)
    - Example : http://127.0.0.1:5000/get_file/token?search=temp.txt

- If User want's to list files that are Uploaded (Request-Type : GET)
    - Example : http://127.0.0.1:5000/list_files/token

## Programmatic Access

- ### Python 3

    - To Upload a file use the snippet below
        ```
        import requests

        url = "http://127.0.0.1:5000/data/6bf9d290957e02a187926cffbfe2bea0af7c56b2161bdda73ee9f5fe9c1666e1"

        payload={}
        files=[
        ('file',('Capture.JPG',open('/C:/Users/Prashanth Reddy/Downloads/Capture.JPG','rb'),'application/octet-stream'))
        ]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        print(response.text)
            

        ```
    - To Download a file use the snippet below
        ```
        import requests
        ResultUrl = ''
        resp = requests.get(ResultUrl)
        print(resp.text)
        ```


- ### Java

    - To Upload a file use the snippet below :

        ```
        OkHttpClient client = new OkHttpClient().newBuilder()
            .build();
            MediaType mediaType = MediaType.parse("text/plain");
            RequestBody body = new MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart("file","Capture.JPG",
                RequestBody.create(MediaType.parse("application/octet-stream"),
                new File("/C:/Users/Prashanth Reddy/Downloads/Capture.JPG")))
            .addFormDataPart("CLOUD","GCP")
            .build();
            Request request = new Request.Builder()
            .url("http://127.0.0.1:5000/data/6bf9d290957e02a187926cffbfe2bea0af7c56b2161bdda73ee9f5fe9c1666e1")
            .method("POST", body)
            .build();
            Response response = client.newCall(request).execute();
        ```
    - To Download a file use the snippet below:
        ```
        OkHttpClient client = new OkHttpClient().newBuilder()
        .build();
        MediaType mediaType = MediaType.parse("text/plain");
        RequestBody body = RequestBody.create(mediaType, "");
        Request request = new Request.Builder()
        .url("http://127.0.0.1:5000/get_file/6bf9d290957e02a187926cffbfe2bea0af7c56b2161bdda73ee9f5fe9c1666e1?search=Capture.JPG")
        .method("GET", body)
        .build();
        Response response = client.newCall(request).execute();
        ```

- ### C#
    - To Upload a file use the snippet below :

        ```
            var client = new RestClient("http://127.0.0.1:5000/data/6bf9d290957e02a187926cffbfe2bea0af7c56b2161bdda73ee9f5fe9c1666e1");
        client.Timeout = -1;
        var request = new RestRequest(Method.POST);
        request.AddFile("file", "/C:/Users/Prashanth Reddy/Downloads/Capture.JPG");
        request.AddParameter("CLOUD", "GCP");
        IRestResponse response = client.Execute(request);
        Console.WriteLine(response.Content);
        ```
    - To Download a file use the snippet below :
        ```
            var client = new RestClient("http://127.0.0.1:5000/get_file/6bf9d290957e02a187926cffbfe2bea0af7c56b2161bdda73ee9f5fe9c1666e1?search=Capture.JPG");
            client.Timeout = -1;
            var request = new RestRequest(Method.GET);
            IRestResponse response = client.Execute(request);
            Console.WriteLine(response.Content);
        ```