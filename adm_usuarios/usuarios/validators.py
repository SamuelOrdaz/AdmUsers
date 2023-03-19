import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SpecialCharacters():

    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if not re.findall(special_characters, password):
            raise ValidationError(
                _("La contraseña debe de contener al menos un caracter especial"),
                code='password_no_symbol',
            )
    def get_help_text(self):
        return _(
            "La contraseña debe de contener al menos un caracter especial" 
        )
        
        
class Numbers():
    def validate(self, password, user=None):
        if not re.findall('[0-9]', password):
            raise ValidationError(
                _("La contraseña debe de contener numeros"),
                code='password_no_symbol',
            )
    def get_help_text(self):
        return _(
            "La contraseña debe de contener numeros" 
        )

class SoloNumeros():
    def validate(self, password, user=None):
        if re.findall('[A-Z]', password) or re.findall('[a-z]', password) :
            raise ValidationError(
                _("La contraseña no debe de contener letras"),
                code='password_no_symbol',
            )
    def get_help_text(self):
        return _(
            "La contraseña no debe de contener letras" 
        )