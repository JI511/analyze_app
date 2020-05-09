from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'houseplants/index.html', {})


def reddit_images(request):
    return render(request, 'houseplants/reddit_images.html', {})
