from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Max, Count, Q
from core.models import Trade
from django.contrib import messages
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
    thread = ChatThread.objects.create(thread_type="group")
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

@login_required
def inbox(request):
    from django.db.models import Max, Count, Q
    user = request.user
    search_query = (request.GET.get("search") or "").strip()

    # -------------------------------------------------------
    # A. SHOW ALL CONVERSATIONS (DM + GROUPCHAT)
    # -------------------------------------------------------
    conversations = (
        ChatThread.objects
        .filter(participants=user)
        .annotate(
            last_msg_at=Max("messages__created_at"),
            unread_count=Count(
                "messages",
                filter=~Q(messages__sender=user) &
                       ~Q(messages__reads__user=user),
                distinct=True
            )
        )
        .order_by("-last_msg_at")
        .prefetch_related("participants", "messages")
        .distinct()
    )

    # Search within conversations: match ANY participant's username/nickname
    if search_query:
        conversations = conversations.filter(
            Q(participants__username__icontains=search_query) |
            Q(participants__profile__nickname__icontains=search_query)
        ).distinct()

    # -------------------------------------------------------
    # B. "OTHER USERS": Users without an existing DM
    # -------------------------------------------------------

    # Get DM threads (only dm type)
    dm_threads = ChatThread.objects.filter(
        participants=user,
        thread_type="dm"
    )

    # Users in DMs with the current user
    dm_partner_ids = (
        User.objects.filter(chat_threads__in=dm_threads)
        .exclude(id=user.id)
        .values_list("id", flat=True)
    )

    # Other users = not in dm list, matching search
    other_users = None
    if search_query:
        other_users = (
            User.objects.filter(
                Q(username__icontains=search_query) |
                Q(profile__nickname__icontains=search_query)
            )
            .exclude(id=user.id)
            .exclude(id__in=dm_partner_ids)        # ← IMPORTANT: GC doesn't matter
            .order_by("username")
        )

    return render(
        request,
        "message_inbox.html",
        {
            "threads": conversations,
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

    messages_qs = thread.messages.all().select_related("sender", "related_trade")

    # Group messages by consecutive sender
    grouped = []
    current_group = []

    prev_sender_id = None

    for msg in messages_qs:
        if prev_sender_id != msg.sender_id:
            # start new group
            if current_group:
                grouped.append(current_group)
            current_group = [msg]
        else:
            # same sender → same group
            current_group.append(msg)

        prev_sender_id = msg.sender_id

    # append last group
    if current_group:
        grouped.append(current_group)

    # Mark unread messages as read
    from messaging.models import MessageRead

    unread_messages = messages_qs.filter(
        ~Q(sender=request.user) &
        ~Q(reads__user=request.user)
    )

    MessageRead.objects.bulk_create(
        [
            MessageRead(message=msg, user=request.user)
            for msg in unread_messages
        ],
        ignore_conflicts=True  # prevents duplicates
    )

    return render(
        request,
        "chat.html",
        {
            "thread": thread,
            "groups": grouped,
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

