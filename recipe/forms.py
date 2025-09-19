from django import forms
from django.contrib.auth.models import User
from django.db import models
from .models import recipemeal, resetpassword


class RecipeForm(forms.ModelForm):
    
    class Meta:
        model = recipemeal
        
        exclude = ["user", "slug"]
        labels = {
            "Description": "Description",
            "title": "Title",
            "date":"Date and Time",
        }