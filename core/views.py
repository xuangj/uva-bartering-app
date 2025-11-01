from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import PostForm
from .models import Post, Profile

# --- Pages --- #


# Render listings page
def home(request):
    """Render homepage with all posts (and optional search filters)."""
    posts = Post.objects.all().order_by("-created_at")

    # Filter
    name_query = request.GET.get("name")
    if name_query:
        posts = posts.filter(title__icontains=name_query)

    return render(request, "home.html", {"posts": posts})


# Handle default login
@login_required
def login_redirect_view(request):
    user = request.user
    if user.is_staff:
        return redirect("moderator_dashboard")
    else:
        return redirect("home")


# Only load moderator dashboard if the user is staff
@login_required
def moderator_dashboard(request):
    user = request.user
    if user.is_staff:
        return render(request, "moderator_dashboard.html")
    return HttpResponseForbidden("You are not allowed to access this page.")


# --- Posts --- #


# Allow a user to create a new Post
@login_required
def post_create(request):
    # Check the request method
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)

            # Get the user profile
            try:
                user = request.user
            except Profile.DoesNotExist:
                return HttpResponseForbidden("User profile not found.")

            # Create the post
            new_post.poster = user
            new_post.save()

            return redirect("home")
    else:
        # Handle GET request (user first opens the page)
        # Create an empty form instance
        form = PostForm()

    # Render the template
    return render(request, "post_form.html", {"form": form})
