
import os
import sys
from pathlib import Path

# Project root (jahan manage.py aur Lead/Provider/... apps hain) ko path mein daalo
BASE_DIR = Path(__file__).resolve().parent.parent
for p in (BASE_DIR, Path(__file__).resolve().parent, Path.cwd()):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application