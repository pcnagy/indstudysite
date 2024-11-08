from django.shortcuts import render

def homepage(request):
    context = {
        
    }
    return render(request, 'homepage.html', context)

def homepagepm(request):
    context = {

    }
    return render(request, 'homepagepm.html', context)

from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Hello, this is a test view!")