import os
from dotenv import load_dotenv 

from services import (
  fetch_file_content_from_bucket,
  upload_file_to_bucket,
  get_files_to_transform,
  get_json_object,
)

load_dotenv(verbose=True)

CLIENT_S3_BUCKET = os.getenv('clients_xml_bucket')
JSON_S3_BUCKET = os.getenv('app_json_bucket')


def transform_file(file_key):
  # read xml content from the s3 bucket
  xml_content = fetch_file_content_from_bucket(
    bucket_name=CLIENT_S3_BUCKET,
    s3_filename=file_key
  )

  # convert to JSON
  json_object = get_json_object(xml_content)

  # upload the JSON content to s3 bucket
  upload_file_to_bucket(
    bucket_name=JSON_S3_BUCKET,
    file_key=file_key + '.json',
    data=json_object,
  )



def handle_data_transform():
  """ Handles the transformation of the files"""
  files_to_transform = get_files_to_transform(
    bucket_name=CLIENT_S3_BUCKET
  )
  for file_key in files_to_transform:
    transform_file(file_key=file_key)

