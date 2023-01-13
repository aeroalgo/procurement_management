from django.core import serializers


class ProfileSerializer:
    fields = ("email", "login")

    def __init__(self, data):
        self.data = data
        self.serialize()

    def serialize(self):
        return serializers.serialize("json", self.data, fields=self.fields)
