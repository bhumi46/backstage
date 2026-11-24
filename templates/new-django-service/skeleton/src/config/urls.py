from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("healthz", core_views.healthz, name="healthz"),
    path("readyz", core_views.readyz, name="readyz"),
    path("", include("django_prometheus.urls")),  # GET /metrics
    path("admin/", admin.site.urls),
    path("api/", include("apps.items.urls")),
]
