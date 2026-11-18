import pytest
from app import app, complaints


@pytest.fixture
def client():
    """Create a test client with a clean complaints storage for each test."""
    app.config["TESTING"] = True
    # Reset in-memory complaints before each test run
    complaints.clear()
    with app.test_client() as test_client:
        yield test_client
    complaints.clear()


def test_health_check(client):
    """Test 1: GET /health returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "customer-service-complaint-management-system"
    assert data["version"] == "1.0.0"


def test_create_complaint_success(client):
    """Test 2: POST /complaints creates a valid complaint with unique ID and 'Open' status."""
    payload = {
        "customer_name": "Rahul",
        "email": "rahul@example.com",
        "subject": "Payment issue",
        "description": "Payment was deducted but order was not confirmed."
    }
    response = client.post("/complaints", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Complaint submitted successfully"
    complaint = data["complaint"]
    assert complaint["id"] == 1
    assert complaint["customer_name"] == "Rahul"
    assert complaint["email"] == "rahul@example.com"
    assert complaint["subject"] == "Payment issue"
    assert complaint["description"] == "Payment was deducted but order was not confirmed."
    assert complaint["status"] == "Open"
    assert "created_at" in complaint


def test_get_complaints(client):
    """Test 3: GET /complaints returns all submitted complaints."""
    # First submit two complaints
    payload1 = {
        "customer_name": "Rahul",
        "email": "rahul@example.com",
        "subject": "Payment issue",
        "description": "Payment was deducted but order was not confirmed."
    }
    payload2 = {
        "customer_name": "Priya",
        "email": "priya@example.com",
        "subject": "Delayed delivery",
        "description": "Product was expected yesterday but not yet received."
    }
    client.post("/complaints", json=payload1)
    client.post("/complaints", json=payload2)

    response = client.get("/complaints")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 2
    assert len(data["complaints"]) == 2
    assert data["complaints"][0]["customer_name"] == "Rahul"
    assert data["complaints"][0]["id"] == 1
    assert data["complaints"][1]["customer_name"] == "Priya"
    assert data["complaints"][1]["id"] == 2


def test_create_complaint_missing_fields(client):
    """Test 4: POST /complaints with missing fields returns 400 Bad Request."""
    payload = {
        "customer_name": "Rahul",
        "email": "rahul@example.com"
        # missing subject and description
    }
    response = client.post("/complaints", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation Error"
    assert "Missing or empty required field" in data["message"]


def test_create_complaint_empty_fields(client):
    """Test 5: POST /complaints with whitespace/empty string values returns 400."""
    payload = {
        "customer_name": "   ",
        "email": "rahul@example.com",
        "subject": "Payment issue",
        "description": ""
    }
    response = client.post("/complaints", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation Error"


def test_create_complaint_invalid_email(client):
    """Test 6: POST /complaints with malformed email returns 400."""
    payload = {
        "customer_name": "Rahul",
        "email": "invalid-email-address",
        "subject": "Refund inquiry",
        "description": "Where is my refund?"
    }
    response = client.post("/complaints", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Validation Error"
    assert "Invalid email format" in data["message"]


def test_create_complaint_non_json_payload(client):
    """Test 7: POST /complaints with non-JSON content type returns 400."""
    response = client.post(
        "/complaints",
        data="This is plain text, not JSON",
        content_type="text/plain"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid content type"
