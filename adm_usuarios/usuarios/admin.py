from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import ModelUser, Perfil, AgregarCreditos
from django.utils.translation import gettext_lazy as _
import csv
from django.http import HttpResponse
# Register your models here.

#Función para exportar csv de cualquier modelo en admin
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Exportar"

class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm #hederar los form por defecto
        
class UserAdmin(CustomUserAdmin):
    list_display =  ('username','first_name', 'email', 'TipoUsuario')
    search_fields = ("email", "username", "date_joined")
    list_per_page = 5
    actions = ["export_as_csv"]  #agregar función de exportar csv como action  
    
    def change_view(self, request, object_id): #Funciónes para que aparezcan los grupos al cambiar o agregar, según el usuario tenga el grupo Agregar_Creditos
        if request.user.groups.filter(name='Agregar_Creditos').exists():
            self.fieldsets = (
                (None, {"fields": ("username", "password")}),
                (_("INFORMACIÓN"), {"fields": ("first_name", "email", "TipoUsuario", "CreditosTotales", "is_active")}),
                        (
                    _("Permissions"),
                    {
                        "fields": (
                            "groups",
                        ),
                    },
                )
            ) 
        else:
            self.fieldsets = ((None, {"fields": ("username", "password")}),
                (_("INFORMACIÓN"), {"fields": ("first_name", "email", "TipoUsuario", "CreditosTotales", "is_active")}),
            )
   
        return super(UserAdmin, self).change_view(request,object_id) 
 
    def add_view(self, request):
        if request.user.groups.filter(name='Agregar_Creditos').exists():
            self.add_fieldsets = (
                UserAdmin.add_fieldsets + ((None, {'fields': ('email', 'first_name', 'TipoUsuario', 'CreditosTotales')},),(_("Permissions"),{"fields":("groups",)}))
            )
        else:
            self.add_fieldsets = UserAdmin.add_fieldsets + (
                (None, {'fields': ('email', 'first_name', 'TipoUsuario', 'CreditosTotales')},),
            )          
        return super(UserAdmin, self).add_view(request) 
       
       #Filtrar queryset según el tipo de usuario y lo que se requiere que contenga según este
    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.TipoUsuario == "administrador":    
            return qs.filter(is_superuser = False)
        elif request.user.TipoUsuario == "distribuidor":
            return qs.filter(TipoUsuario = "cliente")
        elif request.user.TipoUsuario == "cliente":
            return qs.filter(username = request.user.username)
    
        #Cambiar list_vew según el tipo de usuario 
    def changelist_view(self, request):
        if not request.user.is_superuser:
            if request.user.TipoUsuario != 'administrador':
                self.list_display =  ('username','first_name',  'email')
            else:
                self.list_display = ('username','first_name', 'email', 'TipoUsuario')
            return super(UserAdmin, self).changelist_view(request)
        else:
            self.list_display = ('username','first_name', 'email', 'TipoUsuario')            
        return super(UserAdmin, self).changelist_view(request)
    
    #Cambiar form para que el admin solo pueda agregar o cambiar distribuidores y el distribuidor solo clientes
    def get_form(self, request, obj=ModelUser, **kwargs):
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)   
        if not request.user.is_superuser:
            if obj is None:
                if request.user.TipoUsuario == "administrador": 
                    form.base_fields["TipoUsuario"].disabled = True   
                    form.base_fields['TipoUsuario'].initial = "distribuidor"  
                if request.user.TipoUsuario == "distribuidor":
                    form.base_fields["TipoUsuario"].disabled = True
                    form.base_fields["TipoUsuario"].initial = "cliente"   
            if obj is not None:
                if request.user.TipoUsuario == "administrador" and obj.TipoUsuario == "distribuidor": 
                    form.base_fields["TipoUsuario"].disabled = True   
                    form.base_fields['TipoUsuario'].initial = "distribuidor"   
                if request.user.TipoUsuario == "distribuidor" and obj.TipoUsuario == "cliente":
                    form.base_fields["TipoUsuario"].disabled = True
                    form.base_fields["TipoUsuario"].initial = "cliente" 
        return form
    
    #Cancelar permiso de cambiar para que el administrador solo pueda cambiar distribuidores
    def has_change_permission(self, request, obj= ModelUser):
        if not request.user.is_superuser:
            if obj is not None:
                if request.user.TipoUsuario == "administrador":
                    if obj.TipoUsuario == "administrador" or obj.TipoUsuario == "cliente":
                        return False
        return True
    
    #Cancelar permiso de borrar para que el administrador solo pueda borrar distribuidores
    def has_delete_permission(self, request, obj= ModelUser):
        if not request.user.is_superuser:
            if obj is not None:
                if request.user.TipoUsuario == "administrador":
                    if obj.TipoUsuario == "administrador" or obj.TipoUsuario == "cliente":
                        return False
        return True
    
    #En caso de que el usuario se cliente no mostrar este modelo
    def get_model_perms(self, request):
        if not request.user.is_superuser:
            if request.user.TipoUsuario == "cliente":
                return {}
        return super(UserAdmin, self).get_model_perms(request)


  
class PerfilAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display =  ('usuario','Nombre', 'correo')    
    exclude = ("usuario",)
    actions = ["export_as_csv"]      
    
    #Filtrar queryset si el usuario es cliente para que solo pueda modificar su propio perfil
    def get_queryset(self, request):
        qs = super(PerfilAdmin, self).get_queryset(request)
        if request.user.TipoUsuario == "cliente":
            return qs.filter(usuario__username = request.user.username)
        return qs
    
    #No mostrar perfil a los distribuidores (caso especial porque tiene permiso para borrar)
    def get_model_perms(self, request):
        if not request.user.is_superuser:
            if request.user.TipoUsuario == "distribuidor":
                return {}
        return super(PerfilAdmin, self).get_model_perms(request)
    
class AgregarCreditosAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display =  ('usuario','TotalCreditos')    
    readonly_fields = ('TotalCreditos',)
    exclude = ('usuario',)
    
    #Filtrar queryset para cuando el usuario no sea superusuario no contenta al superusuario
    def get_queryset(self, request):
        qs = super(AgregarCreditosAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(usuario__is_superuser = False)
        return qs       

    #No mostrar modelo a los usuarios que no tengan tengan el grupo de Agregar_Creditos
    def get_model_perms(self, request):
        if not request.user.groups.filter(name='Agregar_Creditos').exists():
            return {}
        return super(AgregarCreditosAdmin, self).get_model_perms(request)
         
admin.site.register(ModelUser, UserAdmin)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(AgregarCreditos, AgregarCreditosAdmin)

