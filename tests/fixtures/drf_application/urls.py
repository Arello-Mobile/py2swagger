from django.conf.urls import url
from rest_framework import routers

from testapp.views import RedefineViewSet
from testapp.views import EmailApiView, decorator_view, CustomViewSet

router = routers.SimpleRouter()
router.register(r'd-view$', RedefineViewSet, base_name='test_base_name')

urlpatterns = [
    url(r'a-view$', EmailApiView.as_view()),
    url(r'b-view$', CustomViewSet.as_view({'get': 'list'})),
    url(r'c-view$', decorator_view),
] + router.urls
