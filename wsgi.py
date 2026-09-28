"""
Production WSGI Entrypoint.

Can be run with:
- Gunicorn (Linux/Container): gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
- Waitress (Windows): waitress-serve --port=5000 wsgi:app
"""

from app import create_app
from config.settings import Config

app = create_app(Config)

if __name__ == "__main__":
    app.run()
