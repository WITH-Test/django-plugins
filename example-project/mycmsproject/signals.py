from typing import Type

from django.dispatch import receiver

from django_plugins.models import Plugin
from django_plugins.signals import django_plugin_disabled, django_plugin_enabled


def enable_plugin(plugin):
    pass


def disable_plugin(plugin):
    pass


@receiver(django_plugin_enabled)
def _django_plugin_enabled(sender: Type[Plugin], plugin, **kwargs):
    enable_plugin(plugin)


@receiver(django_plugin_disabled)
def _django_plugin_disabled(sender: Type[Plugin], plugin, **kwargs):
    disable_plugin(plugin)
