
import requests
from requests.auth import HTTPDigestAuth

PUBLIC_KEY = "C3KBNTD0"
PRIVATE_KEY = "7a5f1277-7bb7-4f87-9258-df9a5fafea44"

ENDPOINT_URL = "https://ap-southeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-eIAcyEwh/endpoint/employees"

response = requests.get(
    ENDPOINT_URL,
    auth=HTTPDigestAuth(PUBLIC_KEY, PRIVATE_KEY),
    timeout=30
)

print("Status Code:", response.status_code)
print("Response:", response.json())
