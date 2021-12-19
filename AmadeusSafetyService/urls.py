from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('getSafety/', views.getSafetyRatedLocations, name="getSafetyRatedLocations"),
    path('getSafetyFromAddress/', views.getSafetyLocationFromGivenAddress, name="getSafetyRatedLocationsFromAddress"),
    path('getTravelRestictions/', views.getSafeTravelLocations)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)