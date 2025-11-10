from django import forms

from .models import Post, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "image", "interest"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "bio", "sustainability_interests", "trading_interests"]
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'}),
            "sustainability_interests": forms.CheckboxSelectMultiple,
            "trading_interests": forms.CheckboxSelectMultiple,
        }