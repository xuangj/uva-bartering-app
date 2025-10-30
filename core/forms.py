from django import forms
from .models import Post # Assuming you have an Item model

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Specify the fields you want users to submit from your HTML template
        fields = ['title', 'description']