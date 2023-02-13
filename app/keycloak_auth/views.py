from django.http import HttpResponseRedirect
from keycloak_auth.keycloak import keycloak
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def auth(request):  # noqa
    """
    Схема авторизации:
    1. Мы редиректим тут на KeyCloak
    2. При корретных параметрах запроса ответ будет содержать 303-ий код редиректа с заголовком Location
        в значении url'a ADFS (sts2.x5.ru), в котором откроется форма аутентификации пользователя
    3. После успешной аутентификации пользователя ADFS выполнит редирект на KeyCloak, а KeyCloak выполнит редирект
        на url, переданный при запросе кода авторизации в параметре redirect_uri,
        добавив в него параметр code с кодом авториазции

    Срок действия кода авторизации - 1 минута.
    """
    return HttpResponseRedirect(redirect_to=keycloak.auth_endpoint)
