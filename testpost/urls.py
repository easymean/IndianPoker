from django.urls import path

from .views import get_set_string, PostViewSet, PostView

app_name = "testpost"

post_list = PostViewSet.as_view(
    {
        "get": "list",
    }
)

urlpatterns = [
    # path("", post_list),
    # path("", PostView.as_view()),
    path("", get_set_string),
]