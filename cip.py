# importing required libraries
import os
import io
import boto3
import json
import csv

# import psycopg2
import botocore
from botocore.config import Config
from idfbin.DataQualityModule import *
from idfbin.DataIntegrationModule import *

# from idfbin.Util import *
import numpy as np
import pandas as pd
import datetime
import collections
import ast

Parameter_Store_Rds = "/cip/uw/database/config"
# Parameter_Store_Rds = "/cip/uw/model/output_score"
bucket = "cip-appetite-dl-landing-ue1-demos"
# Parameter_Store_Rds = os.environ['RDS_PARAMETER_STORE']
boto3_ssm_client = boto3.client(
    "ssm",
    config=Config(retries={"max_attempts": 2, "mode": "standard"}, connect_timeout=500),
)


def get_ssm_parameters(boto3_ssm_client, path):
    # function to get parameters stored in ssm
    try:
        response = boto3_ssm_client.get_parameters(Names=path, WithDecryption=True)
        response_object = {}
        for item in response["Parameters"]:
            response_object[item["Name"]] = item["Value"]
        print("SSM Fetched")
        return response_object
    except botocore.exceptions.ClientError as e:
        print("Error in fetching ssm parameters", e)
        raise RuntimeError("FAILED_TO_FETCH_SSM")


ssm_values = get_ssm_parameters(boto3_ssm_client, [Parameter_Store_Rds])
env_var_json = json.loads(ssm_values[Parameter_Store_Rds])

# db_credentials_secrets_arn = env_var_json["db_credentials_secrets_arn"]
# db_cluster_arn = env_var_json["db_cluster_arn"]
# database_name = env_var_json["database_name"]
db_credentials_secrets_arn = env_var_json["secretarnname"]
db_cluster_arn = env_var_json["clusterarn"]
database_name = env_var_json["database"]

rds_boto3_client = boto3.client("rds-data")


def data_fetch(sql):
    data = rds_boto3_client.execute_statement(
        secretArn=db_credentials_secrets_arn,
        database=database_name,
        resourceArn=db_cluster_arn,
        sql=sql,
    )

    lst = []
    records = data["records"]
    n = len(records)
    for i in range(0, n):
        x1 = records[i]
        x2 = [{k: np.nan if k == "isNull" else v for k, v in x.items()} for x in x1]
        y = [list(d.values())[0] for d in x2]
        lst.append(y)
        # print(lst)
    return lst


def lambda_handler(event, context):
    # fetching application id & applicant name from SQS Message
    # application_id = event['queryStringParameters']['application_id']
    # print(event['Records'])
    # application_id = event['Records']['body']['application_id']
    # subject = event['Records']['body']['subject']
    # application_id = event['application_id']
    application_id = ast.literal_eval(event["Records"][0]["body"])["application_id"]
    subject = ast.literal_eval(event["Records"][0]["body"])["subject"]
    # # application_id = "APP0101202001"
    # subject = event['subject']
    print(application_id)
    print(subject)

    if "MARINE" in subject.upper():
        lob = "InlandMarine"
    else:
        lob = "Aerospace"

    # extracting applicant name from the subject of mail body
    if "KLX" in subject.upper():
        applicant_name = "KLX AEROSPACE SOLUTIONS"
    elif "ANGELES" in subject.upper():
        applicant_name = "LOS ANGELES WORLD AIRPORTS"
    elif "GARZA" in subject.upper():
        applicant_name = "PALOS GARZA FORWARDING INC"
    elif "SPECTRUM" in subject.upper():
        applicant_name = "SPECTRUM LABEL CORPORATION"

    # loading the prepared sample jsons
    json1 = json.load(open("src/json1"))
    json1 = {k.upper(): v for k, v in json1.items()}
    json11 = json.load(open("src/json1.1"))
    json11 = {k.upper(): v for k, v in json11.items()}

    json2 = json.load(open("src/json2"))
    json2 = {k.upper(): v for k, v in json2.items()}
    json21 = json.load(open("src/json2.1"))
    json21 = {k.upper(): v for k, v in json21.items()}

    json3 = json.load(open("src/json3"))
    json3 = {k.upper(): v for k, v in json3.items()}
    json31 = json.load(open("src/json3.1"))
    json31 = {k.upper(): v for k, v in json31.items()}

    json4 = json.load(open("src/json4"))
    json4 = {k.upper(): v for k, v in json4.items()}
    json41 = json.load(open("src/json4.1"))
    json41 = {k.upper(): v for k, v in json41.items()}

    json1_name = json1["APPLICANT_DETAILS"][0]["Applicant_Name"]
    json2_name = json2["APPLICANT_DETAILS"][0]["Applicant_Name"]
    json3_name = json3["APPLICANT_DETAILS"][0]["Applicant_Name"]
    json4_name = json4["APPLICANT_DETAILS"][0]["Applicant_Name"]

    # matching applicant name to select on of the jsons
    if applicant_name.upper() == json1_name.upper():
        modify_json2 = json1
        modify_json1 = json11
    elif applicant_name.upper() == json2_name.upper():
        modify_json2 = json2
        modify_json1 = json21
    elif applicant_name.upper() == json3_name.upper():
        modify_json2 = json3
        modify_json1 = json31
    elif applicant_name.upper() == json4_name.upper():
        modify_json2 = json4
        modify_json1 = json41

    print(applicant_name)

    # modifying the json

    # updating application_ids
    sql = """select * from json_counter"""
    json_counter = pd.DataFrame(
        data_fetch(sql),
        columns=[
            "account_id",
            "location_no",
            "aircraft_id",
            "coverage_uid",
            "organisationid",
            "applicant_id",
            "item_uid_sch",
            "item_uid_sov",
            "risk_item_id",
            "airport_asset_id",
        ],
    )
    json_counter += 1
    print(json_counter)

    modify_json2["APPLICATION_INFO_BASIC"][0] = {
        k.upper(): v for k, v in modify_json2["APPLICATION_INFO_BASIC"][0].items()
    }
    modify_json2["APPLICATION_INFO_BASIC"][0]["APPLICATION_ID"] = application_id
    modify_json1["APPLICATION_INFO_BASIC"][0] = {
        k.upper(): v for k, v in modify_json1["APPLICATION_INFO_BASIC"][0].items()
    }
    modify_json1["APPLICATION_INFO_BASIC"][0]["APPLICATION_ID"] = application_id

    modify_json2["APPLICANT_DETAILS"][0] = {
        k.upper(): v for k, v in modify_json2["APPLICANT_DETAILS"][0].items()
    }
    modify_json2["APPLICANT_DETAILS"][0]["APPLICATION_ID"] = application_id
    modify_json2["APPLICANT_DETAILS"][0]["APPLICANT_ID"] = "APPL" + str(
        json_counter["applicant_id"][0]
    )
    modify_json1["APPLICANT_DETAILS"][0] = {
        k.upper(): v for k, v in modify_json1["APPLICANT_DETAILS"][0].items()
    }
    modify_json1["APPLICANT_DETAILS"][0]["APPLICATION_ID"] = application_id
    modify_json1["APPLICANT_DETAILS"][0]["APPLICANT_ID"] = "APPL" + str(
        json_counter["applicant_id"][0]
    )

    modify_json2["APPLICATION_DETAILS"][0] = {
        k.upper(): v for k, v in modify_json2["APPLICATION_DETAILS"][0].items()
    }
    modify_json2["APPLICATION_DETAILS"][0]["APPLICATION_ID"] = application_id
    modify_json2["APPLICATION_DETAILS"][0]["ACCOUNT_ID"] = "ACC" + str(
        json_counter["account_id"][0]
    )
    modify_json2["APPLICATION_DETAILS"][0]["ORGANISATION_ID"] = "OSG" + str(
        json_counter["organisationid"][0]
    )
    modify_json1["APPLICATION_DETAILS"][0] = {
        k.upper(): v for k, v in modify_json1["APPLICATION_DETAILS"][0].items()
    }
    modify_json1["APPLICATION_DETAILS"][0]["APPLICATION_ID"] = application_id
    modify_json1["APPLICATION_DETAILS"][0]["ACCOUNT_ID"] = "ACC" + str(
        json_counter["account_id"][0]
    )
    modify_json1["APPLICATION_DETAILS"][0]["ORGANISATION_ID"] = "OSG" + str(
        json_counter["organisationid"][0]
    )
    # json_counter['account_id'] = (json_counter['account_id'][0]) + 1
    # print(modify_json2['APPLICATION_DETAILS'][0]['ACCOUNT_ID'])

    modify_json2["ORGANISATION"][0] = {
        k.upper(): v for k, v in modify_json2["ORGANISATION"][0].items()
    }
    modify_json2["ORGANISATION"][0]["ORGANISATIONID"] = "OSG" + str(
        json_counter["organisationid"][0]
    )
    modify_json1["ORGANISATION"][0] = {
        k.upper(): v for k, v in modify_json1["ORGANISATION"][0].items()
    }
    modify_json1["ORGANISATION"][0]["ORGANISATIONID"] = "OSG" + str(
        json_counter["organisationid"][0]
    )

    modify_json2["COVERAGE"][0] = {
        k.upper(): v for k, v in modify_json2["COVERAGE"][0].items()
    }
    modify_json2["COVERAGE"][0]["APPLICATION_ID"] = application_id
    modify_json2["COVERAGE"][0]["COVERAGE_UID"] = "CVV" + str(
        json_counter["coverage_uid"][0]
    )
    modify_json1["COVERAGE"][0] = {
        k.upper(): v for k, v in modify_json1["COVERAGE"][0].items()
    }
    modify_json1["COVERAGE"][0]["APPLICATION_ID"] = application_id
    modify_json1["COVERAGE"][0]["COVERAGE_UID"] = "CVV" + str(
        json_counter["coverage_uid"][0]
    )

    if lob == "Aerospace":
        modify_json2["RISK_DETAILS"][0] = {
            k.upper(): v for k, v in modify_json2["RISK_DETAILS"][0].items()
        }
        modify_json2["RISK_DETAILS"][0]["RISK_ITEM_ID"] = "RID" + str(
            json_counter["risk_item_id"][0]
        )
        modify_json2["RISK_DETAILS"][0]["APPLICATION_ID"] = application_id
        modify_json1["RISK_DETAILS"][0] = {
            k.upper(): v for k, v in modify_json1["RISK_DETAILS"][0].items()
        }
        modify_json1["RISK_DETAILS"][0]["RISK_ITEM_ID"] = "RID" + str(
            json_counter["risk_item_id"][0]
        )
        modify_json1["RISK_DETAILS"][0]["APPLICATION_ID"] = application_id
        ## Generating airport_id
        modify_json2["AIRPORT_PROPERTY_DETAILS"][0] = {
            k.upper(): v for k, v in modify_json2["AIRPORT_PROPERTY_DETAILS"][0].items()
        }
        modify_json2["AIRPORT_PROPERTY_DETAILS"][0]["AIRPORT_ASSET_ID"] = "AID" + str(
            json_counter["airport_asset_id"][0]
        )
        modify_json2["AIRPORT_PROPERTY_DETAILS"][0]["RISK_ID"] = "RID" + str(
            json_counter["risk_item_id"][0]
        )
        modify_json1["AIRPORT_PROPERTY_DETAILS"][0] = {
            k.upper(): v for k, v in modify_json1["AIRPORT_PROPERTY_DETAILS"][0].items()
        }
        modify_json1["AIRPORT_PROPERTY_DETAILS"][0]["AIRPORT_ASSET_ID"] = "AID" + str(
            json_counter["airport_asset_id"][0]
        )
        modify_json1["AIRPORT_PROPERTY_DETAILS"][0]["RISK_ID"] = "RID" + str(
            json_counter["risk_item_id"][0]
        )

    try:
        modify_json2["FACILITY_DETAILS"][0] = {
            k.upper(): v for k, v in modify_json2["FACILITY_DETAILS"][0].items()
        }
        modify_json2["FACILITY_DETAILS"][0]["LOCATION_ID"] = "LOC" + str(
            json_counter["location_no"][0]
        )
        modify_json2["FACILITY_DETAILS"][0]["APPLICATION_ID"] = application_id
        modify_json1["FACILITY_DETAILS"][0] = {
            k.upper(): v for k, v in modify_json1["FACILITY_DETAILS"][0].items()
        }
        modify_json1["FACILITY_DETAILS"][0]["LOCATION_ID"] = "LOC" + str(
            json_counter["location_no"][0]
        )
        modify_json1["FACILITY_DETAILS"][0]["APPLICATION_ID"] = application_id
    except Exception as e:
        print(e)
        pass

    if lob == "InlandMarine":
        length_sov = len(
            [ele for ele in modify_json2["IM_SOV"] if isinstance(ele, dict)]
        )
        for i in range(0, length_sov):
            modify_json2["IM_SOV"][i] = {
                k.upper(): v for k, v in modify_json2["IM_SOV"][i].items()
            }
            modify_json2["IM_SOV"][i]["LOCATION"] = "LOC" + str(
                json_counter["location_no"][0]
            )
            json_counter["location_no"][0] = json_counter["location_no"][0] + 1
            modify_json2["IM_SOV"][i]["ITEM_UID"] = "ITM" + str(
                json_counter["item_uid_sov"][0]
            )
            json_counter["item_uid_sov"][0] = json_counter["item_uid_sov"][0] + 1

        length_sch = len(
            [ele for ele in modify_json2["IM_SCH_ITEMS"] if isinstance(ele, dict)]
        )
        for i in range(0, length_sch):
            modify_json2["IM_SCH_ITEMS"][i] = {
                k.upper(): v for k, v in modify_json2["IM_SCH_ITEMS"][i].items()
            }
            modify_json2["IM_SCH_ITEMS"][i]["ITEM_UID"] = "ITM" + str(
                json_counter["item_uid_sch"][0]
            )
            modify_json1["IM_SCH_ITEMS"][i] = {
                k.upper(): v for k, v in modify_json1["IM_SCH_ITEMS"][i].items()
            }
            modify_json1["IM_SCH_ITEMS"][i]["ITEM_UID"] = "ITM" + str(
                json_counter["item_uid_sch"][0]
            )
            json_counter["item_uid_sch"][0] = json_counter["item_uid_sch"][0] + 1

    try:
        modify_json2["AIRCRAFT"][0] = {
            k.upper(): v for k, v in modify_json2["AIRCRAFT"][0].items()
        }
        modify_json2["AIRCRAFT"][0]["APPLICATION_ID"] = application_id
        modify_json2["AIRCRAFT"][0]["AIRCRAFT_ID"] = "RR" + str(
            json_counter["aircraft_id"][0]
        )
        modify_json1["AIRCRAFT"][0] = {
            k.upper(): v for k, v in modify_json1["AIRCRAFT"][0].items()
        }
        modify_json1["AIRCRAFT"][0]["APPLICATION_ID"] = application_id
        modify_json1["AIRCRAFT"][0]["AIRCRAFT_ID"] = "RR" + str(
            json_counter["aircraft_id"][0]
        )
    except Exception as e:
        print(e)
        pass

    length_priorcarrier = len(
        [
            ele
            for ele in modify_json2["PRIOR_CARRIER_INFORMATION"]
            if isinstance(ele, dict)
        ]
    )
    for i in range(0, length_priorcarrier):
        modify_json2["PRIOR_CARRIER_INFORMATION"][i] = {
            k.upper(): v
            for k, v in modify_json2["PRIOR_CARRIER_INFORMATION"][i].items()
        }
        modify_json2["PRIOR_CARRIER_INFORMATION"][i]["APPLICATION_ID"] = application_id
        modify_json2["PRIOR_CARRIER_INFORMATION"][i]["APP_ID_POLICY_ID"] = (
            application_id + modify_json2["PRIOR_CARRIER_INFORMATION"][i]["POLICY_NO"]
        )
        modify_json1["PRIOR_CARRIER_INFORMATION"][i] = {
            k.upper(): v
            for k, v in modify_json1["PRIOR_CARRIER_INFORMATION"][i].items()
        }
        modify_json1["PRIOR_CARRIER_INFORMATION"][i]["APPLICATION_ID"] = application_id
        modify_json1["PRIOR_CARRIER_INFORMATION"][i]["APP_ID_POLICY_ID"] = (
            application_id + modify_json2["PRIOR_CARRIER_INFORMATION"][i]["POLICY_NO"]
        )

    length_lrclmval = len(
        [ele for ele in modify_json2["LOSS_RUN_CLAIM_VALUES"] if isinstance(ele, dict)]
    )
    for i in range(0, length_lrclmval):
        modify_json2["LOSS_RUN_CLAIM_VALUES"][i] = {
            k.upper(): v for k, v in modify_json2["LOSS_RUN_CLAIM_VALUES"][i].items()
        }
        modify_json2["LOSS_RUN_CLAIM_VALUES"][i]["APPLICATION_ID"] = application_id
        modify_json2["LOSS_RUN_CLAIM_VALUES"][i]["APP_ID_DOC_ID"] = (
            application_id + modify_json2["LOSS_RUN_CLAIM_VALUES"][i]["DOC_ID"]
        )

    # try:
    #     for i in range(len(modify_json1['LOSS_RUN_CLAIM_VALUES'][0])-1):
    #          modify_json1['LOSS_RUN_CLAIM_VALUES'][i] = {k.upper(): v for k, v in modify_json1['LOSS_RUN_CLAIM_VALUES'][i].items()}
    #          modify_json1['LOSS_RUN_CLAIM_VALUES'][i]['APPLICATION_ID'] = application_id
    #          modify_json1['LOSS_RUN_CLAIM_VALUES'][i]['APP_ID_DOC_ID'] = application_id+modify_json1['LOSS_RUN_CLAIM_VALUES'][i]['DOC_ID']
    # except Exception as e:
    #     print(e)
    #     pass

    length_lrclmlvl = len(
        [ele for ele in modify_json2["LOSS_RUN_CLAIM_LEVEL"] if isinstance(ele, dict)]
    )
    for i in range(0, length_lrclmlvl):
        modify_json2["LOSS_RUN_CLAIM_LEVEL"][i] = {
            k.upper(): v for k, v in modify_json2["LOSS_RUN_CLAIM_LEVEL"][i].items()
        }
        modify_json2["LOSS_RUN_CLAIM_LEVEL"][i]["APPLICATION_ID"] = application_id
        modify_json2["LOSS_RUN_CLAIM_LEVEL"][i]["APP_ID_CLM_ID"] = (
            application_id + modify_json2["LOSS_RUN_CLAIM_LEVEL"][i]["CLAIM_NO"]
        )
        modify_json1["LOSS_RUN_CLAIM_LEVEL"][i] = {
            k.upper(): v for k, v in modify_json1["LOSS_RUN_CLAIM_LEVEL"][i].items()
        }
        modify_json1["LOSS_RUN_CLAIM_LEVEL"][i]["APP_ID_CLM_ID"] = (
            application_id + modify_json1["LOSS_RUN_CLAIM_LEVEL"][i]["CLAIM_NO"]
        )
        modify_json1["LOSS_RUN_CLAIM_LEVEL"][i]["APPLICATION_ID"] = application_id

    # modify_json1list(modify_json1['APPLICATION_INFO_BASIC'][0].keys()))
    # if 'AIRCRAFT' in modify_json2.keys():
    #     modify_json1 = {key: modify_json2[key] for key in ['APPLICATION_INFO_BASIC','APPLICANT_DETAILS',
    #     'APPLICATION_DETAILS','ORGANISATION','AGENT_DETAILS','AIRCRAFT','LOSS_RUN_CLAIM_LEVEL','PRIOR_CARRIER_INFORMATION',
    #     'COVERAGE']}
    #     print(modify_json1['APPLICATION_INFO_BASIC'][0])
    # else:
    #     modify_json1 = {key: modify_json2[key] for key in ['APPLICATION_INFO_BASIC','APPLICANT_DETAILS',
    #     'APPLICATION_DETAILS','ORGANISATION','AGENT_DETAILS','IM_SCH_ITEMS','LOSS_RUN_CLAIM_LEVEL','PRIOR_CARRIER_INFORMATION',
    #     'COVERAGE']}

    response = rds_boto3_client.execute_statement(
        secretArn=db_credentials_secrets_arn,
        database=database_name,
        resourceArn=db_cluster_arn,
        sql="""delete from json_counter""",
    )

    rec = tuple(json_counter.iloc[0].values)
    print(rec)
    sql = """INSERT INTO json_counter values{vals}""".format(vals=rec)
    response = rds_boto3_client.execute_statement(
        secretArn=db_credentials_secrets_arn,
        database=database_name,
        resourceArn=db_cluster_arn,
        sql=sql,
    )

    print("Updated 2nd Pull Data")
    print(modify_json2)
    print("Updated 1st Pull Data")
    print(modify_json1)

    s3 = boto3.client("s3")

    # Loading 1st pull Json in S3
    # 	transactionToUpload = {}
    # 	transactionToUpload['modify_json2'] = 'modify_json2'

    fileName1 = (
        "cip/standardization/mea_json/first_pull/"
        + lob
        + "_"
        + application_id
        + "_1stPull.json"
    )

    uploadByteStream = bytes(json.dumps(modify_json1).encode("UTF-8"))

    response = s3.put_object(Bucket=bucket, Key=fileName1, Body=uploadByteStream)
    print(response)
    print("First Pull Complete")

    # Loading 2nd pull Json in S3
    fileName2 = (
        "cip/standardization/mea_json/second_pull/"
        + lob
        + "_"
        + application_id
        + "_2ndPull.json"
    )
    uploadByteStream = bytes(json.dumps(modify_json2).encode("UTF-8"))
    response = s3.put_object(Bucket=bucket, Key=fileName2, Body=uploadByteStream)
    print(response)
    print("Second Pull Complete")

    combined_json = {"first_pull": modify_json1, "second_pull": modify_json2}
    print(combined_json)

    # creating JSON for returning
    applicationResponse = {}
    applicationResponse["applicationID"] = application_id
    applicationResponse["applicant_name"] = modify_json2["APPLICANT_DETAILS"][0][
        "APPLICANT_NAME"
    ]
    # applicationResponse['message'] =    'Model Score Displayed Successfully'
    # 3. Construct http response object

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "application/json"
    responseObject["body"] = json.dumps(combined_json)

    return {
        "body": responseObject["body"],
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
