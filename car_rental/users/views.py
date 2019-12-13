from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.forms import SignUpForm, ConnexionForm
from django.contrib.auth.decorators import login_required


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
def profile(request):
    title = 'Profile'

    current_user = get_object_or_404(User, id=request.user.id)

    return render(request, 'users/profile.html')


@login_required
def edit_profile(request):
    pass

@login_required
def create_deal(request):
    pass

@login_required
def requests(request):
    pass

@login_required
def reservations(request):
    pass



