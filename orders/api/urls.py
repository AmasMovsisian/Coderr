from django.urls import path
from .views import (
    OrderListCreateView,
    OrderPatchView,
    OrderDeleteView,
)

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="orders-list-create"),


    path("<int:pk>/", OrderPatchView.as_view(), name="orders-patch"),


    path("<int:pk>/", OrderDeleteView.as_view(), name="orders-delete"),
]
