import json
import urllib3
import base64

payload_classif_api = {
    "requestType": "claimsattachmenttype",
    "submissionid": "DOC202303280000",
    "text": [
        "s3://claimsdidev-cip-document-ingestion/demo/claim_supporting_doc_110.pdf"
    ],
}

CLASSIFICATION_URL = (
    "https://gpl9y98963.execute-api.us-west-2.amazonaws.com/development/submission"
)

payload = json.dumps(payload_classif_api)
message = str(payload)
message_bytes = message.encode("ascii")
base64_bytes = base64.b64encode(message_bytes)
classification_payload = {"data": base64_bytes.decode("UTF-8")}
x = urllib3.PoolManager()
response = x.urlopen(
    "POST",
    CLASSIFICATION_URL,
    body=json.dumps(classification_payload),
)

print(response.data)
