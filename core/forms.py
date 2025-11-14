from django import forms

from .models import Post, Profile, Report


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "image", "category","price"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "bio", "sustainability_interests", "trading_interests"]
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'}),
            "sustainability_interests": forms.CheckboxSelectMultiple,
            "trading_interests": forms.CheckboxSelectMultiple,
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        # Only include the field the user needs to fill out
        fields = ['comments'] 
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe why you are reporting this post and user.'})
        }