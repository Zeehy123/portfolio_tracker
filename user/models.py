from django.db import models
from django.contrib.auth.models import AbstractUser



class CustomUser(AbstractUser):
   id = models.AutoField(db_index=True,
                        primary_key=True)
   
   email = models.EmailField(unique=True, blank=False, null=False)
   first_name = models.CharField(max_length=30, blank=True)
   last_name = models.CharField(max_length=30, blank=True)


def __str__(self):
        return f"{self.user.username}'s Profile"