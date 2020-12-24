from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.views.decorators.csrf import csrf_protect
from spotify.SpotifyAPI import embedify
from .models import Profile

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


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                    request.FILES, 
                                    instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            playlist_data = p_form.data['playlist']
            playlist_data_to_change = embedify(playlist_data)
            u_form.save()
            p_form.save()
            p = Profile.objects.get(playlist=playlist_data)
            if 'embed' not in p.playlist:
                p.playlist = playlist_data_to_change
                p.save()
            messages.success(request, f'Account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'users/edit-profile.html', context)
