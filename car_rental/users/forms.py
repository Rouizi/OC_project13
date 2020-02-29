from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator


class SignUpForm(UserCreationForm):
   
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    # I added this function so that the email is unique
    def clean_email(self):
        """This function return an error message if the email has already been taken"""

        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This Email has already been taken')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(ConnexionForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class EditProfileForm(forms.Form):
    username = forms.CharField(label="Username*")
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    # validators should be a list
    phone_number = forms.CharField(
        label='Phone', validators=[phone_regex], max_length=17, required=False
    )
    location = forms.CharField(label='Location', max_length=100, required=False)
    profile_image = forms.ImageField(label="Image", required=False)

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        for field_name, field in self.fields.items():
            if field != self.fields['profile_image']:
                field.widget.attrs['class'] = 'form-control'

    #  This function ensures that when the user changes his username, he does not take the one of another
    def clean_username(self):
        """This function return an error message if the username has already been taken"""

        username = self.cleaned_data['username']
        if username != self.original_username:
            # The user can not take a username if it is already in the database
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('This username is already taken.')
        return username
