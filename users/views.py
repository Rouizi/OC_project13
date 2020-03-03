from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.forms import SignUpForm, ConnexionForm, EditProfileForm, MessageForm
from django.contrib.auth.decorators import login_required
from users.models import Profile, Message, LastMessageRead
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import Permission


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
            with transaction.atomic():
                user = authenticate(username=username, password=password)
                login(request, user)
                last_msg_read = LastMessageRead.objects.create(user=request.user, last_message_read_time=timezone.now())
                last_msg_read.save()
                messages.add_message(request, messages.SUCCESS, 'Congratulations, you are now a registered user!')
                return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form, 'title': title})


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
            else:  # otherwise an error will be displayed
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

    return render(request, 'users/profile.html', {
        'title': title, 'profile': profile,
        'avatar': avatar, 'profile_user': profile_user,
        'user_has_profile_image': user_has_profile_image
    })


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
            try:
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
                        user.username = username
                        edit.save()
                        user.save()
                    messages.add_message(request, messages.SUCCESS,
                                            'Your changes have been saved.')
                    return redirect('users:profile', username=user.username)
            except IntegrityError:
                form.errors['internal'] = "An internal error has occurred. Please try your request again."
    else:
        edit = Profile.objects.filter(user=request.user)
        if edit.exists():
            form = EditProfileForm(request.user.username, {
                'username': request.user.username,
                'phone_number': edit[0].phone_number,
                'location': edit[0].location
            },
                request.FILES
            )
        else:
            form = EditProfileForm(request.user.username, {
                'username': request.user.username
            },
                request.FILES
            )

    return render(request, 'users/edit_profile.html', {'title': title, 'form': form})



@login_required
def send_message(request, recipient):
    title = 'Send message'

    if timezone.now() >= request.user.date_joined + timezone.timedelta(minutes=10):
        permission = Permission.objects.get(name="Send Private Message")
        request.user.user_permissions.add(permission)
    if not request.user.has_perm('users.send_private_message'):
        wait_sec = (timezone.timedelta(minutes=10) - (timezone.now() - request.user.date_joined)).seconds
        messages.add_message(request, messages.WARNING,
                    'New users must wait 24 hours before they can send private messages.'
                    '(So that you can test this feature you can send a private '
                    f'message in {wait_sec//60:0>2} min and {wait_sec%60:0>2} sec)')
        return redirect('index')
    user = get_object_or_404(User, username=recipient)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = Message(sender=request.user, recipient=user,
                        body=form.cleaned_data['message'])
            msg.save()
            messages.add_message(request, messages.SUCCESS, 'Your message has been sent.')
            return redirect('index')
    else:
        form = MessageForm()
    return render(request, 'users/send_message.html', {'title': title, 'form': form, 'recipient': recipient})


@login_required
def user_messages(request):
    title = 'Mailbox'

    LastMessageRead.objects.filter(user=request.user).update(last_message_read_time=timezone.now()) 
    msgs = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'users/messages.html', {'title': title, 'msgs': msgs})
