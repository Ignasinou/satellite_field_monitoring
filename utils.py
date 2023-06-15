import os
import csv
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, NASA_API_KEY, FIELD_DATE, CSV_INPUT_FILE, \
    DESTINATION_BUCKET, NASA_API_KEY, BASE_URL


def read_field_locations(csv_input_file):
    field_locations = []
    with open(csv_input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            field_locations.append(row)
    return field_locations


def aws_credentials():
    os.environ["FIELD_DATE"] = FIELD_DATE
    os.environ["CSV_INPUT_FILE"] = CSV_INPUT_FILE
    os.environ["DESTINATION_BUCKET"] = DESTINATION_BUCKET
    os.environ["AWS_ACCESS_KEY_ID"] = AWS_ACCESS_KEY_ID
    os.environ["AWS_SECRET_ACCESS_KEY"] = AWS_SECRET_ACCESS_KEY
    os.environ["NASA_API_KEY"] = NASA_API_KEY
    os.environ["BASE_URL"] = BASE_URL
