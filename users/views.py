from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('music-player-login')
        else:
            form = UserRegisterForm()
            args = {}
            text = "Username is taken"
            args['alert'] = text
            return render(request, 'users/register.html', args)
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
