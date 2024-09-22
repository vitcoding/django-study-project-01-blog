from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count  # Avg, Max, Min, Count
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)


def post_list(request, tag_slug=None):
    post_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # pagination: 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    # for updated pagination
    paging = paginator.get_elided_page_range(
        number=page_number, on_each_side=1, on_ends=1
    )
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(
        request,
        "blog/post/list.html",
        {
            "posts": posts,
            "tag": tag,
            "page_obj": paginator.get_page(page_number),
            "paging": paging,
        },
    )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # similar posts list
    post_tags_ids = post.tags.values_list("id", flat=True)
    # fmt: off
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
                                    .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")) \
                                .order_by("-same_tags", "-publish")[:4]
    # fmt: on

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    # extract post with id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s ({cd['email']}) comments: {cd['comments']}"
            )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, "blog/post/share.html", {"post": post, "form": form, "sent": sent}
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


### 03 PostgreSQL weighting search
def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            # default A, B, C, D = 1.0, 0.4, 0.2, 0.1.
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "body", weight="B"
            )
            search_query = SearchQuery(query)
            results = (
                Post.published.annotate(rank=SearchRank(search_vector, search_query))
                .filter(rank__gte=0.3)
                .order_by("-rank")
            )  # Results are filtered to display only those with a rank greater than 0.3.
            ### to change weights: rank = SearchRank(search_vector, search_query, weights=[0.2, 0.4, 0.6, 0.8])
            ### Post.objects.annotate(rank=rank).filter(rank__gte=0.3).order_by('-rank')

    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )


# ### 02 PostgreSQL stemming search
# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []

#     if "query" in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data["query"]

#             # search_vector = SearchVector("title", "body")
#             # search_query = SearchQuery(query)

#             ### config for russian language
#             search_vector = SearchVector("title", "body", config="russian")
#             search_query = SearchQuery(query, config="russian")
#             results = (
#                 Post.published.annotate(
#                     search=search_vector, rank=SearchRank(search_vector, search_query)
#                 )
#                 .filter(search=search_query)
#                 .order_by("-rank")
#             )

#     return render(
#         request,
#         "blog/post/search.html",
#         {"form": form, "query": query, "results": results},
#     )


# ### 01 PostgreSQL basic search
# def post_search(request):
#     form = SearchForm()
#     query = None
#     results = []

#     if "query" in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data["query"]
#             results = Post.published.annotate(
#                 search=SearchVector("title", "body"),
#             ).filter(search=query)

#     return render(
#         request,
#         "blog/post/search.html",
#         {"form": form, "query": query, "results": results},
#     )
