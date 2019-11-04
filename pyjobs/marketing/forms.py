from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from pyjobs.marketing.models import Share


class SharingForm(ModelForm):
    class Meta:
        model = Share
        fields = ["user_receiving_email"]

    def save(self, user_sharing, job, commit=True):
        instance = super(SharingForm, self).save(commit=False)
        self.instance.user_sharing = user_sharing
        self.instance.job = job

        if commit:
            self.instance.save()
