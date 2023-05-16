# Prototype to create an eml file using python

import os
import uuid
from email import generator, encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

# where to write the output file
directory = "zattach"
body = "Hello email!"
subject = "test"
toAddress = "joe@example.com"
fromAddress = "jane@example.com"


def create_message():
    msg = MIMEMultipart()
    msg["To"] = toAddress
    msg["From"] = fromAddress
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    attachment_type_MIMEBase = MIMEBase("application", "octet-stream")
    attachment_name = "piplist.txt"
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
    except Exception as error:
        msg_type_str = f"Error opening attachment file {attachment_name}"
        print(error, msg_type_str)

    return msg


def write_eml_file(msg):
    os.chdir(directory)
    filename = str(uuid.uuid4()) + ".eml"

    with open(filename, "w") as file:
        emlGenerator = generator.Generator(file)
        emlGenerator.flatten(msg)
        print(filename)


def main():
    msg = create_message()
    write_eml_file(msg)


if __name__ == "__main__":
    main()
