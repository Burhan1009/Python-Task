import os
import datetime
import shutil
import boto3
from pathlib import Path
from botocore.exceptions import NoCredentialsError

def filter_current_day_files(source_path):
    """
    Filters the files in the source directory to include only those related to today's date.
    """
    today = datetime.date.today().strftime('%Y_%m_%d')
    return [
        file for file in os.listdir(source_path)
        if today in file and file.endswith('.bak')
    ]

def create_backup(files, source_path, destination_path):
    """
    Copies the filtered files to the destination folder and creates a zip archive.
    """
    # Get today's date for the folder name
    date_name = datetime.date.today().strftime('%Y-%m-%d')
    backup_dir = os.path.join(destination_path, date_name)

    # Ensure the date-named directory exists
    os.makedirs(backup_dir, exist_ok=True)

    try:
        for file in files:
            source_file = os.path.join(source_path, file)
            destination_file = os.path.join(backup_dir, file)
            shutil.copy2(source_file, destination_file)
            print(f"Copied: {file} to {destination_file}")

        # Create a zip archive of the backup folder
        zip_file = shutil.make_archive(backup_dir, 'zip', backup_dir)
        print("Backup Complete..! Created zip archive.")
        return zip_file  # Return the zip file path
    except Exception as e:
        print(f"Error during backup creation: {e}")
        return None

def upload_to_s3(file_path, bucket_name, s3_folder, aws_access_key, aws_secret_key, region_name):
    """
    Uploads the zip file to the specified S3 bucket.
    """
    # Initialize the S3 client with region_name
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region_name
    )

    try:
        file_name = os.path.basename(file_path)
        s3_key = f"{s3_folder}/{file_name}"

        # Upload the zip file to the S3 bucket
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"File uploaded successfully to S3: {s3_key}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error during S3 upload: {e}")

# User-defined paths and credentials
source_path = Path(r"")  # Use a raw string
destination_path = Path(r"")

bucket_name = "managerpro"  # Replace with your S3 bucket name
s3_folder = datetime.date.today().strftime('%Y-%m-%d')  # Date-based folder in S3
aws_access_key = "***********"  # Replace with your AWS access key
aws_secret_key = "**************"  # Replace with your AWS secret key
region_name = "ap-southeast-2"  # Replace with your S3 bucket region

# Filter files for the current date
current_day_files = filter_current_day_files(source_path)

if current_day_files:
    # Create backup
    zip_file = create_backup(current_day_files, source_path, destination_path)

    # Upload to S3 if backup is successful
    if zip_file:
        upload_to_s3(zip_file, bucket_name, s3_folder, aws_access_key, aws_secret_key, region_name)
else:
    print("No files found for the current date.")
