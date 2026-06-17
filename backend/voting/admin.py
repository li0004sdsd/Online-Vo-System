from django.contrib import admin
from .models import Poll, Option, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1


class PollAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ['title', 'creator', 'created_at', 'is_active', 'allow_multiple']
    list_filter = ['is_active', 'allow_multiple', 'created_at']
    search_fields = ['title', 'description']


class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'poll', 'option', 'voted_at']
    list_filter = ['voted_at']
    search_fields = ['user__username', 'poll__title', 'option__text']


admin.site.register(Poll, PollAdmin)
admin.site.register(Vote, VoteAdmin)
