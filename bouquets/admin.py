from django.contrib import admin
from .models import Bouquet, BouquetComposition

class BouquetCompositionInline(admin.TabularInline):
    model = BouquetComposition
    extra = 1

@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'calculated_price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'user__email')
    inlines = [BouquetCompositionInline]

@admin.register(BouquetComposition)
class BouquetCompositionAdmin(admin.ModelAdmin):
    list_display = ('bouquet', 'flower_item', 'quantity')
    list_filter = ('bouquet__category',)
