from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

User = get_user_model()


def home(request):
    return render(request, 'home/index.html')


# for testing html pls use the test view
def test(request):
    return render(request, "dashboard/wishlist.html")