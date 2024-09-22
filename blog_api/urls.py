from django.urls import path, re_path
from .views import PostList, PostDetail, UserPostList, MySpectacularAPIView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("<int:pk>/", PostDetail.as_view(), name="post_detail"),
    path("", PostList.as_view(), name="post_list"),
    re_path("^user/(?P<id>.+)/$", UserPostList.as_view()),  # URL filtration
    # path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # for authorized users
    path("schema/", MySpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),  # Docs var 1
    # path(
    #     "schema/swagger-ui/",
    #     SpectacularSwaggerView.as_view(url_name="schema"),
    #     name="swagger-ui",
    # ),  # Docs var 2
]
