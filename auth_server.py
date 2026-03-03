import os

from flask_app import create_app

app = create_app()


if __name__ == "__main__":
    is_debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    flask_port = int(os.environ.get("FLASK_PORT", 5001))
    app.run(host="127.0.0.1", port=flask_port, debug=is_debug)
