import index

event = {
    "Records": [
        {
            "messageId": "3c90ca2f-3b52-41d9-bbca-f5b2150cae0c",
            "receiptHandle": "AQEBDRsRxlvT181gvqgOOl9kjF2GG0UyJ5+6GVmUgaH5NBKo/Hfw6sVQIfl8dsLUmKOeScavwrwiCDWNhcL1/zTvzdZa0xpdeOwY3Jj9bW06UtQGGMrt8C6QAjO8Gm/XzpRJXQ18lZSIpgj9ScIW9qcDA73Jadj6L6evfEulSdQST2subK6G9TT52hg+uUbnGdCqjjGOkR4NxtfwqhmljSQq4KCgxLqPZRRYnEk7/VbRZciFQNKtApmKAmHRq5jpwtdFCWWp9L7GyfvkCJC/6l7QSX0LUBaHuecSMSgABW8ygkHl97k13igjiMZypHYuKxBYN8wfgOk8PV3Aq4CQD0KawDykM9KWW+kHTtjPwfW+LXRUXlnP2ehEoIKKWVhME4uY",
            "body": {
                "Type": "Notification",
                "MessageId": "f5bec40f-2d78-5a07-9b80-9f96aff2d6cb",
                "TopicArn": "arn:aws:sns:us-east-2:241231414837:emailprocessed",
                "Subject": "Email Processing Complete",
                "Message": {
                    "sr_uid": "4c89b6993bf243bd977c2204e981ca80",
                    "application_id": "APP202209120163",
                    "service_type": "NB",
                    "subject": "FW Inland Marine Request for quotation for PALOS GARZA FORWARDING INC NB SENDTOMEA",
                    "outlook_id": "gn7clcjv8bkar6gov8esgelkhtnd2rdaab1l2ro1",
                    "first_request_flag": "Y",
                    "lob": "inland",
                    "attachments": [
                        "s3://cip-uw-email-extract-dev/inland.marine.docs@cipunderwriting.awsapps.com/thiru.arasan.dayalan@accenture.com/gn7clcjv8bkar6gov8esgelkhtnd2rdaab1l2ro1/Acord_125_PALOS_GARZA_FORWARDING_INCN_1442.pdf"
                    ],
                },
            },
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1663008843031",
                "SenderId": "AIDAJQR6QDGQ7PATMSYEY",
                "ApproximateFirstReceiveTimestamp": "1663008843038",
            },
            "messageAttributes": {},
            "md5OfBody": "9d870465f94d5685155f3604d9ff80c7",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-east-2:241231414837:meaintake",
            "awsRegion": "us-east-2",
        }
    ]
}
index.lambda_handler(event, "")
