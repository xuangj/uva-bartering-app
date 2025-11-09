from django import forms

from .models import Post, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "image"]

class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=15, required=True) 
    class Meta:
        model = Profile
        fields = ["username", "role", "bio", "sustainability_interests", "trading_interests"]
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...',"rows": 3,}),
            "sustainability_interests": forms.CheckboxSelectMultiple(),
            "trading_interests": forms.CheckboxSelectMultiple(),
        }

    # show current username (not working right now for some reason)
    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        self.user_instance = user_instance  # store for clean_username()
        if user_instance:
            self.fields['username'].initial = user_instance.username

    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if another user already has this username
        from django.contrib.auth.models import User
        qs = User.objects.filter(username=username)
        if self.user_instance:
            qs = qs.exclude(pk=self.user_instance.pk)  # allow keeping current username
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

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