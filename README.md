## Satellite field monitoring

This report presents the findings and implementation details of a satellite field monitoring project. 

The objective of this assignment was to develop a daily process utilizing public NASA imagery from the Landsat 8 constellation to monitor a list of fields. 

The process was implemented using Python, leveraging the capabilities of the Earth API and Amazon S3 storage. This report outlines the key aspects of the process, including the retrieval of imagery, data organization, and storage in an S3 bucket.

### Run Dockerfiles:

Example (Make sure to use specific NASA_API_KEY and not `DEMO_KEY`):
```commandline
sudo docker build -t hevam_test .

sudo docker run \
--env FIELD_DATE=2017-06-14 \
--env CSV_INPUT_FILE=data/fields_location_6.csv \
--env DESTINATION_BUCKET=FIELD_MONITORING \
--env AWS_ACCESS_KEY_ID=testing \
--env AWS_SECRET_ACCESS_KEY=testing \
--env BASE_URL=https://api.nasa.gov/planetary/earth/imagery \
--env NASA_API_KEY=DEMO_KEY \
-v $(pwd):/app hevam_test
```

Usage:
```commandline
sudo docker build -t hevam_test .

sudo docker run \
--env FIELD_DATE=<date> \
--env CSV_INPUT_FILE=<path-to-input-csv-file.csv> \
--env DESTINATION_BUCKET=<name-of-s3-bucket> \
--env AWS_ACCESS_KEY_ID=<aws-access-key> \
--env AWS_SECRET_ACCESS_KEY=<aws-secret-access-key> \
--env BASE_URL=https://api.nasa.gov/planetary/earth/imagery \
--env NASA_API_KEY=<nasa-api-key> \
-v $(pwd):/app hevam_test
```

### Tests:

Example:
```commandline
sudo docker build -f Dockerfile.test -t mytestimage .

sudo docker run \
--env FIELD_DATE=2017-06-14 \
--env CSV_INPUT_FILE=data/fields_location_6.csv \
--env DESTINATION_BUCKET=FIELD_MONITORING \
--env AWS_ACCESS_KEY_ID=testing \
--env AWS_SECRET_ACCESS_KEY=testing \
--env BASE_URL=https://api.nasa.gov/planetary/earth/imagery \
--env NASA_API_KEY=DEMO_KEY \
-v $(pwd):/app mytestimage
```

Usage:
```commandline
sudo docker build -f Dockerfile.test -t mytestimage .

sudo docker run \
--env FIELD_DATE=<date> \
--env CSV_INPUT_FILE=<path-to-input-csv-file.csv> \
--env DESTINATION_BUCKET=<name-of-s3-bucket> \
--env AWS_ACCESS_KEY_ID=<aws-access-key> \
--env AWS_SECRET_ACCESS_KEY=<aws-secret-access-key> \
--env BASE_URL=https://api.nasa.gov/planetary/earth/imagery \
--env NASA_API_KEY=<nasa-api-key> \
-v $(pwd):/app mytestimage
```


### Implementation Overview

The retrieved images are then organized and stored in an Amazon S3 bucket, adhering to a specific folder structure. Each field's imagery is stored within its respective folder, identified by the field_id, and further categorized by the date of acquisition.
The final image files are saved in the PNG format and labeled as {date}_imagery.png.

The code is structured as a Python class called `SatelliteFieldMonitor`, which encapsulates the necessary functionality for interacting with the NASA Earth API and Amazon S3. Here's a summary of the key components and steps involved in the implementation:

1. **Setup and Configuration:**
   - The code begins by importing necessary libraries such as `requests`, `moto`, `boto3`, `os`, and custom utility modules.
   - Logging is configured to provide informative output and save log entries in a file.
   - The `SatelliteFieldMonitor` class is defined and initialized with the provided bucket name and the base URL for the NASA Earth API.

2. **Retrieving and Storing Images:**
   - The `get_images` method is responsible for downloading the available satellite images for each field on a specific date.
   - For each field, a request is made to the NASA Earth API with the appropriate parameters, including latitude, longitude, date, dimensions, and API key.
   - If the response is successful, the image content is uploaded to the specified Amazon S3 bucket using the `upload_image` method.
   - The `upload_image` method saves the image content to the S3 bucket with a specific key based on the field ID and date.

3. **Verification and Error Handling:**
   - After uploading an image, the `verify_upload` method checks if the file exists in the S3 bucket using the `head_object` method.

### Results:

Time performance, 5 samples per experiment (averaged):

| num_fields | average_time (sec) (concurrency/no concurrency) |
|:----------:|:-----------------------------------------------:|
|     6      |                  12.49 / 29.29                  |
|     12     |                  11.26 / 29.41                  |
|     24     |                  19.93 / 48.96                  |
|     48     |                 27.65 / 118.44                  |

By utilizing concurrent execution, multiple API requests and image uploads can happen simultaneously, resulting in improved performance for processing a large number of fields.

### Test Coverage Report:
The table below provides an overview of the test coverage for the codebase:

|     Name     | Stmts | Cover | Miss |     Missing      |
|:------------:|:-----:|:-----:|:----:|:----------------:|
|  config.py   |   0   | 100%  |  0   |                  |
|   main.py    |  87   |  93%  |  6   | 85, 97-98, 124-126 |
| test_main.py |  83   | 100%  |  0   |                  |
|test_utils.py |  13   | 100%  |  0   |                  |
|   utils.py   |  19   | 100%  |  0   |                  |
|  **TOTAL**   |  202  |  97%  |  6   |                  |

The coverage analysis reveals that the overall test coverage for the codebase is 97%. This coverage includes both the test files and non-test files. Notably, the coverage for the non-test files is over 96%.

## Part 2: Infrastructure

Possible cloud architecture to run this process on a daily basis could involve the following components:

1. AWS Lambda:
   - Configure an AWS Lambda function to run daily at the Python process or Docker on a scheduled basis using a scheduled event (e.g., AWS CloudWatch Events).
   - Set up the necessary environment variables for AWS access keys, S3 bucket name, NASA API key and date.

2. AWS S3:
   - Set up appropriate permissions and access control to the S3 bucket, ensuring the Lambda function has the necessary permissions to write objects to the bucket.

3. NASA Earth API:
   - Obtain an API key from NASA Earth API (https://api.nasa.gov) to access the satellite imagery.
   - Requests and downloads the available images for the specified date and field locations.

4. CSV File Storage:
   - Store the CSV file containing the field locations in a suitable location, such as an S3 bucket or a database.
   - Ensure that the Python process or Docker can access and read the CSV file to retrieve the field locations.

5. Logging and Monitoring:
   - Created logins can be stored in a dedicated location for easy monitoring and troubleshooting.

![plot_infras.png](data%2Fplot_infras.png)