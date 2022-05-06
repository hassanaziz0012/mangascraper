from django.urls import path
from main import views


urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
]
