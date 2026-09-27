from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm

class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'instagram_page_id', 'access_token')
    fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('email', 'instagram_page_id', 'access_token')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'instagram_page_id', 'access_token')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
