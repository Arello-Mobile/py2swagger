from django.conf.urls import url
from .urlparser import MockApiView


urlpatterns = [
    url(r'a-view/?$', MockApiView.as_view(), name='a test view'),
    url(r'b-view$', MockApiView.as_view(), name='a test view'),
    url(r'c-view/$', MockApiView.as_view(), name='a test view'),
    url(r'a-view/child/?$', MockApiView.as_view()),
    url(r'a-view/child2/?$', MockApiView.as_view()),
    url(r'another-view/?$', MockApiView.as_view(),
        name='another test view'),
    url(r'view-with-param/(:?<ID>\d+)/?$', MockApiView.as_view(),
        name='another test view'),
    url(r'a-view-honky/?$', MockApiView.as_view(), name='a test view'),
    url(r'view-with-pk/{pk}/?$', MockApiView.as_view(),
        name='another test view'),
]
