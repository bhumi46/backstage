from rest_framework.routers import SimpleRouter

from apps.items.views import ItemViewSet

router = SimpleRouter(trailing_slash=False)
router.register("items", ItemViewSet, basename="item")

urlpatterns = router.urls
