import boto3
import asyncpg
import asyncio
import json, base64
from botocore.config import Config
from botocore.exceptions import ClientError

ssm_client = boto3.client(
    "ssm",
    config=Config(retries={"max_attempts": 2, "mode": "standard"}, connect_timeout=1),
)


def get_secret(secret_name, region_name):
    secret = ""

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return json.loads(secret)


async def dbconnect(dbcredentials):
    host = dbcredentials["host"]
    database = dbcredentials["name"]
    user = dbcredentials["username"]
    password = dbcredentials["password"]
    port = dbcredentials["port"]
    print(f"Trying connection to... {host}/{database}")
    try:
        conn = await asyncpg.create_pool(
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
    except Exception as e:
        print(f"Issue with connection")
        raise e
    print(f"Connection successful")
    return conn


async def dbclose(pool):
    await pool.close()


def get_db_connection(db_conn_param):
    try:
        print(f"Connecting to SSM Parameter store")
        response = ssm_client.get_parameter(Name=db_conn_param, WithDecryption=True)
        print(f"Retrieved details from {db_conn_param}")
        secret_name = json.loads(response["Parameter"]["Value"])
        dbcredentials = get_secret(secret_name["secretarnname"], "us-east-2")
        dbcredentials["name"] = secret_name["name"]
        connection = asyncio.get_event_loop().run_until_complete(
            dbconnect(dbcredentials)
        )
    except Exception as e:
        raise e
    return connection


async def run_query(connection, query):
    return await connection.fetch(query)


loop = asyncio.get_event_loop()
connection = get_db_connection("/cip/pncdev/cfnoutput/database/config")
print(connection)
query = "select max(status_change_log_id) from dim_status_changelog"
result = loop.run_until_complete(run_query(connection, query))
for row in result:
    print(dict(row))
    print(list(row))
    print(list(row.items()))
    print(dict(row.items()))
# {'max': 8421}
# [8421]
# [('max', 8421)]
# {'max': 8421}
loop.run_until_complete(dbclose(connection))
