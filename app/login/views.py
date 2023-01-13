from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

from app.login.form import CustomAuthenticationForm


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomAuthenticationForm


class Profile(TemplateView):
    template_name = "profile/profile.html"
