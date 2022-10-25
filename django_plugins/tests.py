from django import forms
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from .fields import (
    PluginChoiceField,
    PluginModelChoiceField,
    PluginModelMultipleChoiceField,
)
from .management.commands.syncplugins import SyncPlugins
from .models import DISABLED, ENABLED, REMOVED, Plugin
from .models import PluginPoint as PluginPointModel
from .point import PluginMount, PluginPoint


class MyPluginPoint(PluginPoint):
    pass


class MyPlugin(MyPluginPoint):
    pass


class MyPluginFull(MyPluginPoint):
    name = "my-plugin-full"
    title = _("My Plugin Full")


class MyPlugin2(MyPluginPoint):
    name = "my-plugin-2"
    title = _("My Plugin 2")


class PluginSyncTestCaseBase(TestCase):
    def delete_plugins_from_db(self):
        Plugin.objects.all().delete()
        PluginPointModel.objects.all().delete()

    def prepate_query_sets(self):
        self.points = PluginPointModel.objects.filter(
            import_string="django_plugins.tests.MyPluginPoint"
        )
        self.plugins = Plugin.objects.filter(
            import_string="django_plugins.tests.MyPlugin"
        )


class PluginSyncTestCase(PluginSyncTestCaseBase):
    def setUp(self):
        self.delete_plugins_from_db()
        self.prepate_query_sets()

    def test_plugins_not_synced(self):
        """
        At first there should not be any plugins in database
        """
        self.assertEqual(self.points.count(), 0)
        self.assertEqual(self.plugins.count(), 0)

    def test_plugins_are_synced(self):
        """
        Now sync plugins and check if they appear in database
        """
        SyncPlugins("plugins", False, 0).all()
        self.assertEqual(self.points.filter(status=ENABLED).count(), 1)
        self.assertEqual(self.plugins.filter(status=ENABLED).count(), 1)

    def test_plugins_meta(self):
        SyncPlugins("plugins", False, 0).all()
        plugin_model = MyPluginPoint.get_model("my-plugin-full")
        self.assertEqual(
            "django_plugins.tests.MyPluginFull", plugin_model.import_string
        )


class PluginSyncRemovedTestCase(PluginSyncTestCaseBase):
    def setUp(self):
        self.prepate_query_sets()
        self.copy_of_points = PluginMount.points

    def tearDown(self):
        PluginMount.points = self.copy_of_points

    def test_removed_plugins(self):
        """
        Remove all plugin points and sync again, without deleting.
        All plugin points (but not plugins) should be marked as REMOVED
        """
        PluginMount.points = []
        SyncPlugins("plugins", False, 0).all()
        self.assertEqual(self.points.filter(status=REMOVED).count(), 1)
        self.assertEqual(self.plugins.filter(status=REMOVED).count(), 0)

    def test_sync_and_delete(self):
        """
        Sync plugins again, with deleting all removed from database.
        Using cascaded deletes, all plugins, that belongs to being deleted
        plugin points will be deleted also.
        """
        PluginMount.points = []
        SyncPlugins("plugins", True, 0).all()
        self.assertEqual(self.points.count(), 0)
        self.assertEqual(self.plugins.count(), 0)


class PluginModelsTest(TestCase):
    def test_plugins_of_point(self):
        qs = MyPluginPoint.get_plugins_qs()
        self.assertEqual(3, qs.count())

    def test_plugin_model(self):
        plugin_name = "django_plugins.tests.MyPlugin"
        plugin = Plugin.objects.get(import_string=plugin_name)
        self.assertEqual(plugin_name, str(plugin))
        self.assertEqual((plugin_name,), plugin.natural_key())

    def test_plugin_model_full(self):
        plugin_name = "django_plugins.tests.MyPluginFull"
        plugin = Plugin.objects.get(import_string=plugin_name)
        self.assertEqual(_("My Plugin Full"), str(plugin))

    def test_plugin_point_model(self):
        point_name = "django_plugins.tests.MyPluginPoint"
        point = PluginPointModel.objects.get(import_string=point_name)
        self.assertEqual("MyPluginPoint", str(point))

    def test_plugins_of_plugin(self):
        self.assertRaises(Exception, MyPlugin.get_plugins_qs)


class PluginsTest(TestCase):
    def test_get_model(self):
        point = "django_plugins.tests.MyPluginPoint"
        plugin = "django_plugins.tests.MyPluginFull"

        model = MyPluginFull.get_model()
        self.assertEqual(plugin, model.import_string)

        model = MyPluginFull().get_model()
        self.assertEqual(plugin, model.import_string)

        model = MyPluginPoint.get_model("my-plugin-full")
        self.assertEqual(plugin, model.import_string)

        model = MyPluginPoint.get_model()
        self.assertEqual(point, model.import_string)

        model = MyPluginPoint().get_model()
        self.assertEqual(point, model.import_string)

        model = MyPluginFull.get_point_model()
        self.assertEqual(point, model.import_string)

        self.assertRaises(Exception, MyPluginPoint.get_point_model)

    def test_get_point(self):
        point = MyPluginFull.get_point()
        self.assertTrue(point is MyPluginPoint)

        self.assertRaises(Exception, MyPluginPoint.get_point)

    def test_get_plugin(self):
        model = MyPluginFull.get_model()
        plugin = model.get_plugin()
        self.assertTrue(isinstance(plugin, MyPluginFull))

    def test_disabled_plugins(self):
        self.assertTrue(MyPluginFull.is_active())
        self.assertEqual(3, MyPluginPoint.get_plugins_qs().count())
        self.assertEqual(3, len(list(MyPluginPoint.get_plugins())))

        model = MyPluginFull.get_model()
        model.status = DISABLED
        model.save()

        self.assertFalse(MyPluginFull.is_active())
        self.assertEqual(2, MyPluginPoint.get_plugins_qs().count())
        self.assertEqual(2, len(list(MyPluginPoint.get_plugins())))
        self.assertRaises(
            Plugin.DoesNotExist, lambda: MyPluginPoint.get_model("my-plugin-full")
        )

        plugin_model = MyPluginPoint.get_model("my-plugin-full", status=None)
        self.assertEqual("my-plugin-full", plugin_model.name)

    def test_get_meta(self):
        self.assertEqual("my-plugin-full", MyPluginFull.get_name())
        self.assertEqual(_("My Plugin Full"), MyPluginFull.get_title())

        model = MyPluginFull.get_model()
        model.name = "test"
        model.save()

        self.assertEqual("test", MyPluginFull.get_name())


class MyTestForm(forms.Form):
    plugin_choice = PluginChoiceField(MyPluginPoint)
    model_choice = PluginModelChoiceField(MyPluginPoint)

    # plugin_multi_choice = PluginMultipleChoiceField(MyPluginPoint)
    model_multi_choice = PluginModelMultipleChoiceField(MyPluginPoint)


class PluginsFieldsTest(TestCase):
    def test_validation(self):
        form = MyTestForm(
            {
                "plugin_choice": "my-plugin-2",
                "model_choice": "%d" % MyPlugin2.get_model().id,
                # 'plugin_multi_choice': ['my-plugin-2'],
                "model_multi_choice": ["%d" % MyPlugin2.get_model().id],
            }
        )
        self.assertTrue(form.is_valid())

        cld = form.cleaned_data
        self.assertTrue(isinstance(cld["plugin_choice"], MyPlugin2))
        self.assertTrue(isinstance(cld["model_choice"], Plugin))
        self.assertTrue(isinstance(cld["model_multi_choice"][0], Plugin))