from django.conf import settings
from markup_doc.api.v1.views import ArticleViewSet
from reference.api.v1.views import ReferenceViewSet
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("reference", ReferenceViewSet, basename="reference")
router.register("first_block", ArticleViewSet, basename="first_block")

urlpatterns = router.urls
