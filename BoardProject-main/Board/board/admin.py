
from django.contrib import admin
from .models import *

class AdsCategoryInline (admin.TabularInline):
    model = AdsCategory
    extra = 1  # возможность добавления еще одной категории

class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'title',
                    'get_category_str')
    list_filter = ('author', 'date')

    def get_category_str(self, obj):
        return ', '.join([cat.category.category
                          for cat in obj.adscategory_set.all()])


# Только админ может добавлять новости через админ-панель
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'content')


admin.site.register(Ads, PostAdmin)
admin.site.register(User)
admin.site.register(Category)