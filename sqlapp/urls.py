from rest_framework.urls import path
from .views import (
    CarGetView,
    CarOneView,
    CarDeleteView,
    CarCreateAPIView,
    CarExistsView,
    CarExplainView,
    CarCountView,
    CarAggregateView,
    CarUpdateOrCreateView,
    CarGetOrCreateView,
    CarBulkCreateView,
    CarUpdateAPIView,
    CarEarliestView,
    CarLatestView,
    CarFirstLastView
)


urlpatterns = [
    path('getsql/', CarGetView.as_view()),
    path('getsql/<int:id>/', CarOneView.as_view()),
    path('deletesql/<int:id>/', CarDeleteView.as_view()),
    path('createsql/', CarCreateAPIView.as_view()),
    path('existsql/', CarExistsView.as_view()),
    path('explainsql/', CarExplainView.as_view()),
    path('countsql/', CarCountView.as_view()),
    path('aggregatesql/', CarAggregateView.as_view()),
    path('bulkcreatesql/', CarBulkCreateView.as_view()),
    path('ucsql/', CarUpdateOrCreateView.as_view()),
    path('bulkcreatesql/', CarBulkCreateView.as_view()),
    path('gcsql/', CarGetOrCreateView.as_view()),
    path('updatesql/<int:id>/', CarUpdateAPIView.as_view()),
    path('earlysql/', CarEarliestView.as_view()),
    path('latestsql/', CarLatestView.as_view()),
    path('firstlastsql/', CarFirstLastView.as_view()),
]