# Generated by Django 4.1.5 on 2023-01-12 15:38

import app.login.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_remove_userprofile_role_direction_key_delete_role'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='userprofile',
            managers=[
                ('objects', app.login.models.MyUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='login',
            field=models.CharField(max_length=255, null=True, unique=True, verbose_name='Логин'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='password',
            field=models.CharField(blank=True, default=None, max_length=128, null=True, verbose_name='Пароль'),
        ),
    ]
