# Documention
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
                - token

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
    - ![alt text](https://i.stack.imgur.com/GGm4I.png)



- If User want's to download a file (Request-Type : GET)
    - Example : http://127.0.0.1:5000/get_file/token?search='temp.txt'

- If User want's to list files that are Uploaded (Request-Type : GET)
    - Example : http://127.0.0.1:5000/list_files/token

## Programmatic Access

- ### Python 3

    - To Upload a file use the snippet below
        ```
        import requests
        filePath = "/Users/xxx.txt"
        uploadResultUrl = ''
        fileFp = open(filePath, 'rb')
        fileInfoDict = {
                "file": fileFp,
            }
        resp = requests.post(uploadResultUrl, files=fileInfoDict)
            

        ```
    - To Download a file use the snippet below
        ```
        import requests
        ResultUrl = ''
        resp = requests.get(ResultUrl)
        print(resp.data)
        ```


- ### Java

    - To Upload a file use the snippet below :

        ```
        CloseableHttpClient httpClient = HttpClients.createDefault();
        HttpPost uploadFile = new HttpPost("http://127.0.0.1:5000/data/token");
        MultipartEntityBuilder builder = MultipartEntityBuilder.create();
        builder.addTextBody("CLOUD", "AWS", ContentType.TEXT_PLAIN);

        // This attaches the file to the POST:
        File f = new File("[/path/to/upload]");
        builder.addBinaryBody(
            "file",
            new FileInputStream(f),
            ContentType.APPLICATION_OCTET_STREAM,
            f.getName()
        );

        HttpEntity multipart = builder.build();
        uploadFile.setEntity(multipart);
        CloseableHttpResponse response = httpClient.execute(uploadFile);
        HttpEntity responseEntity = response.getEntity();
        ```
    - To Download a file use the snippet below:
        ```
        GetMethod get = new GetMethod("http://httpcomponents.apache.org");
        
        InputStream in = get.getResponseBodyAsStream();
        
        get.releaseConnection();
        ```

- ### C#
    - To Upload a file use the snippet below :

        ```
        public UploadResult UploadFile(string  fileAddress)
        {
            HttpClient client = new HttpClient();

            MultipartFormDataContent form = new MultipartFormDataContent();
            HttpContent content = new StringContent("CLOUD");
            form.Add(content, "AWS");       
            var stream = new FileStream(fileAddress, FileMode.Open);            
            content = new StreamContent(stream);
            var fileName = 
            content.Headers.ContentDisposition = new ContentDispositionHeaderValue("form-data")
            {
                Name = "file",
                FileName = Path.GetFileName(fileAddress),                 
            };
            form.Add(fileName, content);
            HttpResponseMessage response = null;          

            var url = new Uri("http://127.0.0.1:5000/data/token");
            response = (client.PostAsync(url, form)).Result;          

        }
        ```
    - To Download a file use the snippet below :
        ```
            public async Task<string> GetAsync(string uri)
                {
                    HttpWebRequest request = (HttpWebRequest)WebRequest.Create(uri);
                    request.AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate;

                    using(HttpWebResponse response = (HttpWebResponse)await request.GetResponseAsync())
                    using(Stream stream = response.GetResponseStream())
                    using(StreamReader reader = new StreamReader(stream))
                    {
                        return await reader.ReadToEndAsync();
                    }
                }
        ```