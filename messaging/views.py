from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from core.models import Trade

from .models import ChatThread, Message

# returns existing DM thread btwn two users if it exists, or create a new one if not
def get_or_create_dm_thread(user1: User, user2: User) -> ChatThread:
    existing = ChatThread.objects.filter(participants=user1).filter(participants=user2)
    for thread in existing:
        if thread.participants.count() == 2:
            return thread

    thread = ChatThread.objects.create()
    thread.participants.add(user1, user2)
    return thread


# displays user's message inbox page: shows ongoing chat threads and a list of other active users they can start chats with
@login_required
def inbox(request: HttpRequest) -> HttpResponse:
    threads = ChatThread.objects.filter(participants=request.user).order_by("-created_at")
    other_users = User.objects.exclude(id=request.user.id)

    search_query = request.GET.get("search", "")
    if search_query:
        other_users = other_users.filter(username__icontains=search_query)

    return render(request, "message_inbox.html", {
        "threads": threads,
        "other_users": other_users,
        "search_query": search_query,
    })


# displays an ongoing chat thread btwn two users and handles sending new msgs
@login_required
def chat(request: HttpRequest, thread_id: int) -> HttpResponse:
    thread = get_object_or_404(ChatThread, id=thread_id)
    if request.user not in thread.participants.all():
        return HttpResponse(status=403)

    other_user = next((u for u in thread.participants.all() if u != request.user), None)

    if request.method == "POST":
        content = (request.POST.get("content") or "").strip()
        if content:
            Message.objects.create(thread=thread, sender=request.user, content=content)
            return redirect("chat", thread_id=thread.id)

    messages = Message.objects.filter(thread=thread)

    trades = Trade.objects.filter(
        Q(userOne=request.user, userTwo=other_user) |
        Q(userOne=other_user, userTwo= request.user)
    ).order_by("-created_at")

    return render(
        request,
        "chat.html",
        {"messages": messages, "other_user": other_user or request.user, "trades": trades},
    )

# starts new chat thread btwn the current user and another user
@login_required
def start_chat(request: HttpRequest, user_id: int) -> HttpResponse:
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect("inbox")
    thread = get_or_create_dm_thread(request.user, other_user)
    return redirect("chat", thread_id=thread.id)

