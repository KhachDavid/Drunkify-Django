from django import forms
from .models import Mood

class MoodForm(forms.ModelForm):
    class Meta:
        model = Mood
        fields = ['dance_or_no', 'sad_or_happy', 'tired_or_not', 'alone_or_not']