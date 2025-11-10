from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import PostForm, ProfileForm
from .models import Post, Profile

# --- Pages --- #


# Render listings page
def home(request):
    """Render homepage with all posts (and optional search filters)."""
    posts = Post.objects.all().order_by("-created_at")


    # Category Filter
    catergory_filter = request.GET.get("category")
    name_search = request.GET.get("name")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    if catergory_filter:
        posts = posts.filter(category=catergory_filter)
    if name_search:
        posts = posts.filter(title__icontains=name_search)
    if price_min and price_min.isdigit(): # Ensure input is valid before filtering
        posts = posts.filter(price__gte=price_min)
    if price_max and price_max.isdigit(): # Ensure input is valid before filtering
        posts = posts.filter(price__lte=price_max)    
    context = {
        'posts': posts,
        'categories': Post.CATEGORY,
    }
    name_query = request.GET.get("name")
    if name_query:
        posts = posts.filter(title__icontains=name_query)

    return render(request, "home.html", context)


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


# Profile pages
@login_required
def user_profile(request, username):
    user = request.user
    if hasattr(user, 'profile'):
        form = ProfileForm(instance=user.profile)
    else:
        form = None  # optional fallback
    return render(request, 'profile.html', {'user': user, 'form': form})


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


@login_required
def edit_profile(request, username):
    user = request.user

    if username != user.username:
        return HttpResponseForbidden("You can only edit your own profile")

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile", username=user.username)
    else:
        form = ProfileForm(instance=user.profile)
    
    return render(
        request,
        "profile.html",
        {"form": form, "user": user},
    )
