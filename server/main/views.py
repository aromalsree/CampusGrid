from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home/index.html')

# for testing html pls use the test view
def test(request):
    return render(request, "home/index.html")