# Bestseller - eCommerce

## The architecture 
The architecture of this transformer app is simple.
I built it to check for uploaded files and to check the `clients_xml_bucket` on **AWS s3** for uploads every `number_of_hours` set on the app or 3 hours, if `number_of_hours` is not set. 3 hours because the client is expected to upload files at least 8 times in every 24 hours. 3 hours would also give enough time for the app to finish processing the files before the next check for uploads.


**The Converter** class is responsible for the conversion of XML data to JSON data, based on the required JSON format in the problem definition document.


The **handle_data_transform** function is responsible for fetching the client's uploads within the last `number_of_hours`. it goes through the list of files, downloading, converting to json and uploading them to the given `app_json_bucket` on **AWS s3**.

![the flow for the system](https://res.cloudinary.com/teamhaven/image/upload/v1613888641/png.png)

## Running the app (locally)
The app runs in a Flask server, with a chron job that runs after each `number_of_hours`. The cron job gets terminated when the server is stopped.

### Add your AWS credentials the `.env`
the sample credentials are in the `.env.example` file

### Starting app via docker-compose

```bash
docker-compose up --build 
```

## Running test
You can run test locally by starting up localstack and running the command below at the root folder

```bash
pytest src/tests.py
```

## Deploying to Production
On AWS EC2, the app can be deployed using any WSGI web server setup like gunicorn.

The app needs to be running first before the clients start uploading the files to the bucket.

## Previous architectural consideration
This was the previous architecture that I had contemplated. It involves listening for upload event and triggering the conversion process with it. I designed it to implement a queue which caters for situations where the client uploads multiple files at once. I love this architecture because the app does work only when it needs too.

![the former flow for the system](https://res.cloudinary.com/teamhaven/image/upload/v1613113741/bestseller-challenge.png)

## Considerations or future improvements
In event of the app turning off, there is currently no way to go back and get all the files that the client must have uploaded before the app shut down. This is something that can come in as a future improvement to make the app more robust
