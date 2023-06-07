from django.contrib import admin
from reviews.models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User,
)


class GenreTitleInline(admin.TabularInline):
    model = GenreTitle
    extra = 0


class TitleAdmin(admin.ModelAdmin):
    inlines = (GenreTitleInline,)
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category',
        'display_genre',
    )
    search_fields = ('name',)
    exclude = ('genre',)
    list_filter = ('year', 'category')
    list_editable = ('category',)
    empty_value_display = '-пусто-'


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
    )
    search_fields = ('username',)
    list_filter = ('role',)
    list_editable = ('role',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Comment)
