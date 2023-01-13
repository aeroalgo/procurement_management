from django.shortcuts import render
from app.login.models import UserProfile
from django.http import HttpResponseRedirect
from django.core.exceptions import BadRequest
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from app.login.form import CustomAuthenticationForm
from app.login.serializers import ProfileSerializer, GroupDirectionSerializer


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomAuthenticationForm


class Profile(TemplateView):
    template_name = "profile/profile.html"

    def get(self, request, id):
        user = UserProfile.objects.get(id=id)
        groups = GroupDirectionSerializer(user.groups.all())
        groups.serialize()
        groups = groups.to_dict
        directions = GroupDirectionSerializer(user.direction.all())
        directions.serialize()
        directions = directions.to_dict
        print(directions)
        data = ProfileSerializer(data=[user])
        data.serialize()
        profile_data = data.to_dict[0]
        print(profile_data)
        print(groups)
        return render(request, self.template_name, context={
            "profile": profile_data, "groups": groups, "directions": directions})


    def profile_information(self):
        pass
