import requests

from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.utils.text import slugify


def blog_index(request):
    page_number = request.GET.get("page", 1)
    if not settings.BLOG_API_URL:
        return redirect("/")
    post_request = requests.get(f"{settings.BLOG_API_URL}posts/").json()

    posts = []
    for post in post_request["posts"]:
        posts.append(
            {
                "id": post["ID"],
                "title": post["title"],
                "slug": post["slug"],
                "thumbnail": post["post_thumbnail"],
                "tags": post["tags"],
                "excerpt": post["excerpt"],
            }
        )

    return render(request, "blog/posts.html", context={"posts": posts})


def blog_tag_view(request, unique_slug):
    response = requests.get(f"{settings.BLOG_API_URL}posts?filter[tag]={unique_slug}")
    if response.status_code != 200:
        return redirect(resolve_url("blog_index"))

    post_response = response.json()

    context = {
        "posts": [],
    }

    for post in post_response["posts"]:
        context["posts"].append(
            {
                "id": post["ID"],
                "title": post["title"],
                "slug": post["slug"],
                "thumbnail": post["post_thumbnail"],
                "tags": post["tags"],
                "excerpt": post["excerpt"],
            }
        )

    return render(request, "blog/posts.html", context=context)


def blog_post(request, unique_slug):
    post_request = requests.get(f"{settings.BLOG_API_URL}posts/slug:{unique_slug}")
    if post_request.status_code != 200:
        return redirect(resolve_url("blog_index"))

    context = {
        "post": post_request.json(),
    }

    return render(request, "blog/post_details.html", context=context)
