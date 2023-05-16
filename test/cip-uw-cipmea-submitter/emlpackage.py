import os
import uuid
from email import generator, encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import datetime, timezone
from pathlib import Path

body = ""
toAddress = "noreply@noreply.com"
fromAddress = "noreply@noreply.com"


def create_message(attachments, subject):
    msg = MIMEMultipart()
    msg["To"] = toAddress
    msg["From"] = fromAddress
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    for attachment_name in attachments:
        attachment_type_MIMEBase = MIMEBase("application", "octet-stream")
        try:
            with open(attachment_name, "rb") as attachment:
                attachment_bytes = attachment.read()
            attachment_type_MIMEBase.set_payload(attachment_bytes)
            encoders.encode_base64(attachment_type_MIMEBase)
            attachment_type_MIMEBase.add_header(
                "content-Disposition",
                "attachment",
                filename=os.path.basename(attachment_name),
            )
            msg.attach(attachment_type_MIMEBase)
            print(f"Attaching {attachment_name} to eml package")
        except Exception as error:
            msg_type_str = f"Error opening attachment file {attachment_name}"
            print(error, msg_type_str)

    return msg


def write_eml_file(msg, temp_directory, subject):
    dt_obj = datetime.now(timezone.utc).strftime("%m%d%Y_%H%M%S")
    filename = f"{subject}_{dt_obj}.eml"
    filename = Path(temp_directory).joinpath(filename)
    with open(filename, "w") as file:
        emlGenerator = generator.Generator(file)
        emlGenerator.flatten(msg)
        print(f"Created package {filename}")
    return str(filename)


def create_eml(attachments, temp_directory, subject):
    msg = create_message(attachments, subject)
    return write_eml_file(msg, temp_directory, subject)
