from allauth.account.forms import SignupForm
from django import forms

class MyCustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(MyCustomSignupForm, self).__init__(*args, **kwargs)
        # Forzamos al navegador a entender que el usuario NO es el email
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'false',
            'placeholder': 'Nombre de Usuario'
        })
        self.fields['email'].widget.attrs.update({
            'autocomplete': 'email',
            'placeholder': 'Correo Electronico'
        })