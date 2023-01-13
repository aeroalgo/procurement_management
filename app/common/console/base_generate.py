import random
import string
from russian_names import RussianNames
from django.utils import timezone
from app.login.permissions import BASE_GROUPS


class BaseGenerate:
    """
    Класс помошник для генерации фейковых данных
    """

    def __init__(self):
        self.full_name_result = NotImplementedError
        self.fake_email_result = NotImplementedError

    @staticmethod
    def fake_datetime(min_year=1900, max_year=timezone.now().year):
        # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
        start = timezone.datetime(min_year, 1, 1, 00, 00, 00)
        years = max_year - min_year + 1
        end = start + timezone.timedelta(days=365 * years)
        return start + (end - start) * random.random()

    def fake_login(self):
        return self.fake_email_result

    def fake_full_name(self):
        self.full_name_result = RussianNames(output_type='dict').get_person()
        return " ".join(self.full_name_result.values())

    def fake_first_name(self):
        return self.full_name_result.get("name")

    def fake_last_name(self):
        return self.full_name_result.get("surname")

    def fake_middle_name(self):
        return self.full_name_result.get("patronymic")

    def fake_email(self):
        domains = [
            "hotmail.com",
            "gmail.com",
            "aol.com",
            "mail.com",
            "mail.kz",
            "yahoo.com",
        ]
        letters = list(string.ascii_lowercase)
        self.fake_email_result = (
              "".join(random.choice(letters) for i in range(10))
              + "@"
              + random.choice(domains)
        )
        return self.fake_email_result

    @staticmethod
    def fake_password():
        return "admin"

    @staticmethod
    def fake_user_group():
        return random.choice(BASE_GROUPS)[0]

    @staticmethod
    def fake_bool():
        return bool(random.getrandbits(1))
