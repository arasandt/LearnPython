"""
This function will perform csv split
"""
import urllib.parse
import logging
import os
from io import StringIO
import json
import uuid
import boto3
from datetime import datetime, timezone
from pathlib import Path
import emlpackage
from meaapi import MEA

from botocore.config import Config

LOGGER = logging.getLogger()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOGGER.setLevel(LOG_LEVEL)
LOGGER.info("Loading function with LOG_LEVEL set to %s", LOG_LEVEL)

S3_RESOURCE = boto3.resource("s3")
S3_CLIENT = boto3.client("s3")
SSM_CLIENT = boto3.client("ssm")


def split_s3_path(s3_path):
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)
    return bucket, key


def upload_to_s3_asfile(bucket, key, temporary_filename):
    """
    This function will upload file into s3
    """

    try:
        S3_CLIENT.upload_file(
            str(temporary_filename),
            bucket,
            str(key),
        )
        print(f"Upload successful from {temporary_filename} to {bucket}/{key}")
        Path.unlink(temporary_filename)
    except FileNotFoundError:
        print(f"{temporary_filename} was not found")
        raise error
    except Exception as error:
        print(f"Issue with {temporary_filename} upload to {bucket}/{key}")
        raise error
    return True


def from_ssm(path):
    """
    This function will return ssm value for parameter
    """
    # function to get parameters stored in ssm
    response = SSM_CLIENT.get_parameter(Name=path, WithDecryption=True)
    return response["Parameter"]["Value"]


def lambda_handler(event, context):
    """
    This is a main lambda handler function
    """
    mea_auth_token_name = "mea-token"
    mea_base_url = (
        "https://apiengine-accenture-demo-us-east-2.meaplatform.com/rest/api/v1"
    )
    email_extract_bucket = "cip-uw-email-extract-dev"
    client_identifier = from_ssm("/cip/uw/customeridentifier")
    temp_directory = "/tmp"

    mea_api_credential = from_ssm("/cip/uw/mea/cipapicredential")
    mea_api_credential = json.loads(mea_api_credential)
    mea = MEA(mea_api_credential["clientid"], mea_base_url)

    for record in event["Records"]:
        if isinstance(record["body"], str):
            message = json.loads(record["body"])
        else:
            message = record["body"]

        if isinstance(message["Message"], str):
            entry = json.loads(message["Message"])
        else:
            entry = message["Message"]

        print(f"Received Message : {entry}")

        subject = entry["subject"]
        attachments = entry["attachments"]
        application_id = entry["application_id"]
        lob = entry["lob"]

        local_attachments = []

        for attach in attachments:
            bucket, key = split_s3_path(attach)
            eml_key = Path(key).parent
            attachment_name = Path(key).name
            try:
                s3_object = S3_RESOURCE.Object(bucket, key)
                local_file = str(Path(temp_directory).joinpath(attachment_name))
                s3_object.download_file(local_file)
                local_attachments.append(local_file)
                print(f"Downloaded {attach} to {local_file}")
            except Exception as error:
                print(
                    "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                        key, bucket
                    )
                )
                raise error

        # Overriding subject to prevent unnecessary characters from to fail in MEA
        # subject = application_id
        eml_file_path = emlpackage.create_eml(
            local_attachments, temp_directory, subject
        )

        mea_token = ""
        if not mea_token:
            mea_token = mea.get_token(
                mea_api_credential["username"], mea_api_credential["password"]
            )
        else:
            mea.mea_api.TOKEN = mea_token

        # AV01-Default Template
        # Default Template
        # IM01-Default Template
        template = "AV01-Default Template"
        lob_code = template.split("-")[0]
        submission_id = f"{lob_code}-{client_identifier.upper()}-{application_id}"
        print(f"Submitting package for {submission_id} with template {template}")

        eml_filename = Path(eml_file_path).name

        response = mea.post_submission(
            submission_id, template, eml_filename, eml_file_path
        )

        eml_key = Path(eml_key).joinpath(f"MEA_{eml_filename}")

        if response is None:
            upload_to_s3_asfile(bucket, eml_key, Path(eml_file_path))
            raise Exception("Unable to submit to mea")
        else:
            print(f"{response.status_code} File submitted. {response.text}")

    # upload_to_s3_asfile(bucket, eml_key, Path(eml_file_path))

    print(f"Processing complete.")
    return {"statusCode": 200, "body": "success"}
