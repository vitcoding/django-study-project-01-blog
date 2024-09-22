from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown


register = template.Library()


# @register.simple_tag(name='my_tag')
@register.simple_tag
def total_posts():
    return Post.published.count()


# Создание шаблонного тега включения
@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by("-publish")[:count]
    return {"latest_posts": latest_posts}


# Создание шаблонного тега, возвращающего набор запросов
@register.simple_tag
def get_most_commented_posts(count=5):
    return (
        Post.published.annotate(total_comments=Count("comments"))
        .exclude(total_comments=0)
        .order_by("-total_comments")[:count]
    )


# Создание шаблонного фильтра для поддержки синтаксиса Markdown
@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
