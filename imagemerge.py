from bs4 import BeautifulSoup
import urllib.parse
import lxml
import os
import re
import boto3
import json
from botocore.config import Config
from pathlib import Path
import fitz
from PIL import Image


TEXTRACT_CLIENT = boto3.client(
    "textract",
    config=Config(
        retries={"max_attempts": 10, "mode": "standard"}, connect_timeout=120
    ),
)


def extract_text_from_file(filename):
    text = ""

    if text:
        text = text.replace("\n", " ")
        text = re.sub(r"\s\s+", " ", text)
        return text
    else:
        temp_filename = Path(Path(filename).parent).joinpath("temp.png")

        textract_contents = []
        with fitz.open(filename) as image_file:
            for page in image_file:
                pix = page.get_pixmap()
                pix.pil_save(temp_filename)
                with open(temp_filename, "rb") as img:
                    img_data = img.read()
                    response = TEXTRACT_CLIENT.analyze_document(
                        Document={"Bytes": img_data},
                        FeatureTypes=["FORMS"],
                    )
                    try:
                        response = [
                            block["Text"].lower()
                            for block in response["Blocks"]
                            if block["BlockType"] in ["LINE"]
                        ]
                    except Exception:
                        response = []

                Path.unlink(temp_filename)

                textract_contents += response

        return " ".join(textract_contents)


contents = extract_text_from_file("uw_supporting document_06.pdf")
print(contents)
