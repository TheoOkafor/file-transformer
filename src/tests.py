import json
import boto3
import localstack_client.session
import pytest

from bs4 import BeautifulSoup

from .services import (
  fetch_file_content_from_bucket,
  get_files_to_transform,
  upload_file_to_bucket,
  make_bucket,
  Converter
)

file_key = 'test-file.xml'
file = open(f'src/uploads/{file_key}', "r")
data = file.read()

BUCKET_NAME = 'test-bucket'
FILE_KEY = 'test-file.xml'

def test_util_convert_xml_to_json():
  json_data = Converter().convert_xml_to_json(BeautifulSoup, data)
  products = json.loads(json_data)

  product = products[0]
  assert isinstance(products, list)
  assert len(products) == 2
  assert isinstance(product, dict)
  assert product['product_id'] == '2445456'


@pytest.fixture(autouse=True)
def boto3_localstack_patch(monkeypatch):
  session_ls = localstack_client.session.Session()
  monkeypatch.setattr(boto3, "client", session_ls.client)
  monkeypatch.setattr(boto3, "resource", session_ls.resource)


def test_make_bucket():
  s3_client = boto3.client('s3')
  response = make_bucket(s3_client, BUCKET_NAME)
  assert isinstance(response, dict)
  assert isinstance(response['ResponseMetadata'], dict)
  assert response['ResponseMetadata']['HTTPStatusCode'] == 200


def test_upload_file_to_bucket():
  s3_resource = boto3.resource('s3')
  s3_url = upload_file_to_bucket(s3_resource, BUCKET_NAME, FILE_KEY, data)
  assert s3_url == f'http://localhost:4566/{BUCKET_NAME}/{FILE_KEY}'


def test_fetch_file_content_from_bucket():
  s3_resource = boto3.resource('s3')

  # fetch the file from bucket
  xml_data = fetch_file_content_from_bucket(s3_resource, BUCKET_NAME, FILE_KEY)
  
  # convert to JSON and make assertions
  json_data = Converter().convert_xml_to_json(BeautifulSoup, xml_data)
  products = json.loads(json_data)

  product = products[0]
  assert isinstance(products, list)
  assert len(products) == 2
  assert isinstance(product, dict)
  assert product['product_id'] == '2445456'


def test_get_files_to_transform():
  s3_resource = boto3.resource('s3')
  files_to_download = get_files_to_transform(s3_resource, BUCKET_NAME)

  assert len(files_to_download) == 1

