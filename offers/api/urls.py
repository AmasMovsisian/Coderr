from django.urls import path
from .views import OfferListCreateView
from .views import OfferDetailView
from .views import OfferDetailRetrieveView

urlpatterns = [
    path("", OfferListCreateView.as_view(), name="offers"),
    path("<int:pk>/", OfferDetailView.as_view(), name="offer-detail"),
    path("details/<int:pk>/", OfferDetailRetrieveView.as_view(), name="offer-detail-item"),
]