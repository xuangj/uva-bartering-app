from django.contrib import admin
from .models import ChatThread, Message

@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created_at')
    search_fields = ('participants__username',)

    def get_participants(self, obj):
        return ", ".join([u.username for u in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'sender', 'content', 'created_at')
    search_fields = ('sender__username', 'content')
    list_filter = ('created_at',)