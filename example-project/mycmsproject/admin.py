from django.contrib import admin
from mycmsproject.models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "content", "plugin")
    readonly_fields = ("plugin",)
    fieldsets = (
        (
            None,
            {
                "fields": ("title",),
            },
        ),
        ("plugin", {"fields": ("content", "plugin")}),
    )
