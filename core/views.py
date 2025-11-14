from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render


from .forms import PostForm, ProfileForm, TradeForm
from .models import Post, Profile, Trade
from django.db.models import Q
from messaging.views import get_or_create_dm_thread

# --- Pages --- #


# Render listings page
def home(request):
    """Render homepage with all posts (and optional search filters)."""
    posts = Post.objects.filter(is_available=True).order_by("-created_at")
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
    profiles = Profile.objects.all()

    if user.is_staff:
        return render(request, "moderator_dashboard.html", {"profiles": profiles})
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
    return render(request, "post_form.html", {"form": form, "is_edit": False})


@login_required
def view_post(request, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # Check if current user already made an offer for this listing/post
    existing_trade = Trade.objects.filter(
        item_requested=post, userOne=user
    ).first() # Returns none if no trades exist

    # display trade form if haven't made offer
    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.userOne = request.user
            trade.userTwo = post.poster
            trade.item_requested = post
            trade.post_reference = post
            trade.save()
            return redirect("my_trades")
    else:
        form = TradeForm()

    return render(request, "post.html", {'post': post, 'form': form, 'existing_trade': existing_trade})


# Edits existing post
@login_required
def edit_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if Trade.objects.filter(item_requested=post, status='Accepted').exists():
        return HttpResponseForbidden("You can't edit a post after it's been traded.")
    
    if post.poster != request.user:
        return HttpResponseForbidden("You can only edit your own posts.")
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.poster = post.poster
            edited_post.save()
            messages.success(request, "Post updated successfully!")
            return redirect("view_post", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "post_form.html", {"form": form, "is_edit": True})


# Delete post
@login_required
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)

    if Trade.objects.filter(item_requested=post, status='Accepted').exists():
        return HttpResponseForbidden("You can't delete a post after it's been traded.")
    
    if request.user.is_superuser:
        post.delete()
        return redirect("home")

    if post.poster == request.user:
        post.delete()
        return redirect("home")    

    return HttpResponseForbidden("You can only delete your own posts")
        

# --- Profile --- #

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


@login_required
def delete_profile(request, profile_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not a moderator, you cannot access this action")
    
    profile = get_object_or_404(Profile, id=profile_id)
    target_user = profile.user

    target_user.delete()

    return redirect("moderator_dashboard")



# --- Trades --- #

# See all active trades (offers and listings)
@login_required
def my_trades(request) -> HttpResponse:
    user = request.user

    pending_trades = Trade.objects.filter(
        Q(userOne=request.user) | Q(userTwo=request.user),
        status='Pending'
    )

    accepted_trades = Trade.objects.filter(
        Q(userOne=request.user) | Q(userTwo=request.user),
        status='Accepted'
    )

    denied_trades = Trade.objects.filter(
        Q(userOne=request.user) | Q(userTwo=request.user),
        status='Denied'
    )

    return render(request, "my_trades.html", {"pending_trades": pending_trades, "accepted_trades": accepted_trades, "denied_trades": denied_trades})


# view individual trade, see original post and possible offer
@login_required
def view_trade(request, trade_id: int) -> HttpResponse:
    trade = get_object_or_404(Trade, id=trade_id)
    post = trade.post_reference
    user = request.user

    return render(request, "trade.html", {'trade': trade, 'post': post})


# OP can accept trade offer
@login_required
def accept_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)

    if trade.item_requested.poster != request.user:
        return HttpResponseForbidden("You're not the OP, you cannot accept this offer")
    
    trade.status = 'Accepted'
    trade.item_requested.is_available = False
    trade.item_requested.save() 

    messages.success(request, "Trade Accepted!", extra_tags="trade")

    return redirect('my_trades')


# OP can decline trade offer
@login_required
def deny_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, userTwo=request.user)
    trade.status = 'Denied'
    trade.save()
    return redirect('my_trades')


# Offerer can rescind their offer
@login_required
def delete_trade_offer(request, trade_id):
    trade = get_object_or_404(Trade,id=trade_id, userOne=request.user)

    trade.delete()
    return redirect("my_trades")
