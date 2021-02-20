import os
import logging
import boto3
import json
import localstack_client.session

from dotenv import load_dotenv 
from datetime import datetime, timedelta
from dateutil import parser
from bs4 import BeautifulSoup



load_dotenv(verbose=True)

logging.basicConfig(
    filename='src/logs/app.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

is_not_production = os.getenv('env') != 'production'
number_of_hours = os.getenv('number_of_hours', 3)

aws_access_key_id=os.getenv('aws_access_key_id')
aws_secret_access_key=os.getenv('aws_secret_access_key')
aws_region = os.getenv('aws_region')

CLIENT_S3_BUCKET = os.getenv('clients_xml_bucket')
JSON_S3_BUCKET = os.getenv('app_json_bucket')

is_not_production = os.getenv('env') != 'production'


def aws_session(region_name=aws_region):
    return boto3.session.Session(
      aws_access_key_id,
      aws_secret_access_key,
      region_name=region_name
    )

def local_aws_session(region_name=aws_region):
    return localstack_client.session.Session(
      aws_access_key_id,
      aws_secret_access_key,
      region_name=region_name,
    )

session = aws_session()
if is_not_production:
  session = local_aws_session()


class Converter():
    def get_images(self, images):
        result = {}
        max_type = 1
        images_dict = {}
        for image in images:
            current_type = int(image.get('type'))
            if max_type < current_type:
                max_type = current_type
                images_dict[current_type] = image.get('url')
        for i in range(1, (max_type + 1)):
            key = 'image_' + str(i)
            if images_dict.get(i, None):
                result[key] = images_dict[i]
            else:
                result[key] = None
        return result


    def get_prices(self, prices):
        result = []
        for price in prices:
            result.append({
            'currency': price.currency.contents[0],
            'value': price.value.contents[0],
            })
        return result
    

    def get_item_element(self, item):
        images = self.get_images(item.findAll('image'))
        prices = self.get_prices(item.findAll('price'))
        
        result = {
            "product_id": item.get('id'),
            "product_category": item.category.contents[0],
            "product_description": item.description.contents[0],
            "product_images": images,
            "prices": prices
        }
        return result


    def convert_xml_to_json(self, Parser, xml_data):
        """Convert XML to JSON using the Parser"""
        xml_parser = Parser(xml_data, 'xml')
        result = []
        for item in xml_parser.findAll('item'):
            result.append(self.get_item_element(item))
        return json.dumps(result)


def upload_file_to_bucket(s3_connection=None, bucket_name=None, file_key=None, data=None):
    """Upload file to an s3 bucket"""
    try:
        if not s3_connection:
            s3_connection = session.resource('s3')
        bucket = s3_connection.Bucket(bucket_name)
        bucket.put_object(
            Key=file_key,
            Body=data,
        )
        s3_connection.ObjectAcl(bucket_name, file_key).put(ACL='public-read')

        s3_url = f'https://{bucket_name}.s3.amazonaws.com/{file_key}'
        if is_not_production:
            s3_url = f'http://localhost:4566/{bucket_name}/{file_key}'

        return s3_url
    except Exception as e:
        logging.error(f'Error while uploading {file_key} to {bucket_name} bucket', exc_info=True)


def download_file_from_bucket(s3_connection=None, bucket_name=None, file_key=None):
    """Download files from s3 bucket"""
    try:
        if not s3_connection:
            s3_connection = session.resource('s3')

        object = s3_connection.Object(bucket_name, file_key)
        object.download_file(f'src/downloads/{file_key}')
    except Exception as e:
        logging.error(f'Error while downloading {file_key} from {bucket_name} bucket', exc_info=True)


def fetch_file_content_from_bucket(s3_connection=None, bucket_name=None, file_key=None):
    if not s3_connection:
        s3_connection = session.resource('s3')

    """Fetch the content of the file without downloading it"""
    try:
        return s3_connection.Object(bucket_name, file_key).get()['Body'].read()
    except Exception as e:
        logging.error(f'Error while reading {file_key} from {bucket_name} bucket', exc_info=True)

def get_files_to_transform(s3_connection=None, bucket_name=None):
    """Get the list of files to be transformed from the customer's bucket"""
    if not s3_connection:
        s3_connection = session.resource('s3')

    try:
        bucket = s3_connection.Bucket(bucket_name)
        objects = bucket.objects.all()

        last_download_time = datetime.utcnow() - timedelta(hours=int(number_of_hours))

        files_to_download = []
        for obj in objects:
            if is_not_production:
                files_to_download.append(obj.key)
            # collect files that are less than three hours old for production
            elif parser.parse(obj.last_modified) > last_download_time:
                files_to_download.append(obj.key)

        return  files_to_download
    except Exception as e:
        logging.error(f'Error getting file keys from {bucket_name} bucket', exc_info=True)


def get_json_object(xml_data):
    """Convert an XML content to JSON content"""
    try:
        converter = Converter()
        return converter.convert_xml_to_json(BeautifulSoup, xml_data)
    except Exception as e:
        logging.error(f'Error converting the XML data to JSON', exc_info=True)


def make_bucket(s3_connection=None, bucket_name=None, acl='public-read'):
    try:
        if not s3_connection:
            s3_connection = session.resource('s3')

        response = s3_connection.create_bucket(Bucket=bucket_name, ACL=acl)
        return response
    except Exception as e:
        logging.error(f'Error creating the bucket - {bucket_name}', exc_info=True)

