from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.views import generic

def home_view(request):
    print(dir(request.user))
    return render(request, "index.html", context={"user":request.user})
