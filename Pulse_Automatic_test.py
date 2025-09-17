import json
import boto3
import requests
import pytest
import os

BASE_URL = "https://ansible.leadgen.pennysaver.in"
LOGIN_ENDPOINT = "https://ansible.leadgen.pennysaver.in/"
# Correct API key
VALID_HEADERS = {"x-api-key": "JePEy20KSPCR7zFTooa5kA=="}
BUCKET_NAME = "meena-test-files"
Key = "smile.png"
# Wrong API key
INVALID_HEADERS = {"x-api-key": "JePEy20KSPCR7zFTooa5kAaa=="}
headers = {
    'x-api-key': 'JePEy20KSPCR7zFTooa5kA==',  # or "x-api-key": API_KEY
    "Content-Type": "application/json"
}
# ---------------- LOGIN NEGATIVE TEST CASES ----------------

@pytest.mark.parametrize("username,password", [
    ("wrong_user", "wrong_pass"),   # completely invalid
    ("valid_user", "wrong_pass"),   # correct username, wrong password
    ("wrong_user", "valid_pass"),   # wrong username, valid password
    ("", "somepass"),               # empty username
    ("someuser", ""),               # empty password
    ("", ""),                       # both empty
    (None, None),                   # missing both
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

##-----------  Inboxes Postive TestCase ---------------------------------------------------------

# boto3 S3 client
s3 = boto3.session.Session(profile_name="meena",region_name="us-east-1")
s3_client = s3.client('s3')
# Get all inboxes
def get_all_inboxes():
    url = f"{BASE_URL}/all_inboxes"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Inbox fetch failed: {response.text}"
    inboxes = response.json()
    print("Inboxes:", inboxes)
    return inboxes
def test_all_inboxes():
    inboxes = get_all_inboxes()
    print('inboxes ->', inboxes[0].get('inbox_id'))
    assert len(inboxes) > 0, "No inbox found"
    first_inbox_id = get_customer_numbers()
    assert first_inbox_id, "No valid inbox ID found"

# Get customer numbers from inbox
def get_customer_numbers():
    url = f"{BASE_URL}/inboxes?user_id=gunalr00@gmail.com"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Customer numbers fetch failed: {response.text}"
    customers = response.json()
    print("Inboxes all:", customers)
    return customers
def test_customer_number():
    customers = get_customer_numbers()
    assert len(customers) > 0, "No customers found in inbox"
    first_customer_id = customers[0].get("inbox_id")
    assert first_customer_id, "No valid customer ID found"
#--------Negative Inbox Test -------

def test_get_all_inboxes_missing_key():
    """Negative test: no API key should return 401/403"""
    response = requests.get(f"{BASE_URL}/all_inboxes")
    assert response.status_code in [401, 403], \
    f"Expected 401/403, got {response.status_code}"

def test_get_all_inboxes_invalid_key():
    """Negative test: wrong API key should return 403"""
    response = requests.get(f"{BASE_URL}/all_inboxes", headers=INVALID_HEADERS)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

def test_get_all_inboxes_wrong_endpoint():
    """Negative test: wrong endpoint should return 404"""
    response = requests.get(f"{BASE_URL}/wrong_inboxes", headers=VALID_HEADERS)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
def test_get_all_inboxes_success():
    """Positive test: valid API key should return 200"""
    response = requests.get(f"{BASE_URL}/all_inboxes", headers=VALID_HEADERS)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert isinstance(response.json(), list), "Expected a list of inboxes"

# #--------------------Postive Thread TestCase ------------------------------------------------
def get_thread():
    url = f"{BASE_URL}/inbox/1/threads?page_size=100&page=1"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200,f"thread fetch failed: {response.text}"
    customer_numbers = response.json()
    print(f"Customer Number:",customer_numbers)
    return customer_numbers
def test_get_thread():
    thread_customer = get_thread()
    assert thread_customer,"No valid"
# #Get inbox for phone number
def get_inbox_phonenumber():
    url = f"{BASE_URL}/inbox/2013507562?user_id=gunalr00%40gmail.com"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Messages fetch failed: {response.text}"
    number = response.json()
    print(f"Phone Number :", number)
    return number
def test_inboxphonenumber():
    phone_number = get_inbox_phonenumber()
    assert phone_number,"Invaild Phone Number"

@pytest.mark.parametrize("inbox_id", [
    "invalid_id",  # invalid format
    "1234",  # non-existing ID
    "!@#$%",  # special chars
])
def test_wrong_inbox_id(inbox_id):
    """Negative test: get inbox with wrong inbox ID"""
    headers = get_headers(token=VALID_HEADERS)
    response = requests.get(f"{BASE_URL}/inboxes/{1}", headers=headers)

    # Accept 400, 403, 404, 422 depending on backend behavior
    if response.status_code == 200:
        data = response.json()
        assert data == {} or data.get("messages") == [] or data.get("count") == 0, (
            f"Expected empty result for wrong inbox_id '{inbox_id}', got {data}"
        )
    else:
        assert response.status_code in [400, 403, 404, 422], (
            f"Expected 400/403/404/422 for wrong inbox_id '{inbox_id}', got {response.status_code}"
        )
##-------------------Thread Negative testCase ------------------------------------------
@pytest.mark.parametrize("filter_type", [
    "invalid_status",   # not read/unread/all
    "",                 # empty filter
    None                # missing filter
])
def test_invalid_filter_type(filter_type):
    """Negative test: invalid filter status"""
    params = {"filter": filter_type} if filter_type is not None else {}
    response = requests.get(f"{BASE_URL}/inbox/1/threads?page_size=100&page=1", headers=headers, params=params)

    if filter_type in ["all"]:  # true invalid
        assert response.status_code in [400, 422], (
            f"Expected 400/422 for invalid filter '{filter_type}', got {response.status_code}"
        )
    elif filter_type in ["", None]:  # treated as default "all"
        assert response.status_code == 200, (
            f"Expected 200 (default behavior) for filter '{filter_type}', got {response.status_code}"
        )

def test_invalid_customer_number_format():
    """Negative test: wrong customer number format"""
    params = {"filter": "all", "customer_number": "abcd1234"}
    response = requests.get(f"{BASE_URL}/inbox/1/threads?page_size=100&page=1", headers=headers, params=params)

    assert response.status_code in [400, 422], (
        f"Expected 400/422 for invalid customer number, got {response.status_code}"
    )


def test_non_existing_customer_number():
    """Negative test: customer number does not exist"""
    params = {"filter": "all", "customer_number": "+9999999999"}  # random non-existing
    response = requests.get(f"{BASE_URL}/inbox/1/threads?page_size=100&page=1", headers=headers, params=params)

    assert response.status_code in [404, 422], (
        f"Expected 200(empty) or 404 or 422, got {response.status_code}"
    )

    if response.status_code == 200:
        data = response.json()
        assert data.get("threads") == [] or data.get("count") == 0, "Should return empty"

def test_wrong_http_method():
    """Negative test: wrong HTTP method"""
    response = requests.post(f"{BASE_URL}/inbox/1/threads?page_size=100&page=1", headers=headers, json={"filter": "all"})
    assert response.status_code in [400, 405], (
        f"Expected 400/405 for wrong method, got {response.status_code}"
    )
def test_get_threads_success():
    """Positive test: fetch threads of a valid inbox"""
    response = requests.get(f"{BASE_URL}/inbox/1/threads?page_size=100&page=1", headers=VALID_HEADERS)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    threads = response.json()
# # ------------------Postive Message TestCase -------------------------------------

def get_customer_messages():
    url = f"{BASE_URL}/inbox/1/messages/%2B12013507562?user_id=gunalr00%40gmail.com&limit=100&offset=0"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Messages fetch failed: {response.text}"
    messages = response.json()
    print(f"Messages for customer :", messages)
    return messages
def test_customer_message():
    messages = get_customer_messages()
    assert messages,"Invalid message_id"

# # Post (send) a message
def send_message():
    url = f"{BASE_URL}/inbox/1/message"
    payload = {
        "recipient_phone_number": "+12013507562",
        "message_body": "Testing"
    }
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 200, f"Send message failed: {response.text}"
    sent_message = response.json()
    print("Sent Message:", sent_message)
    return sent_message
def test_send_message():
    sent_msg = send_message()
    assert "inbox_id" in sent_msg or "message_id" in sent_msg, "Message not sent properly"

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
def test_get_all_inboxes_server_error(monkeypatch):
    """Negative test: simulate 500 server error with monkeypatch"""
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 500
            def json(self):
                return {"detail": "Internal Server Error"}
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    response = requests.get(f"{BASE_URL}/all_inboxes", headers=VALID_HEADERS)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"


def get_headers(token=None):
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}

# ----------------- GET messages negative tests -----------------

@pytest.mark.parametrize("thread_id", [
    "abc",       # invalid format
    "123",       # too short
    "!@#$%",     # special characters
])
def test_get_messages_invalid_thread_id(thread_id):
    """Negative test: invalid thread IDs for GET messages"""
    headers = get_headers(token=VALID_HEADERS)
    response = requests.get(f"{BASE_URL}/inbox/1/messages/%2B12013507562?user_id=gunalr00%40gmail.com&limit=100&offset=0", headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Accept empty result
        assert data == {} or data.get("messages") == [] or data.get("count") == 0, (
            f"Expected empty result for invalid thread_id '{thread_id}', got {data}"
        )
    else:
        # Accept common error codes
        assert response.status_code in [400, 403, 404, 422], (
            f"Expected 400/403/404/422 for invalid thread_id '{thread_id}', got {response.status_code}"
        )


def test_get_messages_missing_thread_id():
    """Negative test: GET messages without thread ID"""
    headers = get_headers(token=VALID_HEADERS)
    response = requests.get(f"{BASE_URL}/inbox/1/messages/%2B12013507562?user_id=gunalr00%40gmail.com&limit=100&offset=0", headers=headers)  # missing ID

    assert response.status_code in [400, 403, 404], (
        f"Expected 400/403/404 for missing thread_id, got {response.status_code}"
    )

    try:
        data = response.json()
        assert "error" in data or "message" in data, "Response should contain error details"
    except ValueError:
        pytest.fail("Response is not valid JSON")
def test_post_blank_message():
    """Negative test: POST blank message to a valid thread"""
    headers = get_headers(token=VALID_HEADERS)
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
@pytest.mark.parametrize("message, description", [
    (1531, "Normal letters exceeding 1530 chars"),  # 1531 letters
    (671, "Emoji exceeding 670 chars"),           # 671 emojis
    (500, "Non-GSM characters exceeding GSM limit"), # Non-GSM example
])
def test_post_message_exceed_limit(message, description):
    """Negative test: sending messages exceeding character limits"""
    headers = get_headers(token=VALID_HEADERS)
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
def test_get_messages_success():
    """Positive test: fetch messages of a valid thread"""
    response = requests.get(f"{BASE_URL}/inbox/1/messages/%2B12013507562?user_id=gunalr00%40gmail.com&limit=100&offset=0", headers=VALID_HEADERS)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    messages = response.json()