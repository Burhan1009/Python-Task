# Backup and Upload Script

This Python script automates the process of filtering, backing up, compressing, and uploading SQL database backups to an Amazon S3 bucket. Below is a detailed explanation of the script's features and functionality.

## Features

1. **Filter Backup Files**:
   - Filters `.bak` files from a source folder that are related to the current day's date.
   - Ensures only relevant backup files are processed to avoid unnecessary uploads.

2. **Create Backup**:
   - Copies the filtered `.bak` files to a destination folder organized by date.
   - Compresses the backup files into a zip archive to save storage space and facilitate faster uploads.

3. **Upload to Amazon S3**:
   - Uploads the compressed zip archive to a specified Amazon S3 bucket under a folder named by the current date.
   - Handles errors such as missing credentials, file not found, or upload failure gracefully.

4. **Error Handling**:
   - Logs and displays any errors during the backup creation or upload process to ensure easy debugging.

---

## Code Breakdown

### Imports
```python
import os
import datetime
import shutil
import boto3
from pathlib import Path
from botocore.exceptions import NoCredentialsError
```
- `os`, `datetime`, and `shutil`: Used for file operations, date management, and compression.
- `boto3`: AWS SDK for Python to interact with Amazon S3.
- `Path`: Provides an easy-to-use interface for file paths.
- `NoCredentialsError`: Handles AWS credential errors.

### Filtering Files for the Current Date
```python
def filter_current_day_files(source_path):
    today = datetime.date.today().strftime('%Y_%m_%d')
    return [
        file for file in os.listdir(source_path)
        if today in file and file.endswith('.bak')
    ]
```
- Extracts the current date and matches files containing that date in their names.
- Filters files with a `.bak` extension.

### Creating Backup and Compressing
```python
def create_backup(files, source_path, destination_path):
    date_name = datetime.date.today().strftime('%Y-%m-%d')
    backup_dir = os.path.join(destination_path, date_name)
    os.makedirs(backup_dir, exist_ok=True)

    try:
        for file in files:
            source_file = os.path.join(source_path, file)
            destination_file = os.path.join(backup_dir, file)
            shutil.copy2(source_file, destination_file)
            print(f"Copied: {file} to {destination_file}")

        zip_file = shutil.make_archive(backup_dir, 'zip', backup_dir)
        print("Backup Complete..! Created zip archive.")
        return zip_file
    except Exception as e:
        print(f"Error during backup creation: {e}")
        return None
```
- Copies filtered files to a dated folder in the destination path.
- Compresses the folder into a zip archive using `shutil.make_archive()`.
- Returns the path to the zip file.

### Uploading to Amazon S3
```python
def upload_to_s3(file_path, bucket_name, s3_folder, aws_access_key, aws_secret_key, region_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region_name
    )

    try:
        file_name = os.path.basename(file_path)
        s3_key = f"{s3_folder}/{file_name}"
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"File uploaded successfully to S3: {s3_key}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Error during S3 upload: {e}")
```
- Initializes the Amazon S3 client with the provided credentials and region.
- Uploads the zip file to an S3 folder named by the current date.
- Handles exceptions to log any issues during the upload process.

### Main Logic
```python
source_path = Path(r"\\192.22.54.3\\DownloadandUpload2\\Burhan\\testingback")
destination_path = Path(r"D:\\backupfile\\destionationfile")

bucket_name = "managerpro"
s3_folder = datetime.date.today().strftime('%Y-%m-%d')
aws_access_key = "************************"
aws_secret_key = "*********************"
region_name = "ap-southeast-2"

current_day_files = filter_current_day_files(source_path)

if current_day_files:
    zip_file = create_backup(current_day_files, source_path, destination_path)
    if zip_file:
        upload_to_s3(zip_file, bucket_name, s3_folder, aws_access_key, aws_secret_key, region_name)
else:
    print("No files found for the current date.")
```
- Defines the source and destination paths for backup files.
- Sets up S3 bucket credentials and folder naming conventions.
- Filters files for the current date, creates a backup zip archive, and uploads it to S3.

---

## How to Use

1. **Setup**:
   - Update the `source_path` and `destination_path` with your local file paths.
   - Replace the `bucket_name`, `aws_access_key`, `aws_secret_key`, and `region_name` with your Amazon S3 credentials.

2. **Run the Script**:
   - Execute the script in a Python environment.
   - Ensure you have the necessary permissions for the specified paths and S3 bucket.

3. **Check Outputs**:
   - Verify the backup zip file in the destination folder.
   - Check the Amazon S3 bucket for the uploaded file.

---

## Dependencies
- **Python 3.6+**
- **boto3**: Install using `pip install boto3`.
- **AWS Credentials**: Ensure you have valid credentials with the necessary S3 permissions.

---

## Error Handling
- If no files are found for the current date, the script displays a message and exits.
- Errors during backup creation or S3 upload are logged to the console.

---

## Future Enhancements
- Add email notifications for successful backups or errors.
- Support for incremental backups to optimize storage and upload time.
- Add logging to a file for better traceability.

