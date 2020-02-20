from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from booking.models import CreateDeal
from booking.forms import CreateDealForm
from django.contrib import messages
from django.contrib.auth.models import User



def index(request):
    description = ''
    all_deals = CreateDeal.objects.all()
    if 'order_by' in request.GET:
        order_by = request.GET['order_by']
        all_deals = CreateDeal.objects.all().order_by(order_by)
    return render(request, 'base.html', {'all_deals': all_deals, 'description': description})


@login_required
def create_deal(request, deal=None):
    title = 'Create Deal'


    if request.method == 'POST':
        update = False

        form = CreateDealForm(request.POST, request.FILES)
        if form.is_valid():
            # if the deal exists so the user want to update her deal, so we remove the previous
            # deal from the DB before we save the updated deal
            if deal is not None:
                deal.delete()
                messages.add_message(request, messages.SUCCESS,
                                     'Your deal has been updated.')
            else:
                messages.add_message(request, messages.SUCCESS,
                                     'Your deal has been created.')
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

            return redirect('index')
    elif deal is not None:
        form = CreateDealForm(initial=
            {'Name': deal[0].name, 'Fuel': deal[0].fuel, 'mileage': deal[0].mileage,
             'phone_number': deal[0].phone_number, 'Location': deal[0].location,
             'price': deal[0].price, 'car_picture': deal[0].car_picture, 'Description': deal[0].description})
        update = True

    else:
        update = False
        form = CreateDealForm()

    return render(request, 'booking/create_deal.html', {'title': title, 'form': form, 'update': update})

@login_required
def requests(request):
    pass

@login_required
def reservations(request):
    pass

@login_required
def cars(request):
    title = 'My cars'

    user = get_object_or_404(User, id=request.user.id)
    user_cars = CreateDeal.objects.filter(user=user)

    return render(request, 'booking/user_cars.html', locals())

@login_required
def update_deal(request, id_deal):
    id_deal = int(id_deal)
    deal = CreateDeal.objects.filter(id=id_deal, user=request.user)
    if not deal.exists():
        messages.add_message(request, messages.INFO,
                             'No deal found.')
        return redirect('index')

    return create_deal(request, deal)

@login_required
def delete_deal(request, id_deal):
    title = "Delete deal"

    id_deal = int(id_deal)
    user = get_object_or_404(User, id=request.user.id)
    user_deals = CreateDeal.objects.filter(user=user)
    if not user_deals.exists():
        messages.add_message(request, messages.INFO,
                                        'You have no deal.')

        return redirect('index')

    return render(request, 'booking/confirmation_delete.html', {'title': title, 'id_deal': id_deal})

@login_required
def confirmation_delete(request, id_deal):

    deal = CreateDeal.objects.filter(id=id_deal, user=request.user)
    if not deal.exists():
        messages.add_message(request, messages.INFO,
                                            'Deal not found')
    else:
        deal.delete()
        messages.add_message(request, messages.INFO,
                                            'Your deal has been deleted.')
    return redirect('index')


def detail_deal(request):
    title = 'Detail deal'

    id_deal = request.GET['id_deal']
    deal = CreateDeal.objects.filter(id=id_deal)
    if not deal.exists():
        messages.add_message(request, messages.INFO,
                             'Deal not found, it has been deleted ou updated')
        return redirect('index')
    deal = deal[0]
    return render(request, 'booking/detail_deal.html', locals())


