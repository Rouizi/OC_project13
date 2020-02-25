from django import forms
from django.core.validators import RegexValidator
from bootstrap_datepicker_plus import DatePickerInput
from booking.models import ReservationDeal
import datetime


class ReservationDealForm(forms.ModelForm):

    class Meta:
        model = ReservationDeal
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': DatePickerInput(
                options={
                    "format": "MM/DD/YYYY",
                    "minDate": (datetime.datetime.today()+ datetime.timedelta(days=0)).strftime('%Y-%m-%d'),
                    "maxDate": (datetime.datetime.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
                }
            ),
            'check_out': DatePickerInput(
                options={
                    "format": "MM/DD/YYYY",
                    "minDate": (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                    "maxDate": (datetime.datetime.today()+ datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
                }
            ),
        }

    def min_date(self):
        a = 0
        return

    def clean(self):
        cleaned_data = super(ReservationDealForm, self).clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        if check_in and check_out:
            if check_in > check_out:
                self.add_error("check_in", "Check_in must be before Check_out")
        return cleaned_data



class CreateDealForm(forms.Form):
    Name = forms.CharField(max_length=100)
    Fuel = forms.CharField(max_length=15)
    mileage = forms.IntegerField(label='Mileage(Km)')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(label='Phone', validators=[phone_regex], max_length=17, required=False) 
    Location = forms.CharField(max_length=100)
    price = forms.IntegerField(label='Price(€ for 1 day and 100Km)')
    car_picture = forms.ImageField()
    Description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'style':'width:100%;'}))

    def __init__(self, *args, **kwargs):
        super(CreateDealForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field != self.fields['car_picture']:
                field.widget.attrs['class'] = 'form-control'

    def clean_mileage(self):
        mileage = self.cleaned_data['mileage']
        if mileage < 0:
            raise forms.ValidationError('This field must be positive.')
        return mileage

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError('This field must be positive.')
        return price
        
        