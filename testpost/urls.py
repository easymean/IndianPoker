from django.urls import path

from .views import get_string, set_string

app_name = "testpost"

urlpatterns = [
    path("<str:key>", get_string),
    path("<str:key>/<str:text>", set_string),
]