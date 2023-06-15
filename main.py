import requests
from moto import mock_s3
import boto3
import os
from utils import aws_credentials, read_field_locations
import logging
import colorlog
import concurrent.futures
import time
import botocore

log = logging.getLogger("NASA API Test")
log.setLevel(logging.DEBUG)
log_file_name = f"log.txt"

if os.path.exists(log_file_name):
    os.remove(log_file_name)
fileHandler = logging.FileHandler(log_file_name)
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
)
log.addHandler(handler)
log.addHandler(fileHandler)


@mock_s3
class SatelliteFieldMonitor:
    def __init__(self, bucket_name, base_url):
        self.api_key = os.environ["NASA_API_KEY"]
        self.bucket_name = bucket_name
        self.base_url = base_url

    def get_image(self, params):
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            log.info(f"Image found: lon:{params['lon']}, lat:{params['lat']}, date: {params['date']}. Uploading it.")
            return response.content
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                log.info(f"Image not found: lon:{params['lon']}, lat:{params['lat']}, date: {params['date']}. Skipping "
                         f"it.")
            else:
                log.info(f"API request failed with status code: {e.response.status_code}")
            return None
        except requests.exceptions.ConnectionError as e:
            log.info(f"Connection error occurred: {e}")
            return None
        except requests.exceptions.Timeout as e:
            log.info(f"Timeout error occurred: {e}")
            return None
        except requests.exceptions.RequestException as e:
            log.info(f"An error occurred during the API request: {str(e)}")
            return None

    def pooling_images(self, filed_locations, date, s3_client):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for field_id, lat, lon, dim in filed_locations:
                params = {
                    'lon': lon,
                    'lat': lat,
                    'date': date,
                    'dim': dim,
                    'api_key': self.api_key
                }
                future = executor.submit(self.get_image, params)
                futures.append((future, field_id))

            for future, field_id in futures:
                response_content = future.result()
                if response_content:
                    self.upload_image(response_content, date, field_id, s3_client)

    def get_images(self, date, field_locations):
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
            )
            new_bucket = s3_client.create_bucket(Bucket=self.bucket_name)
            self.pooling_images(field_locations, date, s3_client)
            return new_bucket
        except Exception as e:
            log.info(f'During get_images: {str(e)}')

    def upload_image(self, response, date, field_id, s3_client):
        output_key = f"{field_id}/{date}_imagery.png"
        try:
            response_put = s3_client.put_object(
                Body=response,
                Bucket=self.bucket_name,
                Key=output_key
            )
            self.verify_upload(output_key, s3_client)
            return response_put
        except Exception as e:
            log.info(f'An error occurred during image upload: {str(e)}')
            return None

    def verify_upload(self, output_key, s3_client):
        try:
            s3_client.head_object(Bucket=self.bucket_name, Key=output_key)
            log.info(f'Verifying if file was uploaded correctly...')
            log.info(f'File {output_key} exists in S3 bucket {self.bucket_name}')
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                log.info(f'ERROR 404: File {output_key} does not exists in S3 bucket {self.bucket_name}')
            return False
        except Exception as e:
            log.info(f'Non-related ClientError occurred: {str(e)}')
            return False


def main():  # pragma: no cover

    # aws_credentials() # No docker initialization of variables.

    csv_input_file = os.environ["CSV_INPUT_FILE"]
    destination_bucket = os.environ["DESTINATION_BUCKET"]
    base_url = os.environ["BASE_URL"]
    field_date = os.environ["FIELD_DATE"]

    field_locations = read_field_locations(csv_input_file)
    monitor = SatelliteFieldMonitor(destination_bucket, base_url)

    start = time.time()
    monitor.get_images(field_date, field_locations)
    end = time.time()
    log.info(f"Time performance {end - start} seconds")


if __name__ == "__main__":  # pragma: no cover
    main()
