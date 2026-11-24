"""Production (the container image default). Fails fast if required settings are missing."""

from .base import *

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY")

# Behind TLS, keep these True. The lab serves plain HTTP via port-forward, so gitops sets
# DJANGO_SECURE_COOKIES=false there.
_secure = env.bool("DJANGO_SECURE_COOKIES", default=True)
SESSION_COOKIE_SECURE = _secure
CSRF_COOKIE_SECURE = _secure
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=0)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_TRUSTED_ORIGINS: list[str] = env.list("CSRF_TRUSTED_ORIGINS", default=[])
