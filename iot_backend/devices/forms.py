from django import forms
from devices.models import *
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
        'password': forms.PasswordInput(),
    }