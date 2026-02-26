from rest_framework.urls import path
from .views import (
    CarAggregateAndAnnotateView,
    CarListCreateAPIView,
    FQView,
    CarSubqueryView,
    CarFuncView)


urlpatterns = [
    path('lc/', CarListCreateAPIView.as_view()),

    path('agg/', CarAggregateAndAnnotateView.as_view()),
    path('fq/', FQView.as_view()),
    path('sub/', CarSubqueryView.as_view()),
    path('func/', CarFuncView.as_view()),
]