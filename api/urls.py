from django.urls import path
from .views import (
    CarGetView,
    CarGetOneView,
    CarBulkPatchView,
    CarCountView,
    CarAggregateView,
    CarEarliestView,
    CarIteratorView,
    CarExplainView,
    CarCreateAPIView,
    CarDeleteView,
    CarExistsView,
    CarLatestView,
    CarUpdateView,
    CarBulkCreateView,
    CarBulkUpdateView,
    CarInBulkView,
    CarUpdateOrCreateView,
    CarGetOrCreateView,
    CarFirstLastView,
    CarGetToyotasView,
    CarGetOldCarsView
)

urlpatterns = [
    path('get/', CarGetView.as_view()),
    path('delete/<int:pk>/', CarDeleteView.as_view(), name='delete'),

    path('createview/', CarCreateAPIView.as_view()),
    path('cg/', CarGetOrCreateView.as_view()),
    path('cu/', CarUpdateOrCreateView.as_view()),
    path('update/', CarUpdateView.as_view()),

    path('bulkcreate/', CarBulkCreateView.as_view()),
    path('bulkupdate/', CarBulkUpdateView.as_view()),
    path('bulkpatch/', CarBulkPatchView.as_view()),

    path('getone/<int:id>/', CarGetOneView.as_view()),

    path('count/', CarCountView.as_view()),
    path('bulkview/', CarInBulkView.as_view()),
    path('itr/', CarIteratorView.as_view()),
    path('latest/', CarLatestView.as_view()),
    path('early/', CarEarliestView.as_view()),
    path('flv/', CarFirstLastView.as_view()),
    path('ag/', CarAggregateView.as_view()),
    path('exist/', CarExistsView.as_view()),
    path('explain/', CarExplainView.as_view()),

    path('getToyota/', CarGetToyotasView.as_view()),
    path('oldcar/', CarGetOldCarsView.as_view()),
]