from django.urls import path
from . import views
urlpatterns = [
    path('getSafety/', views.getSafetyRatedLocations, name="getSafetyRatedLocations")
]