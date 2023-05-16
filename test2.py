# import boto3
# import json
# import msal
# from boto3.dynamodb.conditions import Key, Attr

# ssm_client = boto3.client("ssm")
# acm_client = boto3.client("acm")
# dynamodb_resource = boto3.resource("dynamodb")


# def get_mailboxes_to_monitor(table):
#     table = dynamodb_resource.Table(table)
#     response = table.scan(
#         FilterExpression=Attr("type").eq("outlook") and Attr("active").eq("y")
#     )
#     mailboxes = []
#     for item in response["Items"]:
#         mailboxes.append(item)
#     return mailboxes


# def get_from_acm(certificate_arn):
#     try:
#         response = acm_client.get_certificate(CertificateArn=certificate_arn)
#     except Exception as ex:
#         raise ex
#     else:
#         return response


# def get_token_public_client(client_id, authority, credential_flow, scope):
#     try:
#         app = msal.PublicClientApplication(
#             client_id,
#             authority=authority,
#         )
#         result = app.acquire_token_by_username_password(
#             username=credential_flow["username"],
#             password=credential_flow["password"],
#             scopes=scope,
#         )
#     except Exception as ex:
#         print("Unable to validate client credentials for public client")
#         raise ex
#     else:
#         token = result["access_token"]
#         return token


# def get_token_confidential_client(client_id, authority, credential_flow, scope):
#     try:
#         app = msal.ConfidentialClientApplication(
#             client_id,
#             authority=authority,
#             client_credential=credential_flow,
#         )
#         result = app.acquire_token_for_client(scopes=scope)
#     except Exception as ex:
#         print("Unable to validate client credentials for confidential client")
#         raise ex
#     else:
#         token = result["access_token"]
#         return token


# def get_mailbox_connection_token(mailbox):

#     tenant_id = mailbox.get("tenantid", "")
#     client_id = mailbox.get("clientid", "")
#     client_credentials = mailbox.get("clientcredentials", "")
#     authority = "https://login.microsoftonline.com/" + tenant_id
#     scope = ["https://graph.microsoft.com/.default"]

#     response = ssm_client.get_parameter(Name=client_credentials, WithDecryption=True)
#     print(f"Retrieved details from {client_credentials}")
#     client_credentials = json.loads(response["Parameter"]["Value"])

#     credential_flow = {}
#     print(client_credentials)
#     if client_credentials.get("clientsecret", ""):
#         print("Using Client Secret")
#         credential_flow = client_credentials["clientsecret"]
#         return get_token_confidential_client(
#             client_id, authority, credential_flow, scope
#         )
#     elif client_credentials.get("thumbprint", ""):
#         print("Using Client Certificate")
#         certificate_data = get_from_acm(client_credentials["certificatearn"])
#         certificate_data = certificate_data["Certificate"]
#         credential_flow = {
#             "thumbprint": client_credentials["thumbprint"],
#             "private_key": certificate_data,
#         }
#         return get_token_confidential_client(
#             client_id, authority, credential_flow, scope
#         )
#     elif client_credentials.get("username", ""):
#         print("Using ROPC")
#         credential_flow = {
#             "username": client_credentials["username"],
#             "password": client_credentials["password"],
#         }
#         return get_token_public_client(client_id, authority, credential_flow, scope)
#     else:
#         print(f"Client Credentials is not valid: {client_credentials}")
#         return None


# mailbox = get_mailboxes_to_monitor("mailboxconnections")
# print(mailbox)
# token = get_mailbox_connection_token(mailbox[0])
# print(token)
# import sys
import boto3

# from awsglue.transforms import *
# from awsglue.utils import getResolvedOptions
# from awsglue.context import GlueContext
# from pyspark.context import SparkContext

glue_client = boto3.client("glue")
workflow_name = "cip-uw-aig-etl-wf"
workflow_run_id = "wr_94b241e64632e5b2255dc47bf6302fa680b7f6ada64da5f0cf24db2fa900d80d"
workflow_params = glue_client.get_workflow_run_properties(
    Name=workflow_name, RunId=workflow_run_id
)["RunProperties"]

print(workflow_params)
