import json
import boto3
import requests
import pytest
import os
from collections import defaultdict

BASE_URL = "https://ansible.leadgen.pennysaver.in"
LOGIN_ENDPOINT = "https://ansible.leadgen.pennysaver.in/"
# Correct API key
VALID_HEADERS = {"x-api-key": "JePEy20KSPCR7zFTooa5kA=="}
API_KEY = "JePEy20KSPCR7zFTooa5kA=="
BUCKET_NAME = "meena-test-files"
Key = "smile.png"
INBOX_ID = 1
TEST_NUMBER = "+12013507562"
# Wrong API key
INVALID_HEADERS = {"x-api-key": "JePEy20KSPCR7zFTooa5kAaa=="}
headers = {
    'x-api-key': 'JePEy20KSPCR7zFTooa5kA==',  # or "x-api-key": API_KEY
    "Content-Type": "application/json"
}
s3 = boto3.session.Session(profile_name="meena",region_name="us-east-1")
s3_client = s3.client('s3')
# ---------------- LOGIN NEGATIVE TEST CASES ----------------

@pytest.mark.parametrize("username,password", [
    ("wrong_user", "wrong_pass"),   # completely invalid
    ("valid_user", "wrong_pass"),   # correct username, wrong password
    ("wrong_user", "valid_pass"),   # wrong username, valid password
    ("", "somepass"),               # empty username
    ("someuser", ""),              # empty password
    ("", ""),  # both empty
])
def test_invalid_login(username, password):
    """Negative test: invalid username/password combinations"""
    payload = {}
    if username is not None:
        payload["username"] = username
    if password is not None:
        payload["password"] = password

    response = requests.post(LOGIN_ENDPOINT, json=payload)

    # Accept 400, 401, 403, or 422 depending on backend auth design
    assert response.status_code in [400, 401, 403, 422], (
        f"Expected 400/401/403/422 for invalid credentials, got {response.status_code}"
    )

    # Check that the API returns an error message in response
    try:
        data = response.json()
        assert "error" in data or "message" in data, "Response should contain error details"
    except ValueError:
        pytest.fail("Response is not valid JSON")

def test_missing_credentials():
    """Negative test: no body at all"""
    response = requests.post(LOGIN_ENDPOINT, json={})

    # Accept 400, 401, 403, or 422 depending on backend behavior
    assert response.status_code in [400, 401, 403, 422], (
        f"Expected 400/401/403/422 for missing credentials, got {response.status_code}"
    )

    # Check that error details are included
    try:
        data = response.json()
        assert "error" in data or "message" in data, "Response should contain error details"
    except ValueError:
        pytest.fail("Response is not valid JSON")

###--------Inboxes TestCase-----------------------------------------------------------------

def get_all_inboxes():
    """Fetch all inboxes accessible with the API key."""
    url = f"{BASE_URL}/all_inboxes"
    response = requests.get(url, headers=headers)

    # Ensure the request was successful
    assert response.status_code == 200, f"Failed to fetch inboxes: {response.text}"

    inboxes = response.json()  # data is already a list
    assert isinstance(inboxes, list), "Expected inboxes to be a list"

    return inboxes


def test_all_inboxes_structure():
    """Check all inboxes exist and have required fields."""
    inboxes = get_all_inboxes()
    for inbox in inboxes:
        print(f"Inbox ID: {inbox['inbox_id']}, Inbox_Name: {inbox['inbox_name']}")

    # Ensure there is at least one inbox
    assert len(inboxes) > 0, "No inboxes found for this API key"

    for inbox in inboxes:
        # Check required fields for each inbox
        assert "inbox_id" in inbox, f"Inbox missing 'inbox_id': {inbox}"
        assert "inbox_name" in inbox, f"Inbox missing 'inbox_name': {inbox}"
        # print(f"Inbox ID: {inbox['inbox_id']}, Name: {inbox['inbox_name']}")
def get_all_inboxes_with_count():
    url = f"{BASE_URL}/inboxes?user_id=gunalr00@gmail.com"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Customer numbers fetch failed: {response.text}"
    inboxes = response.json()
    print("Inboxes with Count:", inboxes)
    return inboxes
def test_all_inboxes_with_count():
    response = get_all_inboxes_with_count()
    assert response , "Invalid Inbox_id"
#----------------Thread Testcase---------------------------------------------
def test_wrong_http_method():
    """Negative test: wrong HTTP method"""
    response = requests.post(f"{BASE_URL}/inbox/1/threads?page_size=100&page=1", headers=headers, json={"filter": "all"})
    assert response.status_code in [400, 405], (
        f"Expected 400/405 for wrong method, got {response.status_code}"
    )
def get_thread():
  url = f"{BASE_URL}/inbox/1/threads?page_size=100&page=1"
  response = requests.get(url, headers=headers)
  response.raise_for_status()
  return response.json()
#
# # Step 3: Test all threads in all inboxes
def test_threads_in_all_inboxes():
    inboxes = get_thread()
    print(inboxes)
    assert len(inboxes) > 0, "No inboxes found for this API key"
#------------Message Test case--------------
def test_missing_auth_header():
    """Negative test: no API key"""
    response = requests.post(f"{BASE_URL}/inbox/1/message")
    assert response.status_code in [401, 403], (
        f"Expected 401/403 for missing auth, got {response.status_code}"
    )


def test_wrong_http_method():
    """Negative test: wrong method (POST instead of GET)"""
    response = requests.get(f"{BASE_URL}/inbox/1/message", headers=headers)
    assert response.status_code in [400, 405], (
        f"Expected 400/405 for wrong HTTP method, got {response.status_code}"
    )
def get_customer_messages():
    url = f"{BASE_URL}/inbox/1/messages/%2B12013507562?user_id=gunalr00%40gmail.com&limit=100&offset=0"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Messages fetch failed: {response.text}"
    messages = response.json()
    print(f"Messages for customer :", messages)
    return messages
def test_customer_message():
    messages = get_customer_messages()
    data = messages.get("messages")[0]
    print(data)
    assert "message_id" in data ,"Message_id not sent properly"
def get_presigned_url():
    url = f"{BASE_URL}/presigned_url?bucket=meena-test-files&key=smile.png"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Messages fetch failed: {response.text}"
    presigned = response.json()
    print(f"Messages for customer :", presigned)
    return presigned
def test_presigned_url():
    presigned_url = get_presigned_url()
    assert presigned_url ,"In vaild key"
def test_send_message():
    payload = {
        "recipient_phone_number": TEST_NUMBER,
        "message_body": "Automation Test"
    }
    url = f"{BASE_URL}/inbox/{INBOX_ID}/message"
    response = requests.post(url, headers=headers, json=payload)

    assert response.status_code == 200, f"GSM send failed: {response.text}"
    data = response.json()
    assert "message_id" in data, f"Missing message_id: {data}"
@pytest.mark.parametrize("filename,content_type", [
    ("smile.png", "image/png"),
])

def test_upload_and_post_message(filename, content_type):
    # Step 1: Request presigned URL for upload
    presign_res = requests.post(
        f"{BASE_URL}/presigned_url",
        json={
            "inbox_name": "Authorizations - Dev",
            "customer_number": "+12013507562",
            "files": [{"filename": filename, "content_type": content_type}],
        },
        headers=headers,
    )

    print("Presign Response:", presign_res.status_code, presign_res.json())
    assert presign_res.status_code == 200, f"Presign failed: {presign_res.text}"

    presign_json = presign_res.json()
    #
    # # Handle different presign response formats
    if filename in presign_json:
        file_info = presign_json[filename]
        url = file_info["url"]
        fields = file_info.get("fields")
        if fields and "key" in fields:
            key = fields["key"]
        else:
            raise AssertionError(f"No file key in presign response: {file_info}")

    print("Presigned URL:", url)
    print("Resolved S3 object key:", key)

    # # Step 2: Upload file to S3
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, "rb") as f:
        if fields:
            # Multipart POST upload
            files = {"file": (filename, f, content_type)}
            upload_resp = requests.post(url, data=fields, files=files)
        else:
            # Simple PUT upload
            upload_resp = requests.put(url, data=f, headers={"Content-Type": content_type})

    assert upload_resp.status_code in (200, 201, 204), \
        f"S3 upload failed: {upload_resp.status_code} {upload_resp.text}"
    print("Upload successful!")
    # # Step 3: Post message with file_key to backend
    #
    message_payload = {
        "recipient_phone_number": "+12013507562",
        "message_body": f"Uploaded file {filename}",
        "file_key": key,
    }
    resp = requests.post(
        f"{BASE_URL}/inbox/1/message",
        json=message_payload,
        headers=headers,
    )

    print("Message Response:", resp.status_code, resp.json())
    assert resp.status_code == 200, f"Message API failed: {resp.text}"

    data = resp.json()
    number = data.get("recipient") or data.get("recipient_phone_number") or data.get("customer_number")
    assert number == "+12013507562", f"Unexpected phone number in response: {data}"

    returned_file_key = data.get("key") or data.get("file_key")
    if returned_file_key:
        assert returned_file_key == key, f"File key mismatch: expected {key}, got {returned_file_key}"

    get_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": Key},  # use dynamic key
        ExpiresIn=3600,
    )
    img_resp = requests.get(get_url)
    assert img_resp.status_code == 200, f"Failed to fetch image: {img_resp.text}"
    print("Image fetched, size:", len(img_resp.content))

def get_headers_token(token=None):
    if token:
        return {"Authorization": f"{token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}
def test_post_blank_message():
    """Negative test: POST blank message to a valid thread"""
    headers = get_headers_token(token=VALID_HEADERS)
    payload = {"message": ""}  # empty message
    thread_id = "12345"  # replace with valid thread ID
    response = requests.post(f"{BASE_URL}/inbox/1/message", headers=headers, json=payload)

    assert response.status_code in [400, 403, 422], (
        f"Expected 400/403/422 for blank message, got {response.status_code}"
    )

    try:
        data = response.json()
        assert "error" in data or "message" in data, "Response should contain error details"
    except ValueError:
        pytest.fail("Response is not valid JSON")
@pytest.mark.parametrize("message, description", [
    (1531, "Normal letters exceeding 1530 chars"),  # 1531 letters
    (671, "Emoji exceeding 670 chars")          # 671 emojis
    # (500, "Non-GSM characters exceeding GSM limit"), # Non-GSM example
])
def test_post_message_exceed_limit(message, description):
    """Negative test: sending messages exceeding character limits"""
    headers = get_headers_token(token=VALID_HEADERS)
    payload = {"message": message}
    thread_id = "12345"  # replace with valid thread ID
    response = requests.post(f"{BASE_URL}/inbox/1/message", headers=headers, json=payload)

    assert response.status_code in [400, 422, 403], (
        f"Expected 400/422/403 for {description}, got {response.status_code}"
    )

    try:
        data = response.json()
        assert "error" in data or "message" in data, f"Response should contain error details for {description}"
    except ValueError:
        pytest.fail(f"Response is not valid JSON for {description}")
