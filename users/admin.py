from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'subscription_tier', 'date_joined')
    list_filter = ('subscription_tier', 'is_staff', 'is_superuser')
    search_fields = ('email',)
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('subscription_tier', 'subscription_expires')
        }),
    )
