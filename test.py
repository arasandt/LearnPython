# # import boto3
# # import email


# # s3_client = boto3.client("s3")
# # bucket = "cip-uw-email-inbound"
# # key = "aerospace.docs@cipunderwriting.awsapps.com/2022/6/1/17/24/lalit.bansal@accenture.com/gjeoon8l56jbmjp8n7ihn5tqa6o0r8h559bc9ug1"
# # data = s3_client.get_object(Bucket=bucket, Key=key)
# # contents = data["Body"].read().decode("utf-8")
# # email_msg = email.message_from_string(contents)
# # print(email_msg["X-SES-Virus-Verdict"])

# # from adal import AuthenticationContext

# # tenantname = "e0793d39-0939-496d-b129-198edd916feb"
# # clientid = "f58ed474-d9cf-494c-bc19-cbe00acc88aa"
# # username = "thiru.arasan.dayalan@accenture.com"
# # password = ""
# # resource = "https://graph.microsoft.com"

# # def obtain_accesstoken(tenantname,clientid,username,password, resource):
# #     auth_context = AuthenticationContext('https://login.microsoftonline.com/' +
# #         tenantname)
# #     token = auth_context.acquire_token_with_username_password(
# #         resource=resource,client_id=clientid,
# #         username=username, password=password)
# #     return token

# # token = obtain_accesstoken(tenantname,clientid,username,password,resource)
# # print(token)
# # # token_url = 'https://login.microsoftonline.com/e0793d39-0939-496d-b129-198edd916feb/oauth2/token'

# import msal
# import boto3

# acm_client = boto3.client("acm")


# def get_from_acm(certificate_arn):
#     try:
#         response = acm_client.get_certificate(CertificateArn=certificate_arn)
#     except Exception as ex:
#         raise ex
#     else:
#         return response


# tenant_id = "e0793d39-0939-496d-b129-198edd916feb"
# client_id = "bf1297ef-ba2f-463d-a0d4-dae496de2ba4"
# authority = "https://login.microsoftonline.com/" + tenant_id
# scope = ["https://graph.microsoft.com/.default"]
# client_secret = "CtD8Q~cKrxey2qTcNwajt2dSy5sW_degPQmogaBW"
# certificate_arn = "arn:aws:acm:us-east-2:241231414837:certificate/1c6fb8f2-5e1a-43e2-9fb3-c8a32e0d7f5f"
# thumbprint = "thumbprint generated after uploading it in Azure"
# certificate_data = get_from_acm(certificate_arn)
# certificate_data = certificate_data["Certificate"]

# try:
#     if client_secret:
#         client_credential = client_secret
#     else:
#         client_credential = {
#             "thumbprint": thumbprint,
#             "private_key": certificate_data,
#         }
#     app = msal.ConfidentialClientApplication(
#         client_id,
#         authority=authority,
#         client_credential=client_credential,
#     )
# except Exception as ex:
#     print("Unable to validate client credentails")
#     print(ex)
# else:
#     result = app.acquire_token_for_client(scopes=scope)
#     token = result["access_token"]
#     print(token)

# import json
# import boto3
# import base64
# import os
# from redis import Redis

# ssm_client = boto3.client("ssm")
# from botocore.exceptions import ClientError


# def get_secret(secret_name, region_name):

#     secret = ""

#     # Create a Secrets Manager client
#     session = boto3.session.Session()
#     client = session.client(service_name="secretsmanager", region_name=region_name)

#     # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
#     # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
#     # We rethrow the exception by default.

#     try:
#         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
#     except ClientError as e:
#         if e.response["Error"]["Code"] == "DecryptionFailureException":
#             # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
#             # Deal with the exception here, and/or rethrow at your discretion.
#             raise e
#         elif e.response["Error"]["Code"] == "InternalServiceErrorException":
#             # An error occurred on the server side.
#             # Deal with the exception here, and/or rethrow at your discretion.
#             raise e
#         elif e.response["Error"]["Code"] == "InvalidParameterException":
#             # You provided an invalid value for a parameter.
#             # Deal with the exception here, and/or rethrow at your discretion.
#             raise e
#         elif e.response["Error"]["Code"] == "InvalidRequestException":
#             # You provided a parameter value that is not valid for the current state of the resource.
#             # Deal with the exception here, and/or rethrow at your discretion.
#             raise e
#         elif e.response["Error"]["Code"] == "ResourceNotFoundException":
#             # We can't find the resource that you asked for.
#             # Deal with the exception here, and/or rethrow at your discretion.
#             raise e
#     else:
#         # Decrypts secret using the associated KMS CMK.
#         # Depending on whether the secret is a string or binary, one of these fields will be populated.
#         if "SecretString" in get_secret_value_response:
#             secret = get_secret_value_response["SecretString"]
#         else:
#             secret = base64.b64decode(get_secret_value_response["SecretBinary"])

#     return json.loads(secret)


# def redisconnect(rediscredentials):
#     try:
#         redis_endpoint, redis_port = rediscredentials["endpoint"].split(":")
#         token = rediscredentials["token"]
#         print(f"Trying connection to... {rediscredentials['endpoint']}")
#         connection = Redis(
#             host=redis_endpoint,
#             port=redis_port,
#             decode_responses=True,
#             ssl=True,
#             password=token,
#         )
#         connection.set("foo", "bar", ex=60)
#         foo = connection.get("foo")
#         assert foo == "bar"
#         print("Connection successful")
#     except AssertionError:
#         raise Exception(f"Connection failed to to Redis cluster {redis_endpoint}")
#     except Exception as e:
#         print(f"Issue with connection")
#         raise e
#     return connection


# def get_redis_connection(redis_conn_param):
#     try:

#         print(f"Connecting to SSM Parameter store")
#         response = ssm_client.get_parameter(Name=redis_conn_param, WithDecryption=True)
#         print(f"Retrieved details from {redis_conn_param}")
#         secret_name = json.loads(response["Parameter"]["Value"])
#         rediscredentials = get_secret(
#             secret_name["secretarnname"], os.getenv("AWS_REGION")
#         )
#         rediscredentials["endpoint"] = secret_name["endpoint"]
#         print(rediscredentials)
#         # connection = redisconnect(rediscredentials)
#     except Exception as e:
#         raise e
#     return True  # connection


# x = get_redis_connection("/cip/uw/redis/config")
# from sagemaker import image_uris, session

# sklearn_image = image_uris.retrieve("sklearn", session.Session().boto_region_name)

# print(sklearn_image)

# import boto3
# import sagemaker

# from sagemaker import session

# from sagemaker.model import Model
# from sagemaker.pipeline import PipelineModel

# # "rf-scikit-2022-07-19-12-45-08-645"
# model = Model(
#     model_data="s3://new-cip-uw/uw-win-propensity-final/rf-scikit-2022-07-19-12-37-54-742/output/model.tar.gz",
#     image_uri="257758044811.dkr.ecr.us-east-2.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3",
#     env={
#         "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
#         "SAGEMAKER_PROGRAM": "script.py",
#         "SAGEMAKER_REGION": "us-east-2",
#         "SAGEMAKER_SUBMIT_DIRECTORY": "s3://new-cip-uw/rf-scikit-2022-07-19-12-37-54-742/source/sourcedir.tar.gz",
#     },
# )

# print(model)

# model_name = "inference-pipeline-model"
# endpoint_name = "inference-pipeline-endpoint"
# sagemaker_role = "arn:aws:iam::241231414837:role/service-role/AmazonSageMaker-ExecutionRole-20220407T140127"
# sm_model = PipelineModel(name=model_name, role=sagemaker_role, models=[model])

# sm_model.deploy(
#     initial_instance_count=1,
#     instance_type="ml.c5.xlarge",
#     endpoint_name=endpoint_name,
#     wait=False,
# )

# from sagemaker.sklearn.model import SKLearnModel

# model_path = ""
# script_path = ""

# model = SKLearnModel(
#     model_data=model_path,
#     # role=aws_role,
#     entry_point=script_path,
#     framework_version="0.20.0",
#     sagemaker_session=session.Session().boto_region_name,
# )


# import boto3
# import re

# textractClient = boto3.client("textract")


# def textract_analyze_form_docs(client, image_binary):
#     resp = {}
#     try:
#         resp = client.analyze_document(
#             Document={"Bytes": image_binary},
#             FeatureTypes=["FORMS"],
#         )
#     except Exception as e:
#         print("Error processing form analysis:", e)
#         resp = {}
#     return resp


# # object_link = "s3://cip-uw-email-extract-demo/test.cip.uw.docs@accenture.com/kanika.a.anand@accenture.com/AAMkADhhZTYwMWMzLWIyZTYtNGQ3ZC1hYTNiLTIzMGM0YTEwYmY0YQBGAAAAAAAJN-VlmROmSKyZ2dlHwpEZBwAPf363PBjoS59xLR3aycGiAAAXnyBiAAAPf363PBjoS59xLR3aycGiAAAZe0IFAAA=/Acord 325__KLX_AEROSPACE_SOLUTIONS_7117.pdf"
# object_link = "s3://cip-uw-email-extract-demo/test.cip.uw.docs@accenture.com/kanika.a.anand@accenture.com/AAMkADhhZTYwMWMzLWIyZTYtNGQ3ZC1hYTNiLTIzMGM0YTEwYmY0YQBGAAAAAAAJN-VlmROmSKyZ2dlHwpEZBwAPf363PBjoS59xLR3aycGiAAAXnyBiAAAPf363PBjoS59xLR3aycGiAAAZe0IFAAA=/Loss Run _KLX_AEROSPACE_SOLUTIONS_8224.pdf"
# # object_link = "s3://cip-uw-email-extract-demo/test.cip.uw.docs@accenture.com/kanika.a.anand@accenture.com/AAMkADhhZTYwMWMzLWIyZTYtNGQ3ZC1hYTNiLTIzMGM0YTEwYmY0YQBGAAAAAAAJN-VlmROmSKyZ2dlHwpEZBwAPf363PBjoS59xLR3aycGiAAAXnyBiAAAPf363PBjoS59xLR3aycGiAAAZe0IFAAA=/SOV_KLX_AEROSPACE_SOLUTIONS_2878.pdf"
# bucket, key = re.sub(r"^s3://", "", object_link).split("/", 1)

# import sys, fitz  # import the bindings

# # doc = fitz.open("a.pdf")  # open document
# # doc = "Acord 325__KLX_AEROSPACE_SOLUTIONS_7117.pdf"
# # doc = "Loss Run _KLX_AEROSPACE_SOLUTIONS_8224.pdf"
# # doc = "SOV_KLX_AEROSPACE_SOLUTIONS_2878.pdf"
# doc = "Acord_325_LOS_ANGELES_WORLD_AIRPORTS.pdf"
# with fitz.open(doc) as doc:
#     page = doc[0]
#     pix = page.get_pixmap()  # render page to an image
#     pix.pil_save("page1.png")  # store image as a PNG

# with open("page1.png", "rb") as img:
#     img_data = img.read()
# # pages = convert_from_path("a.pdf", single_file=True)
# # print(len(pages))
# response = textract_analyze_form_docs(textractClient, img_data)
# # print(response)
# response = [
#     block["Text"].lower()
#     for block in response["Blocks"]
#     if block["BlockType"] in ["WORD", "LINE"]
# ]
# response = " ".join(response)
# print(response)
# if (
#     "sov" in response
#     or "statement of value" in response
#     or "schedule of value" in response
# ):
#     attachment_type = "SOV"
# elif "loss run" in response:
#     attachment_type = "LOSS RUN"
# elif "acord" in response:
#     attachment_type = "ACORD"
# else:
#     attachment_type = "OTHERS"
# print(attachment_type)


from bs4 import BeautifulSoup
import lxml

with open("a.html", "r") as f:
    html = f.read()
soup = BeautifulSoup(html, features="lxml")
x = soup.get_text()
x = x.split("________________________________")[0]
print(x.replace("\n", " ").replace("\r", " "))
