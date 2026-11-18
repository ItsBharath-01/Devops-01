import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for complaints
# Note: Data will be lost when the application restarts.
complaints = []


def is_valid_email(email: str) -> bool:
    """Basic validation for email format."""
    if not isinstance(email, str):
        return False
    email = email.strip()
    return "@" in email and "." in email.split("@")[-1] and len(email) >= 5


@app.route("/health", methods=["GET"])
def health_check():
    """Health endpoint returning application status and metadata."""
    return jsonify({
        "status": "healthy",
        "service": "customer-service-complaint-management-system",
        "version": "1.0.0"
    }), 200


@app.route("/complaints", methods=["GET"])
def get_complaints():
    """Retrieve all submitted customer complaints."""
    return jsonify({
        "total": len(complaints),
        "complaints": complaints
    }), 200


@app.route("/complaints", methods=["POST"])
def create_complaint():
    """
    Accept and record a customer complaint.
    Validates required fields, assigns a unique ID, and sets status to Open.
    """
    if not request.is_json:
        return jsonify({
            "error": "Invalid content type",
            "message": "Request payload must be JSON with Content-Type: application/json"
        }), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "error": "Bad Request",
            "message": "JSON body must be a valid object"
        }), 400

    required_fields = ["customer_name", "email", "subject", "description"]
    missing_or_empty = []

    for field in required_fields:
        val = data.get(field)
        if val is None or not isinstance(val, str) or not val.strip():
            missing_or_empty.append(field)

    if missing_or_empty:
        return jsonify({
            "error": "Validation Error",
            "message": f"Missing or empty required field(s): {', '.join(missing_or_empty)}"
        }), 400

    # Validate email
    email = data["email"].strip()
    if not is_valid_email(email):
        return jsonify({
            "error": "Validation Error",
            "message": "Invalid email format provided"
        }), 400

    complaint_id = len(complaints) + 1
    new_complaint = {
        "id": complaint_id,
        "customer_name": data["customer_name"].strip(),
        "email": email,
        "subject": data["subject"].strip(),
        "description": data["description"].strip(),
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    complaints.append(new_complaint)

    return jsonify({
        "message": "Complaint submitted successfully",
        "complaint": new_complaint
    }), 201


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "HTTP method not supported on this endpoint"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
