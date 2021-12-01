from django.shortcuts import render

def homepage(request):
    context = {
        
    }
    return render(request, 'homepage.html', context)

def homepagepm(request):
    context = {

    }
    return render(request, 'homepagepm.html', context)