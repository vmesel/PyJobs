from django.shortcuts import render


def home_view(request):
    print(dir(request.user))
    return render(request, "index.html", context={"user": request.user})
