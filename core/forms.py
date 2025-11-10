from django import forms

from .models import Post, Profile, Trade


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "image"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["role", "bio", "sustainability_interests", "trading_interests"]
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'}),
            "sustainability_interests": forms.CheckboxSelectMultiple,
            "trading_interests": forms.CheckboxSelectMultiple,
        }


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['item_offered', 'comment']
        widgets = {
            'item_offered': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What will you offer?'})
        }