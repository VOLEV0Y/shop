from django.shortcuts import render
from .models import Product

def main_page(request):
    return render(request, 'home.html')