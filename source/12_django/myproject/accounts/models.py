from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField("전화", max_length=20, blank=True, null=True)
    address = models.CharField("주소", max_length=100, blank=True, null=True)

    def __str__(self):
        return "{}({}-{})".format(self.user.username,
                                    self.phone_number,
                                    self.address)
    