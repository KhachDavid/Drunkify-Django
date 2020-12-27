from django.db import models
from django.contrib.auth.models import User


class Mood(models.Model):
    CHOICES_dance = (
        ('Y', 'yes'),
        ('N', 'no'),
    )

    CHOICES_sad_or_happy = (
        ('s', 'Sad'),
        ('h', 'Happy'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="")
    dance_or_no = models.CharField(max_length=10, choices=CHOICES_dance)
    sad_or_happy = models.CharField(max_length=10, choices=CHOICES_sad_or_happy)
    tired_or_not = models.CharField(max_length=10, choices=CHOICES_dance)
    alone_or_not = models.CharField(max_length=10, choices=CHOICES_dance)

    def __str__(self):
        return self.dance_or_no
