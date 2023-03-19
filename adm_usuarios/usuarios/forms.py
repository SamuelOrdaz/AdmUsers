from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm

from .models import ModelUser

#Form por defecto de useradmin
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = ModelUser


#Form por defecto de useradmin para añadir 
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ModelUser
