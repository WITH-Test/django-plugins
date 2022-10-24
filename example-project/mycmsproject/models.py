from django.db import models

from django_plugins.fields import PluginField

from .plugins import ContentType


class Content(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    plugin = PluginField(ContentType, editable=False, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return self.plugin.get_plugin().get_read_url(self)
