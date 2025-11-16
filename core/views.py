# core/views.py

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q, Exists, OuterRef

from .forms import PostForm, ProfileForm, ReportForm, TradeForm, PfpForm
from .models import Post, Profile, Report, Trade
from messaging.models import Message

from messaging.views import get_or_create_dm_thread
from messaging.utils import (
    notify_trade_offer,
    notify_trade_cancelled,
    notify_trade_accepted,
    notify_trade_denied,
)


# Homepage
from django.db.models import Exists, OuterRef, Subquery
from core.models import Post, Trade


def home(request):
    posts = Post.objects.filter(is_available=True).order_by("-created_at")

    # Filters
    category_filter = request.GET.get("category")
    name_search = request.GET.get("name")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    general_size_filter = request.GET.get("general_size")
    weight_filter = request.GET.get("weight")
    sort_by = request.GET.get("sort_by")

    if category_filter:
        posts = posts.filter(category=category_filter)
    if general_size_filter:
        posts = posts.filter(general_size=general_size_filter)
    if weight_filter:
        posts = posts.filter(weight=weight_filter)
    if name_search:
        posts = posts.filter(title__icontains=name_search)
    if price_min and price_min.isdigit():
        posts = posts.filter(price__gte=price_min)
    if price_max and price_max.isdigit():
        posts = posts.filter(price__lte=price_max)

    # Sorting
    if sort_by == "oldest":
        posts = posts.order_by("created_at")
    elif sort_by == "price_asc":
        posts = posts.order_by("price")
    elif sort_by == "price_desc":
        posts = posts.order_by("-price")
    elif sort_by == "title_asc":
        posts = posts.order_by("title")
    elif sort_by == "title_desc":
        posts = posts.order_by("-title")
    elif sort_by == "available_date_asc":
        posts = posts.order_by("available_date")
    else:
        posts = posts.order_by("-created_at")

    # Pending trade detection
    if request.user.is_authenticated:

        # Subquery that finds a pending trade the user made for this post
        pending_trade_qs = Trade.objects.filter(
            offerer=request.user,     # user who made the offer
            item_requested=OuterRef("pk"),
            status="Pending"
        )

        # Annotate each post with boolean flag
        posts = posts.annotate(
            user_has_pending_trade=Exists(pending_trade_qs),
            pending_trade_id=Subquery(
                pending_trade_qs.values("id")[:1]
            )
        )

    # Context
    context = {
        "posts": posts,
        "categories": Post.CATEGORY,
        "general_sizes": Post.GENERAL_SIZES,
        "weights": Post.WEIGHT_CATEGORIES,
    }

    return render(request, "home.html", context)


# Login redirect
@login_required
def login_redirect_view(request):
    if request.user.is_staff:
        return redirect("moderator_dashboard")
    return redirect("home")


# Moderator Dashboard
@login_required
def moderator_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to access this page.")
    
    profiles = Profile.objects.all()

    name_query = request.GET.get("name")
    role_query = request.GET.get("role")

    if name_query:
        profiles = profiles.filter(user__username__icontains=name_query)
    if role_query:
        profiles = profiles.filter(role=role_query)

    return render(request, "moderator_dashboard.html", {"profiles": profiles})


# View Profile
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Only allow edit form for the owner
    form = ProfileForm(instance=profile_user.profile) if request.user == profile_user else None

    return render(
        request,
        "profile.html",
        {
            "profile_user": profile_user,   # person being viewed
            "logged_user": request.user,    # current user viewing page
            "form": form,
        },
    )


# Edit Profile
@login_required
def edit_profile(request, username):
    if username != request.user.username:
        return HttpResponseForbidden("You can only edit your own profile.")

    profile_user = request.user
    profile = profile_user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile", username=profile_user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile.html", {
        "profile_user": profile_user,
        "form": form,
    })


# Delete User
@login_required
def delete_profile(request, profile_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not a moderator.")

    profile = get_object_or_404(Profile, id=profile_id)
    profile.user.delete()

    return redirect("moderator_dashboard")


# Create Post

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.poster = request.user
            new_post.save()
            return redirect("home")
    else:
        form = PostForm()

    return render(request, "post_form.html", {"form": form, "is_edit": False})


# View Post + Offer Trade

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    can_trade = user != post.poster

    existing_trade = None
    if can_trade:
        existing_trade = Trade.objects.filter(
            offerer=user,
            item_requested=post,
            status='Pending'
        ).first()

    if request.method == "POST":
        if not can_trade:
            return HttpResponseForbidden("You cannot trade with your own listing.")

        if existing_trade:
            messages.error(request, "You already have a pending trade for this post.")
            return redirect("view_post", post_id=post.id)

        form = TradeForm(request.POST, user=user)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.offerer = user
            trade.receiver = post.poster
            trade.item_requested = post
            trade.save()
            form.save_m2m()

            notify_trade_offer(trade)
            messages.success(request, "Trade offer sent!", extra_tags="trade")

            return redirect("my_trades")
    else:
        form = TradeForm(user=user) if can_trade and not existing_trade else None

    return render(request, "post.html", {
        "post": post,
        "form": form,
        "existing_trade": existing_trade,
        "can_trade": can_trade,
    })


# Edit Post

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if Trade.objects.filter(item_requested=post, status='Accepted').exists():
        return HttpResponseForbidden("You can't edit a traded post.")

    if post.poster != request.user:
        return HttpResponseForbidden("You can only edit your own posts.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated!")
            return redirect("view_post", post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "post_form.html", {"form": form, "is_edit": True})


# Delete Post

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if Trade.objects.filter(item_requested=post, status='Accepted').exists():
        return HttpResponseForbidden("You can't delete a traded post.")

    if request.user.is_superuser or post.poster == request.user:
        post.delete()
        return redirect("home")

    return HttpResponseForbidden("You can only delete your own posts.")


# My Trades Page

@login_required
def my_trades(request):
    user = request.user

    def trades(status):
        return Trade.objects.filter(
            Q(offerer=user) | Q(receiver=user),
            status=status
        ).select_related('item_requested', 'offerer', 'receiver').prefetch_related('offered_posts')

    context = {
        "pending_trades": trades('Pending'),
        "accepted_trades": trades('Accepted'),
        "denied_trades": trades('Denied'),
    }

    return render(request, "my_trades.html", context)


# View Trade

@login_required
def view_trade(request, trade_id):
    trade = get_object_or_404(
        Trade.objects.select_related('item_requested', 'offerer', 'receiver').prefetch_related('offered_posts'),
        id=trade_id
    )

    if request.user not in (trade.offerer, trade.receiver) and not request.user.is_staff:
        return HttpResponseForbidden("You are not part of this trade.")

    return render(request, "trade.html", {
        "trade": trade,
        "post": trade.item_requested,
    })


# Accept Trade

@login_required
def accept_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, receiver=request.user)

    if trade.status != 'Pending':
        messages.error(request, "This trade is no longer pending.")
        return redirect("my_trades")

    trade.status = 'Accepted'
    trade.save()

    trade.item_requested.is_available = False
    trade.item_requested.save()

    for offered in trade.offered_posts.all():
        offered.is_available = False
        offered.save()

    notify_trade_accepted(trade, request.user)

    messages.success(request, "Trade accepted!", extra_tags="trade")
    return redirect("my_trades")


# Deny Trade

@login_required
def deny_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, receiver=request.user)

    if trade.status != 'Pending':
        messages.error(request, "This trade is no longer pending.")
        return redirect("my_trades")

    trade.status = 'Denied'
    trade.save()

    notify_trade_denied(trade, request.user)

    messages.info(request, "Trade denied.", extra_tags="trade")
    return redirect("my_trades")


# Withdraw Trade Offer

@login_required
def delete_trade_offer(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, offerer=request.user)

    if trade.status != 'Pending':
        messages.error(request, "You can only withdraw pending trades.")
        return redirect("my_trades")

    notify_trade_cancelled(trade, request.user)

    trade.delete()
    messages.info(request, "Trade offer withdrawn.", extra_tags="trade")
    return redirect("my_trades")


# Report Post

@login_required
def report_post(request, post_id):
    reported_post = get_object_or_404(Post, id=post_id)
    reported_user = reported_post.poster

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.reported_post = reported_post
            report.save()
            return redirect("home")
    else:
        form = ReportForm()

    return render(request, "report_form.html", {
        "reported_post": reported_post,
        "reported_user": reported_user,
        "form": form,
    })


# Change Profile Picture

@login_required
def change_pfp(request, username):
    if username != request.user.username:
        return HttpResponseForbidden("You cannot change someone else's picture.")

    profile = request.user.profile

    if request.method == "POST":
        form = PfpForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile", username=username)
    else:
        form = PfpForm(instance=profile)

    return render(request, "pfp_change_form.html", {"form": form})

@login_required
def make_trade_offer(request, post_id):
    requested_post = get_object_or_404(Post, id=post_id)

    # Check if a pending trade already exists
    existing_trade = Trade.objects.filter(
        offerer=request.user,
        item_requested=requested_post,
        status='Pending'
    ).first()

    # else
    if request.method == "POST":
        # if user has already made a request for the item
        if existing_trade:
            messages.warning(request, "You have already submitted a trade offer for this item.")

        form = TradeForm(request.POST, user=request.user)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.offerer = request.user
            trade.receiver = requested_post.poster
            trade.item_requested = requested_post
            trade.save()

            # Wrap single Post in a list for ManyToManyField
            trade.offered_posts.set([form.cleaned_data['offered_posts']])

            messages.success(request, "Trade offer sent!")
            return redirect('home')
    else:
        form = TradeForm(user=request.user)

    return render(request, "trade_offer_form.html", {
        "form": form,
        "requested_post": requested_post,
    })


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been permanently deleted.")
        return redirect("account_login")  # or homepage

    return redirect("user_profile", username=request.user.username)
