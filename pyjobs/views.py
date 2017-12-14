from django.shortcuts import render


def home_view(request):
    return render(request, "index.html", context={"user": request.user})

def ads_view(request):
    return render(request, "ads.html", context={"user": request.user})
