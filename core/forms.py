from django import forms

from .models import Post, Profile, Trade, Report

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "image", "category","price","general_size","weight","clothing_size"]


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True) 
    class Meta:
        model = Profile
        fields = ["username", "role", "bio", "sustainability_interests", "trading_interests"]
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...',"rows": 3,}),
            "sustainability_interests": forms.CheckboxSelectMultiple(),
            "trading_interests": forms.CheckboxSelectMultiple(),
        }

    # pre-fill username in edit profile modal
    def __init__(self, *args, **kwargs):
        profile = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if profile:
            self.fields['username'].initial = profile.user.username

    # update username throughout database if user edits it
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.username = self.cleaned_data['username']  # save username to User model
        profile.user.save()
        if commit:
            profile.save()
            self.save_m2m()
        return profile


class PfpForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["pfp"]

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['item_offered', 'comment']
        widgets = {
            'item_offered': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What will you offer?'})
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        # Only include the field the user needs to fill out
        fields = ['comments'] 
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe why you are reporting this post and user.'})
        }
