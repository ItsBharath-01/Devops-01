import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Binding to 0.0.0.0 allows access from inside containers and local networks
    app.run(host="0.0.0.0", port=port, debug=True)
