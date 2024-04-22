from django.contrib.auth.backends import BaseBackend
from ..models import Advertiser

class AdvertiserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            advertiser = Advertiser.objects.get(email=email)
            if advertiser.check_password(password):
                return advertiser
        except Advertiser.DoesNotExist:
            return None

    def get_user(self, advertiser_id):
        try:
            return Advertiser.objects.get(advertiser_id=advertiser_id)
        except Advertiser.DoesNotExist:
            return None
