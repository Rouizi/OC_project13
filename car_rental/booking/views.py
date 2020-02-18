from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from booking.models import CreateDeal
from booking.forms import CreateDealForm
from django.contrib import messages



def index(request):
    description = ''
    all_deals = CreateDeal.objects.all()
    return render(request, 'base.html', {'all_deals': all_deals, 'description': description})


@login_required
def create_deal(request):
    title = 'Create Deal'

    if request.method == 'POST':
        form = CreateDealForm(request.POST, request.FILES)
        if form.is_valid():
            deal = CreateDeal()
            deal.name = form.cleaned_data['Name']
            deal.energie = form.cleaned_data['Energie']
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
            return redirect('index')
    else:
        form = CreateDealForm()

    return render(request, 'booking/create_deal.html', {'title': title, 'form': form})

@login_required
def requests(request):
    pass

@login_required
def reservations(request):
    pass



