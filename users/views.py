from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            emails = User.objects.filter(email=email).first()
            if isinstance(emails, type(None)):
                messages.success(request, f'Account created for {username}!')
                form.save()
                return redirect('login')
            args = {}
            text = "Email is taken"
            args['alert'] = text
            return render(request, 'users/register.html', args)
        else:
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')

            if password1 != password2:
                args = {}
                text = "Password Do Not Match"
                args['alert'] = text
                return render(request, 'users/register.html', args)
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