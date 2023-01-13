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
        if request.user.id != id and request.user.has_perm("permissions.users.index"):
            profile_data = self.profile_information(id=id)
            return render(request, self.template_name, context=profile_data)

    def profile_information(self, id):
        """Забираем информацию по профилю"""
        # Профиль
        user = UserProfile.objects.get(id=id)
        data = ProfileSerializer(data=[user])
        data.serialize()
        profile_data = data.to_dict[0]
        # Группы
        groups = GroupDirectionSerializer(user.groups.all())
        groups.serialize()
        groups = groups.to_dict
        # Направления
        directions = GroupDirectionSerializer(user.direction.all())
        directions.serialize()
        directions = directions.to_dict
        return {"profile": profile_data, "groups": groups, "directions": directions}
