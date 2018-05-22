from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {'email_address': request.user.email})
