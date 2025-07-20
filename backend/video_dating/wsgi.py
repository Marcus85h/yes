"""
WSGI config for video_dating project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_dating.settings.production")

application = get_wsgi_application()
