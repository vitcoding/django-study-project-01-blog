from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from blog.models import Post
from .serializers import PostSerializer

from rest_framework import mixins
from rest_framework import generics, permissions

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework.pagination import PageNumberPagination

from .permissions import IsAuthorOrReadOnly

from drf_spectacular.views import SpectacularAPIView
from django.contrib.auth.mixins import LoginRequiredMixin


# for authorized users
class MySpectacularAPIView(LoginRequiredMixin, SpectacularAPIView):
    login_url = "/api-auth/login/?next=/api/schema/"


class CustomSearchFilter(filters.SearchFilter):
    template = "blog_api/search.html"

    def get_search_fields(self, view, request):
        if request.query_params.get("title_only"):
            return ["title"]
        return super().get_search_fields(view, request)


# Filters and Search
class PostList(generics.ListCreateAPIView):
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [
        DjangoFilterBackend,
        # filters.SearchFilter,
        CustomSearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["author"]
    search_fields = ["body", "author__username"]
    ordering_fields = "__all__"
    ordering = ["body"]  # default


### URL filtration (user: .../api/user/1/ - example)
class UserPostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.kwargs["id"]
        return Post.objects.filter(author=user)


### User filtration
# class PostList(generics.ListCreateAPIView):
#     # queryset = Post.objects.all()
#     serializer_class = PostSerializer

#     def get_queryset(self):
#         user = self.request.user
#         return Post.objects.filter(author=user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = (permissions.IsAdminUser,) # permission for view (example)
