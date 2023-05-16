import email
import boto3

s3_client = boto3.client("s3")
bucket = "cip-uw-email-inbound-dev"
# key = "incoming/ses/inland.marine.doca@cipunderwriting.awsapps.com/gukra2nn30ut7agudpuoil73npfu5h6tagd8hdg1"
key = "incoming/ses/gen.liability.docs@cipunderwriting.awsapps.com/9uohqd5ocebto7l6nkopnhb0kh2vkh8n641p3bo1"
data = s3_client.get_object(Bucket=bucket, Key=key)
contents = data["Body"].read().decode("utf-8")

payload1 = None
email_msg = email.message_from_string(contents)


def get_attachments_count():
    global payload1
    global email_msg
    # Sometimes if an d
    # Sometimes if an dummy email is sent then payload might still contain more than 1 attachment. So removing any payload that does not have
    # "attachment" disposition. Retain only the first element since that would be the body.
    temp_payload = email_msg.get_payload()
    temp_payload = [
        p for p in temp_payload[1:] if p.get("Content-Disposition") is not None
    ]
    payload = [email_msg.get_payload()[0]]
    payload1 = payload + temp_payload
    return 0


get_attachments_count()
bodytext = payload1[0].get_payload()
if type(bodytext) is list:
    bodytext = ",".join(
        # str(v.get_payload(decode=True).decode("utf8")) for v in bodytext
        str(v.get_payload(decode=True).decode("utf8", "ignore"))
        for v in bodytext
    )
print(bodytext)
