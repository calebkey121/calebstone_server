# server/run.py
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.getenv("CALEBSTONE_HOST", "127.0.0.1")
    port = int(os.getenv("CALEBSTONE_PORT", "5001"))
    debug = os.getenv("CALEBSTONE_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(debug=debug, host=host, port=port)
