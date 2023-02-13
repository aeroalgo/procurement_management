from abc import ABC, abstractmethod

import jwt
import requests
from django.conf import settings
from django.core.cache import cache
from fabrique.logger import logger
from keycloak_auth.exceptions import CustomAuthenticationFailed
from rest_framework import exceptions


class AbstractKeyCloak(ABC):
    keycloak_content_type_post_header = "application/x-www-form-urlencoded"
    grant_type_authorization_code = "authorization_code"
    grant_type_client_credentials = "client_credentials"
    grant_type_password = "password"
    grant_type_refresh_token = "refresh_token"

    @abstractmethod
    def token(self, data, grant_type: str):
        """получение токена по grant_type"""
        pass


class KeyCloak(AbstractKeyCloak):
    def __init__(
        self, server_url, realm_name, client_id, client_secret_key, redirect_uri=None
    ):
        self.server_url = server_url
        self.realm_name = realm_name
        self._client_id = client_id
        self._client_secret_key = client_secret_key
        self.redirect_uri = redirect_uri

        base_endopoint_url = self.server_url + "/realms/" + self.realm_name
        # эндпоинты keycloak
        self.auth_endpoint = (
            base_endopoint_url
            + "/protocol/openid-connect/auth/?response_type=code&"
            + "client_id="
            + client_id
        )
        if redirect_uri:
            self.auth_endpoint += f"&redirect_uri={self.redirect_uri}"
        self.logout_endpoint = base_endopoint_url + "/protocol/openid-connect/logout"
        self.client_endpoint = base_endopoint_url + "/clients"
        self.token_introspection_endpoint = (
            base_endopoint_url + "/protocol/openid-connect/token/introspect"
        )
        self.token_endpoint = base_endopoint_url + "/protocol/openid-connect/token"
        self.userinfo_endpoint = (
            base_endopoint_url + "/protocol/openid-connect/userinfo"
        )
        self.public_key_endpoint = base_endopoint_url

    @property
    def public_key(self):
        cache_key = "keycloak_public_key"
        public_key = cache.get(cache_key)
        if public_key is None:
            response = requests.request("GET", self.public_key_endpoint, verify=False)
            if not response.ok:
                logger.warning(
                    event="KeyClock__public_key",
                    message="Response keycloak public_key isn't ok",
                    payload__token_endpoint=self.public_key_endpoint,
                    payload__response=response.content,
                )
                raise CustomAuthenticationFailed(
                    detail=response.json(), status_code=401
                )
            public_key_from_response = response.json()["public_key"]
            public_key = (
                "-----BEGIN PUBLIC KEY-----\n"
                + public_key_from_response
                + "\n-----END PUBLIC KEY-----"
            )
            cache.set(cache_key, public_key, 60 * 10)
        return public_key

    def decode_jwt_token(self, token):
        return jwt.decode(
            token, key=self.public_key, audience="eNPS", algorithms="RS256"
        )

    def token(self, data, grant_type: str) -> dict:
        """
        получение/обновление токена в зависимости от grant_type.
        если grant_type = password, то пользователь аутентифицируется в keycloak
        и получает токен и рфефреш токен
        если grant_type = refresh_token, то токен пользователя обновляется
        """
        headers = {
            "Content-Type": self.keycloak_content_type_post_header,
        }
        payload = {
            "grant_type": grant_type,
            "client_id": self._client_id,
            "client_secret": self._client_secret_key,
        }
        if data:
            payload.update(data)
        if self.redirect_uri:
            payload.update({"redirect_uri": self.redirect_uri})
        response = requests.request(
            "POST", self.token_endpoint, verify=False, headers=headers, data=payload
        )
        if not response.ok:
            logger.warning(
                event="KeyClock__token",
                message="Response keycloak token isn't ok",
                payload__token_endpoint=self.token_endpoint,
                payload__headers=headers,
                payload__data=payload,
                payload__response=response.content,
            )
            raise CustomAuthenticationFailed(detail=response.json(), status_code=401)
        return response.json()

    def logout(self, refresh_token: str) -> int:
        """Логаут пользователя в кейклок"""
        headers = {"Content-Type": self.keycloak_content_type_post_header}
        payload = {
            "refresh_token": refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret_key,
        }
        try:
            response = requests.request(
                "POST",
                self.logout_endpoint,
                verify=False,
                headers=headers,
                data=payload,
            )
        except Exception as e:
            logger.error(e)
            raise exceptions.APIException(detail="error request")
        if not response.ok:
            raise CustomAuthenticationFailed(detail=response.json(), status_code=401)
        return response.status_code

    def introspect(self, token):
        """получение информации по токену. Идентично извелечению информации из токена (utils.decode_jwt_token)"""

        payload = {
            "token": token,
            "client_id": self._client_id,
            "client_secret": self._client_secret_key,
        }
        headers = {
            "Content-Type": self.keycloak_content_type_post_header,
            "Authorization": token,
        }
        try:
            response = requests.request(
                "POST", self.token_introspection_endpoint, data=payload, headers=headers
            )
        except Exception as e:
            logger.error(e)
            raise exceptions.APIException(
                detail=f"error request to {self.token_introspection_endpoint}"
            )
        return response.json()

    def is_token_active(self, token):
        introspect_token = self.introspect(token)
        is_active = introspect_token.get("active", False)
        return is_active


class MetaSingleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super().__call__(*args, **kwargs)
        return cls._instance[cls]


class KeyCloakConnect(metaclass=MetaSingleton):
    def __init__(self):
        config = settings.KEYCLOAK_CONFIG
        server_url = config.get("KEYCLOAK_SERVER_URL")
        realm = config.get("KEYCLOAK_REALM")
        client_id = config.get("KEYCLOAK_CLIENT_ID")
        client_secret_key = config.get("KEYCLOAK_CLIENT_SECRET")
        redirect_uri = config.get("KEYCLOAK_REDIRECT_URI")
        if server_url is None:
            raise exceptions.APIException("KEYCLOAK_SERVER_URL отсутствует")
        if realm is None:
            raise exceptions.APIException("KEYCLOAK_REALM отсутствует")
        if client_id is None:
            raise exceptions.APIException("KEYCLOAK_CLIENT_ID отсутствует")
        if client_secret_key is None:
            raise exceptions.APIException("KEYCLOAK_CLIENT_SECRET отсутствует")
        self.__keycloak_connect = KeyCloak(
            server_url=server_url,
            realm_name=realm,
            client_id=client_id,
            client_secret_key=client_secret_key,
            redirect_uri=redirect_uri,
        )

    def connect(self) -> KeyCloak:
        return self.__keycloak_connect


keycloak = KeyCloakConnect().connect()
