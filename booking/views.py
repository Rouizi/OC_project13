from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from booking.models import CreateDeal, ReservationDeal
from booking.forms import CreateDealForm, ReservationDealForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from users.models import LastMessageRead


def index(request):
    """The home page of the website which displays all available deals"""
    description = ''
    
    all_deals = CreateDeal.objects.filter(available=True)
    if 'order_by' in request.GET:
        order_by = request.GET['order_by']
        all_deals = CreateDeal.objects.filter(available=True).order_by(order_by)

    
    return render(request, 'base.html', {'all_deals': all_deals, 'description': description})


@login_required
def create_deal(request, id=None):
    """this view function allow users to create a deal"""
    title = 'Create Deal'

    if id is None or int(id) == 0:
        deal = None
    else:
        id = int(id)
        try:
            deal = CreateDeal.objects.filter(id=id, user=request.user)[0]
        except IndexError:
            messages.add_message(request, messages.ERROR, 'Deal not found.')
            deal = None
            return redirect('index')

    if request.method == 'POST':
        if deal is not None:
            update = True
        else:
            update = False
        form = CreateDealForm(request.POST, request.FILES)

        if form.is_valid():
            if deal is None:  # If there is no update
                deal = CreateDeal()
                deal.name = form.cleaned_data['Name']
                deal.fuel = form.cleaned_data['Fuel']
                deal.mileage = form.cleaned_data['mileage']
                deal.phone_number = form.cleaned_data['phone_number']
                deal.location = form.cleaned_data['Location']
                deal.car_picture = form.cleaned_data['car_picture']
                deal.description = form.cleaned_data['Description']
                deal.price = form.cleaned_data['price']
                deal.user = request.user
                deal.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Your deal has been created.')
            else:
                deal.name = form.cleaned_data['Name']
                deal.fuel = form.cleaned_data['Fuel']
                deal.mileage = form.cleaned_data['mileage']
                deal.phone_number = form.cleaned_data['phone_number']
                deal.location = form.cleaned_data['Location']
                deal.car_picture = form.cleaned_data['car_picture']
                deal.description = form.cleaned_data['Description']
                deal.price = form.cleaned_data['price']
                deal.user = request.user
                deal.save()
                messages.add_message(request, messages.SUCCESS, 'Your deal has been updated.')
            return redirect('index')

    elif deal is not None:
        form = CreateDealForm(initial={
            'Name': deal.name, 'Fuel': deal.fuel, 'mileage': deal.mileage,
            'phone_number': deal.phone_number, 'Location': deal.location,
            'price': deal.price, 'car_picture': deal.car_picture, 'Description': deal.description
        })
        update = True
        
    else:
        update = False
        form = CreateDealForm()

    return render(request, 'booking/create_deal.html',
                  {'title': title, 'form': form, 'update': update})


@login_required
def user_requests(request):
    """List all requests of a user"""
    
    title = "My requests"

    if 'accept' in request.GET and 'id_deal' in request.GET:
        accept = request.GET['accept']
        id_deal = request.GET['id_deal']
        if accept == 'True':
            deal = get_object_or_404(CreateDeal, id=int(id_deal))
            user_request = get_object_or_404(ReservationDeal, user_owner=request.user, deal=deal, requested=True)
            # We use a transaction so that if one of the requests below fails all previous ones are canceled
            try:
                with transaction.atomic():
                    user_request.canceled = False
                    user_request.accepted = True
                    user_request.requested = False
                    user_request.save()
                    deal.available = False
                    deal.save()
            except IntegrityError:
                messages.add_message(
                    request, messages.ERROR,
                    'An internal error has occurred. Please try your request again.')
                return redirect('index')
        elif accept == 'False':
            deal = get_object_or_404(CreateDeal, id=int(id_deal))
            user_request = get_object_or_404(ReservationDeal, user_owner=request.user, deal=deal, requested=True)
            try:
                with transaction.atomic():
                    user_request.canceled = False
                    user_request.accepted = False
                    user_request.requested = False
                    user_request.save()
                    deal.available = True
                    deal.save()
            except IntegrityError:
                messages.add_message(
                    request, messages.ERROR,
                    'An internal error has occurred. Please try your request again.')
                return redirect('index')

    user_requests = ReservationDeal.objects.filter(user_owner=request.user)

    return render(request, 'booking/user_requests.html', {'title': title, 'user_requests': user_requests})


@login_required
def user_reservations(request):
    """List all reservations of a user"""

    title = 'My reservations'

    if 'cancel' in request.GET and 'id_deal' in request.GET:
        cancel = request.GET['cancel']
        id_deal = request.GET['id_deal']
        if cancel == 'True':
            deal = get_object_or_404(CreateDeal, id=int(id_deal))
            user_reservation = get_object_or_404(ReservationDeal, user_reserve=request.user, deal=deal, requested=True)
            # We use a transaction so that if one of the requests below fails all previous ones are canceled
            try:
                with transaction.atomic():
                    user_reservation.canceled = True
                    user_reservation.accepted = False
                    user_reservation.requested = False
                    user_reservation.save()
                    deal.available = True
                    deal.save()
            except IntegrityError:
                messages.add_message(
                    request, messages.ERROR,
                    'An internal error has occurred. Please try your request again.')
                return redirect('index')
      
    user_reservations = ReservationDeal.objects.filter(user_reserve=request.user)  

    return render(request, 'booking/user_reservations.html', {'title': title, 'user_reservations': user_reservations})


@login_required
def reservations(request, id_deal):
    """Allow users to reserve an available car"""

    title = 'Reservations'

    id_deal = int(id_deal)
    deal = CreateDeal.objects.filter(id=id_deal, available=True)
    if not deal.exists():
        messages.add_message(request, messages.ERROR,
                             'No deal found.')
        return redirect('index')

    if deal[0].user == request.user:
        messages.add_message(request, messages.ERROR,
                             'You cannot book your own deal.')
        return redirect('index')

    if request.method == 'POST':
        form = ReservationDealForm(request.POST)
        if form.is_valid():
            reservation = ReservationDeal()
            try:
                with transaction.atomic():
                    reservation.check_in = form.cleaned_data['check_in']
                    reservation.check_out = form.cleaned_data['check_out']
                    reservation.requested = True
                    reservation.canceled = False
                    reservation.accepted = False
                    reservation.user_owner = deal[0].user
                    reservation.user_reserve = request.user
                    reservation.deal = deal[0]
                    reservation.save()
                    deal.update(available=False)  # We make the deal not available
                    messages.add_message(
                        request, messages.WARNING,
                        'We have send a request to the deal owner, '
                        'if he does not respond tomorrow the reservation will be canceled.')
                    return redirect('index')
            except IntegrityError:
                form.errors['internal'] = "An internal error has occurred. Please try your request again."
                
    else:
        form = ReservationDealForm()

    return render(request, 'booking/reservations.html',
                  {'title': title, 'form': form, 'deal': deal[0]})


@login_required
def user_cars(request):
    """Display all deals of a user"""

    title = 'My cars'

    user = get_object_or_404(User, id=request.user.id)
    user_cars = CreateDeal.objects.filter(user=user)

    return render(request, 'booking/user_cars.html', locals())


@login_required
def update_deal(request, id_deal):
    """Redirect to 'create_deal' view function to update the deal"""

    id_deal = int(id_deal)
    deal = CreateDeal.objects.filter(id=id_deal, user=request.user)
    if not deal.exists():
        messages.add_message(request, messages.ERROR,
                             'No deal found.')
        return redirect('index')

    return redirect('booking:create_deal', id=deal[0].id)


@login_required
def delete_deal(request, id_deal):
    """Allow users to delete her deals, return to a confirmation page"""
    
    id_deal = int(id_deal)
    user = get_object_or_404(User, id=request.user.id)
    user_deal = CreateDeal.objects.filter(id=id_deal, user=user)
    if not user_deal.exists():
        messages.add_message(request, messages.ERROR,
                             'Deal not found.')

        return redirect('index')

    return redirect('booking:confirmation_delete', id_deal=id_deal)
    


@login_required
def confirmation_delete(request, id_deal):
    """this view function is called before deleting a deal to confirm the deletion"""

    title = "Confirmation delete deal"

    id_deal = int(id_deal)
    deal = CreateDeal.objects.filter(id=id_deal, user=request.user)
    if not deal.exists():
        messages.add_message(request, messages.ERROR,
                             'Deal not found.')
        return redirect('index')
    else:
        if 'delete' in request.GET:
            delete = request.GET['delete']
            if delete == 'True':
                deal.delete()
                messages.add_message(request, messages.SUCCESS, 'Your deal has been deleted.')
                return redirect('index')

        return render(request, 'booking/confirmation_delete.html', 
            {'title': title, 'id_deal': id_deal}
        )


def detail_deal(request):
    """Display details of a deal"""

    title = 'Detail deal'

    id_deal = request.GET['id_deal']
    deal = CreateDeal.objects.filter(id=id_deal)
    # If user want to see her deal we display it to him
    if deal[0].user == request.user:
        deal = CreateDeal.objects.filter(id=id_deal, user=request.user)
    else:
        deal = CreateDeal.objects.filter(id=id_deal, available=True)
    if not deal.exists():
        messages.add_message(request, messages.ERROR,
                             'Deal not found, it has been deleted.')
        return redirect('index')
    deal = deal[0]
    return render(request, 'booking/detail_deal.html', locals())
