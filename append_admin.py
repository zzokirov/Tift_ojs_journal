with open('journal/admin.py', 'a', encoding='utf-8') as f:
    f.write('''

# --- LOG ENTRY ADMIN ---

from django.contrib.admin.models import LogEntry
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_time', 'action_flag', 'content_type', 'user')
    search_fields = ('object_repr', 'change_message')
    date_hierarchy = 'action_time'
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
''')
