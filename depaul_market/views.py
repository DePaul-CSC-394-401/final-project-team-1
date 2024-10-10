from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def listings(request):
    return render(request, 'explore.html')
