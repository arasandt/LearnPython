import requests
import json
from pathlib import Path

LOB_KEY = "Product Name"
VALUE_KEY = "value"
VALUE_STARTING_INDEX = 1


class MEAElement:
    name = ""
    value = None
    confidence = None

    def extract(self, input):
        if len(input) == 3:
            return self.extract_single_value(input)
        if (
            input[VALUE_STARTING_INDEX][VALUE_KEY] == ""
            and input[VALUE_STARTING_INDEX + 1][VALUE_KEY] == ""
        ):
            return None
        if input[VALUE_STARTING_INDEX + 1][VALUE_KEY] != "":
            return self.extract_array(input)
        else:
            return self.extract_single_value(input)

    def extract_name(self, input):
        return input[0][VALUE_KEY]

    def extract_confidence(self, input):
        return input[-1][VALUE_KEY]

    def extract_array(self, input):
        arr = []
        for i in input[1:-1]:
            arr.append(i[VALUE_KEY])
        return arr

    def extract_single_value(self, input):
        if input[1][VALUE_KEY] == "":
            return None
        return input[1][VALUE_KEY]

    def __init__(self, input):
        self.value = self.extract(input)
        self.name = self.extract_name(input)
        self.confidence = self.extract_confidence(input)

    def __str__(self):
        return str(self.to_json())

    def to_json(self):
        return {"name": self.name, "value": self.value, "confidence": self.confidence}


class MEAStructure:

    struct = []

    def transform(self, doc):
        struct = []
        doc = doc[0]  # skip first level of structure
        for i in doc:
            struct.append(MEAElement(i))
        return struct

    def __init__(self, doc):
        self.struct = self.transform(doc)

    def to_json(self):
        obj = {}
        for i in self.struct:
            j = i.to_json()
            obj[j["name"]] = j[VALUE_KEY]
        return obj


class MEAExtract:

    lob = None
    extract = None
    submission_id = None  # To be filled in once that value is extracted

    def __init__(self, doc):
        self.extract = MEAStructure(doc).to_json()
        self.lob = self.extract[LOB_KEY]

    def to_json(self):
        return {"lob": self.lob, "extract": self.extract}


class MEA_API:
    def __init__(self, base_url):
        self.BASE_URL = base_url
        self.TOKEN = ""

    def _make_mea_file_request(self, url, file_name):
        filename_to_upload = Path(file_name).name
        # with open(file_name, "rb") as upload_file:
        #     files = {"file": (filename_to_upload, upload_file)}
        #     headers = {}
        #     response = requests.put(url, files=files, headers=headers, verify=True)
        with open(file_name, "rb") as upload_file:
            upload_text = upload_file.read()
        response = requests.put(url, data=upload_text)
        return response

    def _make_mea_request(self, type, url, body, headers):
        url = self.BASE_URL + url
        request_body = body
        payload = json.dumps(request_body)
        headers = {"Content-Type": "text/plain"}
        if self.TOKEN:
            headers["Authorization"] = self.TOKEN

        response = requests.request(
            type, url, headers=headers, data=payload, verify=True
        )
        return response

    def post(self, url, body, headers):
        return self._make_mea_request("POST", url, body, headers)

    def get(self, url):
        return self._make_mea_request("GET", url, None, None)


class MEA:
    def __init__(self, client_id, base_url):
        self.client_id = client_id
        self.mea_api = MEA_API(base_url)

    def get_token(self, username, password):
        route = "/token"

        request_body = {
            "AuthParameters": {"USERNAME": username, "PASSWORD": password},
            "ClientId": self.client_id,
        }

        headers = {"Content-Type": "text/plain"}
        response = self.mea_api.post(route, request_body, headers)

        try:
            token = json.loads(response.text)["AuthenticationResult"]["AccessToken"]
        except Exception as error:
            print(error)
            return None
        self.mea_api.TOKEN = token
        return token

    def get_submission_documents(self, submission_id):
        submission_docs_response = self.mea_api.get(
            f"/submissions/{str(submission_id)}"
        )

        if "failed" in submission_docs_response.text:
            print("ERROR: ", submission_docs_response.text)
            return None

        json_response = json.loads(submission_docs_response.text)

        if "results" in json_response:
            return json_response["results"]
        else:
            return None

    def get_single_document(self, submission_id, file_name):
        try:
            api_response = self.mea_api.get(
                f"/submissions/{submission_id}/extractedFile/{file_name}"
            )
            json_result = json.loads(api_response.text)

            s3_url = json_result["results"]["S3Url-extractedFile"]
            s3_file = requests.get(s3_url, verify=True)
            json_res = json.dumps((s3_file.content).decode())
            json_res = json.loads(json_res)
            return json_res
        except Exception as error:
            print(error)
            return []

    def _get_document_to_extract(self, submission_id):
        res = self.get_submission_documents(submission_id)
        input_doc = [i["inputDocumentName"] for i in res if i["extractedDocumentName"]]
        return input_doc[0] if input_doc else ""

    def get_extract(self, submission_id):
        extract_file_name = self._get_document_to_extract(submission_id)
        if extract_file_name:
            print(f"File name : {extract_file_name}")
            single_doc = self.get_single_document(submission_id, extract_file_name)
            return str(single_doc)
            # return MEAExtract(single_doc).to_json()
        else:
            return False

    def post_submission(self, submission_id, template_name, file_name, file_path):
        route = f"/submissions/{submission_id}/{file_name}"
        body = {"templateName": template_name}
        res = self.mea_api.post(route, body, None)
        response_content = (res.content).decode("UTF-8", "ignore")
        if "failed" in response_content:
            print("ERROR: ", response_content)
            return None
        upload_url = json.loads(res.content)["uploadUrl"]
        print(f"Retrieved package upload url : {upload_url[:100]}")
        return self.mea_api._make_mea_file_request(upload_url, file_path)
