from django import forms

class MoodForm(forms.Form):
    class Meta:
        fields = ['dance_or_no', 'sad_or_happy', 'tired_or_not', 'alone_or_not']