from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'content', 'timestamp', 'reply_to', 'attachment')
    list_filter = ('timestamp', 'sender')
    search_fields = ('content', 'sender__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
