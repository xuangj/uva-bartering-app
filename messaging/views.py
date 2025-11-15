from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Max
from core.models import Trade

from .models import ChatThread, Message

# returns existing DM thread btwn two users if it exists, or create a new one if not
def get_or_create_dm_thread(user1: User, user2: User) -> ChatThread:
    threads = ChatThread.objects.filter(
        thread_type="dm",
        participants=user1
    ).filter(participants=user2)

    if threads.exists():
        return threads.first()

    thread = ChatThread.objects.create(thread_type="dm")
    thread.participants.add(user1, user2)
    return thread

# group chats
@login_required
def groupchat_create(request):
    if request.method != "POST":
        return redirect("groupchat_select_users")

    selected_ids = request.POST.getlist("selected")
    selected_ids = [int(uid) for uid in selected_ids if uid.isdigit()]

    if len(selected_ids) < 2:
        messages.error(request, "A group chat must include at least 2 other users.")
        return redirect("groupchat_select_users")

    # Create the thread
    thread = ChatThread.objects.create()
    thread.participants.add(request.user)
    thread.participants.add(*selected_ids)

    return redirect("chat", thread_id=thread.id)

@login_required
def groupchat_select_users(request):
    search = request.GET.get("search", "").strip()
    selected_ids = request.GET.getlist("selected")

    # Convert selected list to ints
    selected_ids = [int(uid) for uid in selected_ids if uid.isdigit()]
    selected_users = User.objects.filter(id__in=selected_ids)

    # Search logic
    if search:
        users = User.objects.filter(username__icontains=search).exclude(id=request.user.id)
    else:
        users = User.objects.exclude(id=request.user.id).order_by("username")

    context = {
        "users": users,
        "selected_users": selected_users,
        "search": search,
        "selected_ids": selected_ids,
    }
    return render(request, "create_groupchat.html", context)

# Inbox page
@login_required
def inbox(request):
    user = request.user
    search_query = (request.GET.get("search") or "").strip()

    # Base threads: only show threads with at least one message
    base_threads = (
        ChatThread.objects
        .filter(participants=user)
        .filter(messages__isnull=False)
        .annotate(last_msg_at=Max("messages__created_at"))
        .order_by("-last_msg_at")
        .prefetch_related("participants", "messages")
        .distinct()
    )

    # Filter threads by search (search only usernames)
    if search_query:
        threads = base_threads.filter(participants__username__icontains=search_query)
    else:
        threads = base_threads

    # Other users only shown when searching
    other_users = None
    if search_query:
        # Users already in any shown thread
        users_in_threads = User.objects.filter(
            chat_threads__in=threads
        ).distinct()

        other_users = (
            User.objects.filter(username__icontains=search_query)
            .exclude(id=user.id)
            .exclude(id__in=users_in_threads)
            .order_by("username")
        )

    return render(
        request,
        "message_inbox.html",
        {
            "threads": threads,
            "other_users": other_users,
            "search_query": search_query,
        },
    )

# displays an ongoing chat thread btwn two users and handles sending new msgs
@login_required
def chat(request: HttpRequest, thread_id: int) -> HttpResponse:
    thread = get_object_or_404(ChatThread, id=thread_id)

    if request.user not in thread.participants.all():
        return HttpResponse(status=403)

    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        if content:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content,
                message_type="normal",
            )
            return redirect("chat", thread_id=thread.id)

    messages = thread.messages.all().select_related("sender", "related_trade")

    return render(
        request,
        "chat.html",
        {
            "thread": thread,
            "messages": messages,
            "participants": thread.participants.all(),
        },
    )

# starts new chat thread btwn the current user and another user
@login_required
def start_chat(request: HttpRequest, user_id: int) -> HttpResponse:
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect("inbox")
    thread = get_or_create_dm_thread(request.user, other_user)
    return redirect("chat", thread_id=thread.id)

