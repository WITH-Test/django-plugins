from django.db.models.signals import post_migrate

from django_plugins import models as plugins_app
from django_plugins.conf import settings as plugins_settings

from .commands.syncplugins import SyncPlugins


def sync_plugins(sender, verbosity, **kwargs):
    # Different django version have different senders.
    if (hasattr(sender, "name") and sender.name == "django_plugins") or (
        sender == plugins_app
    ):
        SyncPlugins(plugins_settings.PLUGINS_MODULE, False, verbosity).all()


# Plugins must be synced to the database.
post_migrate.connect(sync_plugins)
