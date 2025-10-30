from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm # Import the form you created
from .models import Profile
from django.http import HttpResponseForbidden
@login_required # Ensures only logged-in users can post
def post_create(request):
    # Step 1: Check the request method
    if request.method == 'POST':
        
        # A. Bind the POST data and any files to the form
        form = PostForm(request.POST, request.FILES)
        
        # B. Validate the data against the rules defined in the form and model
        if form.is_valid():
            new_post = form.save(commit=False)
    
            # 🚨 FIX IS HERE: Get the Profile object associated with the User
            try:
                user_profile = request.user.profile # Access the profile linked by OneToOneField
            except Profile.DoesNotExist:
                # Handle case where user is logged in but has no profile
                # (This shouldn't happen but is good practice)
                return HttpResponseForbidden("User profile not found.") 
                
            new_post.poster = user_profile 
            new_post.save()
            
            return redirect('home')

    else:
        # Step 2: Handle GET request (User first opens the page)
        # Create an empty form instance
        form = PostForm()

    # Step 3: Render the template, passing the form instance to the context
    return render(request, 'post_form.html', {'form': form})