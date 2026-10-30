import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
print("WSGI DEBUG file:", __file__, flush=True)
print("WSGI DEBUG cwd:", os.getcwd(), flush=True)
print("WSGI DEBUG here:", sorted(os.listdir(HERE))[:50], flush=True)
print("WSGI DEBUG var/task:", sorted(os.listdir("/var/task"))[:50], flush=True)

for p in (HERE.parent, HERE, Path.cwd(), Path("/var/task")):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application