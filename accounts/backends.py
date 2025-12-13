from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email')
        if email is None:
            email = username
        
        if email is None or password is None:
            return None
        
        user = None
        try:
            user = User.objects.get(Q(email__iexact=email) | Q(username__iexact=email))
        except User.DoesNotExist:
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

