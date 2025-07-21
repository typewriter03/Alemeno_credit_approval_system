from .settings import *

# Override DATABASES for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",       # In-memory DB for fast, isolated tests
    }
}
