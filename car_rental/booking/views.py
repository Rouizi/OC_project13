from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from booking.models import CreateDeal, ReservationDeal
from booking.forms import CreateDealForm, ReservationDealForm
from django.contrib import messages
from django.contrib.auth.models import User


def index(request):
    """
    The home page of the website which displays all available deals
    """
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
            messages.add_message(request, messages.WARNING, 'Deal not found.')
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
                messages.add_message(request, messages.SUCCESS,
                                     'Your deal has been created.')
            else:
                messages.add_message(request, messages.SUCCESS,
                                     'Your deal has been updated.')
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

            return redirect('index')

    elif deal is not None:
        form = CreateDealForm(initial={'Name': deal.name, 'Fuel': deal.fuel, 'mileage': deal.mileage,
                                       'phone_number': deal.phone_number, 'Location': deal.location,
                                       'price': deal.price, 'car_picture': deal.car_picture, 'Description': deal.description})
        update = True

    else:
        update = False
        form = CreateDealForm()

    return render(request, 'booking/create_deal.html',
                  {'title': title, 'form': form, 'update': update})


@login_required
def requests(request):
    pass


@login_required
def reservations(request, id_deal):
    """Allow users to reserve an available car"""

    title = 'Reservations'

    id_deal = int(id_deal)
    deal = CreateDeal.objects.filter(id=id_deal, available=True)
    if not deal.exists():
        messages.add_message(request, messages.INFO,
                             'No deal found.')
        return redirect('index')

    if request.method == 'POST':
        form = ReservationDealForm(request.POST)
        if form.is_valid():
            reservation = ReservationDeal()
            reservation.check_in = form.cleaned_data['check_in']
            reservation.check_out = form.cleaned_data['check_out']
            reservation.user = request.user
            reservation.deal = deal[0]
            reservation.save()
            """
            RENDRE UN DEAL AVAILABLE SI DIFF == 0
            from datetime import date, timedelta
            print((reservation.check_out - date.today()) == timedelta(days=1))"""
            deal.update(available=False)  # We make the deal not available
            messages.add_message(request, messages.INFO,
                                 'We have send a request to the deal owner, '
                                 'if he does not respond within 3 days the reservation will be canceled.')
            return redirect('index')
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
        messages.add_message(request, messages.INFO,
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
        messages.add_message(request, messages.WARNING,
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
        messages.add_message(request, messages.WARNING,
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
    deal = CreateDeal.objects.filter(id=id_deal, available=True)
    if not deal.exists():
        messages.add_message(request, messages.WARNING,
                             'Deal not found, it has been deleted.')
        return redirect('index')
    deal = deal[0]
    return render(request, 'booking/detail_deal.html', locals())
