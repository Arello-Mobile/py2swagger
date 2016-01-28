from django.conf.urls import patterns, url
from testapp.views import EmailApiView, decorator_view, CustomViewSet

urlpatterns = patterns(
    '',
    url(r'a-view$', EmailApiView.as_view()),
    url(r'b-view$', CustomViewSet.as_view({'get': 'list'})),
    url(r'c-view$', decorator_view),
)