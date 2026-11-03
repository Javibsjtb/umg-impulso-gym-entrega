from django.contrib import admin
from .models import Member, Plan, Membership, Payment, Attendance, AuditEvent

class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

for model in (Member, Plan, Membership, Payment, Attendance, AuditEvent):
    admin.site.register(model, ReadOnlyAdmin)
admin.site.site_header = 'Impulso · mantenimiento'
admin.site.site_title = 'Impulso'
