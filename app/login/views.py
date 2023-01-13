from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView

from app.login.form import CustomAuthenticationForm
from app.login.models import UserProfile


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomAuthenticationForm


class Profile(TemplateView):
    template_name = "profile/profile.html"

    def get(self, request, id):
        user = UserProfile.objects.get(id=id)
        return HttpResponseRedirect('/')
