# Generated by Django 5.2.4 on 2025-07-19 18:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenant_name', models.CharField(max_length=200, verbose_name='Nombre del Inquilino')),
                ('contact_person', models.CharField(max_length=150, verbose_name='Persona de Contacto')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='Email de Contacto')),
                ('contact_phone', models.CharField(max_length=20, verbose_name='Teléfono de Contacto')),
                ('address', models.TextField(verbose_name='Dirección')),
                ('city', models.CharField(max_length=100, verbose_name='Ciudad')),
                ('state', models.CharField(max_length=100, verbose_name='Estado')),
                ('zip_code', models.CharField(max_length=10, verbose_name='Código Postal')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('assigned_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Usuario Asignado')),
            ],
            options={
                'verbose_name': 'Inquilino',
                'verbose_name_plural': 'Inquilinos',
                'ordering': ['tenant_name'],
            },
        ),
    ]
