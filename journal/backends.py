from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()


class EmailAuthBackend:
    """
    Email + parol orqali autentifikatsiya.
    Django standart username + parol o'rniga ishlatiladi.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # username parametri login formasidan keladi (biz uni email sifatida olamiz)
        email = username or kwargs.get('email')
        if not email or not password:
            return None

        # Email formatini tekshirish
        try:
            validate_email(email)
        except ValidationError:
            return None

        # Foydalanuvchini topish
        try:
            user = User.objects.get(email__iexact=email.strip())
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email__iexact=email.strip()).first()

        # Parolni tekshirish
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        return getattr(user, 'is_active', True)
