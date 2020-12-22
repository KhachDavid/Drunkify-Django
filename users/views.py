from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            emails = User.objects.filter(email=email).first()
            if isinstance(emails, type(None)):
                messages.success(request, f'Account created for {username}!')
                return redirect('login')
            args = {}
            text = "Email is taken"
            args['alert'] = text
            return render(request, 'users/register.html', args)
        else:
            args = {}
            text = "Username is taken"
            args['alert'] = text
            return render(request, 'users/register.html', args)
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html')