# core/forms.py

from django import forms

from .models import Post, Profile, Trade, Report

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'available_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # ... include any other existing widgets you have ...
        }
        fields = ["title", "description", "category", "general_size", "weight", "clothing_size", "price", "image","available_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = True

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
    offered_posts = forms.ModelChoiceField(
        queryset=Post.objects.none(),
        widget=forms.Select(attrs={"class":"form-select"}),  # standard dropdown
        required=True,
        help_text="Select one or more of your posts to offer."
    )

    class Meta:
        model = Trade
        fields = ['offered_posts', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is not None:
            # Only allow offering your own available posts
            self.fields['offered_posts'].queryset = Post.objects.filter(
                poster=user,
                is_available=True,
            )

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        # Only include the field the user needs to fill out
        fields = ['comments'] 
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe why you are reporting this post and user.'})
        }
