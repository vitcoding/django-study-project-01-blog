from rest_framework import serializers
from blog.models import Post


### with user permissions
class PostSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        fields = (
            "id",
            "author",
            "title",
            "body",
            "created",
            "status",
            "slug",
        )
        model = Post
        extra_kwargs = {"slug": {"required": True}}
