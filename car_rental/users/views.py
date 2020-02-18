from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.forms import SignUpForm, ConnexionForm, EditProfileForm
from django.contrib.auth.decorators import login_required
from users.models import Profile
from django.db import transaction


def signup(request):
    title = 'Signup'
    
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 'Congratulations, you are now a registered user!')
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form ,'title': title})

def log_in(request):
    title = 'Login'
    error = False
    next = request.GET.get('next')
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # We check if the data is correct
            if user and next is None:  # If the returned object is not None
                login(request, user)  # we connect the user
                messages.add_message(request, messages.SUCCESS,
                                     f'You are logged in {username}')
                return redirect('index')
            elif user and next is not None:
                login(request, user)
                return redirect(next)
            else: # otherwise an error will be displayed
                error = True
    else:
        form = ConnexionForm()

    return render(request, 'users/login.html', locals())


def log_out(request):
    logout(request)
    return redirect(reverse('users:log_in'))


@login_required
def profile(request, username):
    title = 'Profile'

    profile_user = get_object_or_404(User, username=username)
    profile = Profile.objects.filter(user=profile_user)
    # We check if the user has a profile image and if not we provide him an avatar
    if profile.exists():
        if profile[0].profile_image:
            user_has_profile_image = True
        else:
            user_has_profile_image = False 
    else: 
         user_has_profile_image = False
    p = Profile()
    p.user = profile_user
    avatar = p.avatar(128)

    return render(request, 'users/profile.html', {'title': title, 'profile': profile, 
                        'avatar': avatar, 'profile_user': profile_user, 'user_has_profile_image': user_has_profile_image})


@login_required
def edit_profile(request):
    title = 'Edit profile'

    if request.method == "POST":
        # request.user.username is the original username
        form = EditProfileForm(request.user.username, request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            phone_number = form.cleaned_data["phone_number"]
            location = form.cleaned_data["location"]
            profile_image = form.cleaned_data["profile_image"]
            user = get_object_or_404(User, id=request.user.id)

            # We use a transaction so that if one of the requests below fails all previous ones are canceled
            with transaction.atomic():
                edit = Profile.objects.filter(user=user)
                if edit.exists():
                    edit = Profile.objects.get(user=user)
                    edit.phone_number = phone_number
                    edit.location = location
                    if profile_image:
                        edit.profile_image = request.FILES['profile_image']
                    edit.save()
                    user.username = username
                    user.save()
                else:
                    edit = Profile(user=user)
                    edit.phone_number = phone_number
                    edit.location = location
                    edit.profile_image = profile_image
                    username = username
                    edit.save()
                    user.save()
                messages.add_message(request, messages.SUCCESS,
                                        'Your changes have been saved.')
                return redirect('users:profile', username=user.username)
    else:
        edit = Profile.objects.filter(user=request.user)
        if edit.exists():
            form = EditProfileForm(request.user.username, {'username': request.user.username,
                                            'phone_number': edit[0].phone_number, 'location': edit[0].location}, request.FILES)
        else:
            form = EditProfileForm(request.user.username, {'username': request.user.username}, request.FILES)

    return render(request, 'users/edit_profile.html', {'title': title, 'form': form})





