from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from user_app.models import MyUser

class LoginForm(AuthenticationForm):
    class Meta:     
        model = MyUser
        fields = ['username', 'password']


class RegistrForm(UserCreationForm):
    class Meta: 
        model = MyUser
        fields = ['username', 'password1', 'password2']