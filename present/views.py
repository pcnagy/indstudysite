from django.shortcuts import render

def present(request):
    context = {

    }
    return render(request, 'present.html', context)
