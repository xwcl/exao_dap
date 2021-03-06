from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token

from .registrar.models import Datum, Dataset

def home(request):
    if request.user.is_authenticated and request.user.is_active:
        data = Datum.objects.filter(dataset__owner=request.user)
        return render(request, 'home_logged_in.html', {
            'data': data,
            'datasets': request.user.datasets_owned.all(),
            'token': Token.objects.get(user=request.user)
        })
    else:
        return render(request, 'home_logged_out.html')

@login_required
def redirect_to_profile(request):
    return redirect('user_profile', username=request.user.username)

def user_profile(request, username):
    user_of_interest = get_object_or_404(get_user_model(), username=username)
    is_me = user_of_interest == request.user
    data = Datum.objects.filter(dataset__owner=user_of_interest)
    if not is_me:
        data = data.filter(dataset__public=True, state=Datum.DatumState.SYNCED)
    if is_me:
        datasets = user_of_interest.datasets_owned.all()
    else:
        datasets = user_of_interest.datasets_owned.filter(public=True)
    return render(request, 'user_profile.html', {
        'user_of_interest': user_of_interest,
        'is_me': is_me,
        'data': data,
        'datasets': datasets,
    })
