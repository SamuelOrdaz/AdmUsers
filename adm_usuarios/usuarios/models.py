from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

 #Modelo para los usuarios           
class ModelUser(AbstractUser):   
    rol = (
        ('administrador', 'administrador'),
        ('distribuidor', 'distribuidor'),
        ('cliente', 'cliente'),
    )
    TipoUsuario = models.CharField(_('Tipo de usuario'),max_length=50,choices=rol, blank=True, null=True, default="")
    CreditosTotales = models.PositiveIntegerField(_('Creditos totales'), null=True, blank=True, default=0)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=True)    
    first_name = models.CharField(_("Nombre"), max_length=150, blank=True)
    is_active = models.BooleanField(_("DESMARCAR SI DESEA SUSPENDER USUARIO"), default=True)   

    class Meta:
        verbose_name = "usuarios"
        verbose_name_plural = "usuarios"
        
    def save(self, *args,**Kwargs):
        content_type = ContentType.objects.get_for_model(ModelUser)
        post_permission = Permission.objects.filter(content_type=content_type)   
             
        if not self.id:      
            content_type = ContentType.objects.get_for_model(AgregarCreditos)
            permission = Permission.objects.filter(content_type=content_type)            
            grupo, creado = Group.objects.get_or_create(name ='Agregar_Creditos') #crear grupo con los permisos change_agregarcreditos y view_agregarcreditos      
            if creado:
                for perm in permission:
                    if perm.codename == "change_agregarcreditos":
                        grupo.permissions.add(perm.id)
                    if perm.codename == "view_agregarcreditos":
                        grupo.permissions.add(perm.id)               
            super().save(*args, **Kwargs)   
            if self.TipoUsuario is not None:
                AgregarCreditos.objects.update_or_create(usuario = (ModelUser(self.id)), TotalCreditos = self.CreditosTotales )  #pasar los creditos del usario logeado al modelo AgregarCreditos
                if self.TipoUsuario != "cliente":    
                    for perm in post_permission: #Asignar los permisos de perfil a los usuarios que no sean clientes
                        self.user_permissions.add(perm.id)
                    for perm in permission:
                        if perm.codename == "delete_agregarcreditos": #Asignar el permiso de borrar creditos para que pueda borrar en CASCADA a los usuarios que no sean clientes 
                            self.user_permissions.add(perm.id) 
                                          
                    if self.TipoUsuario == "distribuidor": #si el usuario logeado es cliente agregarle los permisos delete_perfil para que este pueda borrar clientes en cascada
                        content_type = ContentType.objects.get_for_model(Perfil)
                        permission = Permission.objects.filter(content_type=content_type)
                        for perm in permission:
                            if perm.codename == "delete_perfil":
                                self.user_permissions.add(perm.id)
                    if self.TipoUsuario == "administrador":   #si el usuario logeado es administrador asignarle el grupo de Agregar_Creditos 
                        self.groups.add(grupo)
                    super().save(*args, **Kwargs)
                elif self.TipoUsuario == "cliente": #si es cliente que tenga los permisos de perfil para que modifique su nombre y correo
                    Perfil.objects.update_or_create(usuario = (ModelUser(self.id)), correo = self.email, Nombre = self.first_name)  
                    super().save(*args, **Kwargs)
                    content_type = ContentType.objects.get_for_model(Perfil)
                    permission = Permission.objects.filter(content_type=content_type)
                    for perm in permission:
                        if perm.codename == "view_perfil":
                            self.user_permissions.add(perm.id)
                        elif perm.codename == "change_perfil":
                            self.user_permissions.add(perm.id)
                    super().save(*args, **Kwargs)
        else:
             #condiciones para pode actualizar AgregarCreditos y Perfil al guardar cambios 
            if AgregarCreditos.objects.filter(usuario__username = self.username) != None:
                AgregarCreditos.objects.filter(usuario__username = self.username).update(TotalCreditos = self.CreditosTotales )                      
            
            if Perfil.objects.filter(usuario__username = self.username) != None:
                Perfil.objects.filter(usuario__username = self.username).update(correo = self.email, Nombre = self.first_name)       
            super().save(*args, **Kwargs)  

class Perfil(models.Model):
    usuario =  models.OneToOneField(ModelUser, on_delete = models.CASCADE, null=True, blank=True)
    correo = models.EmailField(_("email"),max_length=100, blank=True, null=True)
    Nombre = models.CharField(_("Nombre"), max_length=150, blank=True)
    
    def save(self, *args,**Kwargs):
        ModelUser.objects.filter(id = self.usuario.id).update(email = self.correo, first_name = self.Nombre) #Actualizar email y correo al guardar cambios en o de Perfil
        super().save(*args, **Kwargs) 
    
    def __str__(self):
        return self.Nombre 
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfil"            

class AgregarCreditos(models.Model):
    usuario = models.OneToOneField(ModelUser, on_delete = models.CASCADE, null=True, blank=True)
    TotalCreditos = models.PositiveIntegerField(_('Creditos totales'), null=True, blank=True, default=0)
    Agregar = models.PositiveIntegerField(_('Agregar Creditos'), null=True, blank=True, default=0)

    def save(self, *args,**Kwargs):
        ModelUser.objects.filter(id = self.usuario.id).update(CreditosTotales = self.TotalCreditos + self.Agregar) #Actualizar CreditosTotales de ModelUser con la suma de TotalCreditos y Agregar del Modelo AgregarCreditos
        Credit = ModelUser.objects.filter(id = self.usuario.id)
        for creditos in Credit:
            self.TotalCreditos = creditos.CreditosTotales
        self.Agregar = 0
        super().save(*args, **Kwargs) 

    def __str__(self):
        return str(self.usuario) 
    
    class Meta:
        verbose_name = "Agregar Creditos"
        verbose_name_plural = "Agregar Creditos"  
        