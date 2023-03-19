# Generated by Django 4.1.5 on 2023-03-15 01:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modeluser',
            options={'verbose_name': 'usuarios', 'verbose_name_plural': 'usuarios'},
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='ModelUser',
            new_name='usuario',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='NombreUsuario',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='email',
        ),
        migrations.AddField(
            model_name='perfil',
            name='correo',
            field=models.EmailField(blank=True, max_length=100, null=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='modeluser',
            name='CreditosTotales',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Creditos totales'),
        ),
        migrations.AlterField(
            model_name='modeluser',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='AgregarCreditos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TotalCreditos', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Creditos totales')),
                ('Agregar', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Agregar Creditos')),
                ('usuario', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agregar Creditos',
                'verbose_name_plural': 'Agregar Creditos',
            },
        ),
    ]