import os
import boto3

import localstack_client.session
from dotenv import load_dotenv 

from services import upload_file_to_bucket, make_bucket

load_dotenv(verbose=True)

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

s3_resource = session.resource('s3')
s3_client = session.client(
  service_name="s3",
  region_name=aws_region,
  endpoint_url="http://localhost:4566",
  verify=False,
  aws_access_key_id = aws_access_key_id,
  aws_secret_access_key=aws_secret_access_key
)

file_key = 'test-file.xml'
file = open(f'src/uploads/{file_key}', "r")

def init():
  """Initialize the environment for development and test"""
  make_bucket(s3_client, CLIENT_S3_BUCKET)
  make_bucket(s3_client, JSON_S3_BUCKET)

  upload_file_to_bucket(
    s3_connection=s3_resource,
    bucket_name=CLIENT_S3_BUCKET,
    file_key= file_key,
    data=file.read()
  )

