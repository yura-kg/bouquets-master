from django.contrib import admin
from .models import FlowerItem

@admin.register(FlowerItem)
class FlowerItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'price', 'type', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name', 'user__email')
