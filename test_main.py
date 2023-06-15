import os
import boto3
import requests
import responses
from moto import mock_s3
from main import SatelliteFieldMonitor
# from utils import aws_credentials
# aws_credentials()


@mock_s3
def test_get_image_success():
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=os.environ['DESTINATION_BUCKET'])
    s3_client.put_object(Bucket=os.environ['DESTINATION_BUCKET'], Key='test.jpg', Body=b'Mock Image Content')
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    params = {
        'lon': 45,
        'lat': 24,
        'date': os.environ['FIELD_DATE'],
        'dim': 0.32,
        'api_key': os.environ['NASA_API_KEY']
    }
    response = monitor.get_image(params)
    assert isinstance(response, (bytes, bytearray))


def test_get_image_http_error():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    params = {
        'lon': 54,
        'lat': -12,
        'date': os.environ['FIELD_DATE'],
        'dim': 0.06,
        'api_key': os.environ['NASA_API_KEY']
    }
    response = monitor.get_image(params)
    assert response is None


@responses.activate
def test_upload_image_connection():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])

    params = {
        'lon': 54,
        'lat': -12,
        'date': os.environ['FIELD_DATE'],
        'dim': 0.06,
        'api_key': os.environ['NASA_API_KEY']
    }
    responses.get(
        url=os.environ['BASE_URL'],
        body=requests.ConnectionError(None)
    )
    assert monitor.get_image(params) is None


@responses.activate
def test_upload_image_timeout():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])

    params = {
        'lon': 54,
        'lat': -12,
        'date': os.environ['FIELD_DATE'],
        'dim': 0.06,
        'api_key': os.environ['NASA_API_KEY']
    }
    responses.get(
        url=os.environ['BASE_URL'],
        body=requests.Timeout(None)
    )
    assert monitor.get_image(params) is None


@responses.activate
def test_upload_image_request_exception():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])

    params = {
        'lon': 54,
        'lat': -12,
        'date': os.environ['FIELD_DATE'],
        'dim': 0.06,
        'api_key': os.environ['NASA_API_KEY']
    }
    responses.get(
        url=os.environ['BASE_URL'],
        body=requests.RequestException(None)
    )
    assert monitor.get_image(params) is None


@mock_s3
def test_verify_upload():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=os.environ['DESTINATION_BUCKET'])
    output_key = 'my_file.txt'
    s3_client.put_object(Bucket=os.environ['DESTINATION_BUCKET'], Key=output_key, Body=b'Test content')
    ver_res = monitor.verify_upload(output_key, s3_client)
    assert ver_res is True


@mock_s3
def test_verify_upload_not_found():
    # We don't upload the file but check if it is there ie 404
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=os.environ['DESTINATION_BUCKET'])
    output_key = 'my_file.txt'
    ver_res = monitor.verify_upload(output_key, s3_client)
    assert ver_res is False


@mock_s3
def test_upload_image():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=os.environ['DESTINATION_BUCKET'])
    response = b'Test content'
    date = '2023-06-15'
    field_id = '123'
    response_upload = monitor.upload_image(response, date, field_id, s3_client)
    assert response_upload.get('ResponseMetadata').get('HTTPStatusCode') == 200


def test_get_images():
    date = '2023-06-15'
    field_locations = [['1235', ' 100', ' 123', ' 0.025'], ['1341', ' 32', ' 15', ' 0.12']]
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    new_bucket = monitor.get_images(date, field_locations)
    assert new_bucket.get('ResponseMetadata').get('HTTPStatusCode') == 200


@mock_s3
def test_upload_image_error():
    monitor = SatelliteFieldMonitor(os.environ['DESTINATION_BUCKET'], os.environ['BASE_URL'])
    s3_client = boto3.client('s3')
    response = b'Test content'
    date = '2023-06-15'
    field_id = '123'
    response_upload = monitor.upload_image(response, date, field_id, s3_client)
    assert response_upload is None
