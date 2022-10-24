from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_plugins.signals import django_plugin_disabled, django_plugin_enabled

from .utils import get_plugin_from_string, get_plugin_name

ENABLED = 0
DISABLED = 1
REMOVED = 2

STATUS_CHOICES = (
    (ENABLED, _("Enabled")),
    (DISABLED, _("Disabled")),
    (REMOVED, _("Removed")),
)

STATUS_CHOICES_ENABLED = (ENABLED,)
STATUS_CHOICES_DISABLED = (
    DISABLED,
    REMOVED,
)


class PluginPointManager(models.Manager):
    def get_point(self, point):
        return self.get(import_string=get_plugin_name(point))


class PluginPoint(models.Model):
    import_string = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=ENABLED)

    objects = PluginPointManager()

    def __str__(self):
        return self.title


class PluginManager(models.Manager):
    def get_plugin(self, plugin: str):
        return self.get(import_string=get_plugin_name(plugin))

    def get_plugins_of(self, point: PluginPoint):
        """
        Return the plugins that implement this PluginPoint.
        Only enabled plugins are returned.
        """
        return self.filter(point__import_string=get_plugin_name(point), status=ENABLED)

    def get_by_natural_key(self, name):
        return self.get(import_string=name)


class Plugin(DirtyFieldsMixin, models.Model):
    """
    Database representation of a plugin.

    Fields ``name`` and ``title`` are synchronized from plugin classes.

    point
        Plugin point.

    import_string
        Full python path to plugin class, including class too.

    name
        Plugin slug name, must be unique within one plugin point.

    title
        Eny verbose title of this plugin.

    index
        Using values from this field plugins are ordered.

    status
        Plugin status.
    """

    point = models.ForeignKey(PluginPoint, on_delete=models.CASCADE)
    import_string = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, default="", blank=True)
    index = models.IntegerField(default=0)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=ENABLED)

    objects = PluginManager()

    class Meta:
        unique_together = (("point", "name"),)
        ordering = ("index", "id")

    def __str__(self):
        if self.title:
            return self.title
        if self.name:
            return self.name
        return self.import_string

    def natural_key(self):
        return (self.import_string,)

    def is_active(self):
        return self.status == ENABLED

    def get_plugin(self):
        plugin_class = get_plugin_from_string(self.import_string)
        return plugin_class()

    def save(self, *args, **kwargs):
        if "status" in self.get_dirty_fields().keys() and self.pk:
            if self.status in STATUS_CHOICES_ENABLED:
                django_plugin_enabled.send(
                    sender=self.__class__, plugin=self.get_plugin()
                )
            else:
                django_plugin_disabled.send(
                    sender=self.__class__, plugin=self.get_plugin()
                )

        return super().save(*args, **kwargs)
