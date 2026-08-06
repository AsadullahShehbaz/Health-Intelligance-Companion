from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

response = client.post(
    "/chat/stream",
    json={
        "messages": [
            {
                "role": "user",
                "content": "What is diabetes?"
            }
        ]
    }
)

print(response.status_code)
print(response.text)