from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('get_employee', 'get_employer', 'get_vacancy', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('employee__username', 'employer__username', 'vacancy__title')
    date_hierarchy = 'created_at'
    list_per_page = 25

    def get_employee(self, obj):
        return obj.employee.username if obj.employee else "Unknown"
    get_employee.short_description = 'Employee'

    def get_employer(self, obj):
        return obj.employer.username if obj.employer else "Unknown"
    get_employer.short_description = 'Employer'

    def get_vacancy(self, obj):
        return obj.vacancy.title if obj.vacancy else "Unknown"
    get_vacancy.short_description = 'Vacancy'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'get_chatroom', 'content_preview', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'sender')
    search_fields = ('content', 'sender__username', 'chatroom__employee__username', 'chatroom__employer__username')
    date_hierarchy = 'created_at'
    list_per_page = 25

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Message'

    def get_chatroom(self, obj):
        return str(obj.chatroom)
    get_chatroom.short_description = 'Chat Room'
