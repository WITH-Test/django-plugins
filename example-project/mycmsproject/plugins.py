from django.urls import path, reverse

from django_plugins.point import PluginPoint

from .views import content_create, content_list, content_read


class ContentType(PluginPoint):
    @property
    def instance_urls(self):
        return [path(r"<int:pk>/", content_read, name=self._suffix("content-read"))]

    def _suffix(self, name):
        return f"{name}-{self.get_plugin().name}"

    @property
    def urls(self):
        return [
            path(r"", content_list, name=self._suffix("content-list")),
            path(r"create/", content_create, name=self._suffix("content-create")),
            # path(r"<int:id>/", content_read, name=self._suffix("content-read"))
        ]

    def get_list_url(self):
        return reverse(self._suffix("content-list"))

    def get_create_url(self):
        return reverse(self._suffix("content-create"))

    def get_read_url(self, content):
        return reverse(self._suffix("content-read"), args=[content.pk])
