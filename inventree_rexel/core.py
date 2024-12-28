"""Order history plugin for InvenTree."""

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin, UserInterfaceMixin
from .version import REXEL_PLUGIN_VERSION


class RexelPlugin(SettingsMixin, UrlsMixin, UserInterfaceMixin, InvenTreePlugin):
    """rexel part import plugin for InvenTree."""
    AUTHOR = "Philip van der honing"
    DESCRIPTION = "rexel parts import plugin"
    VERSION = REXEL_PLUGIN_VERSION
    MIN_VERSION = '0.17.0'
    NAME = "rexel"
    SLUG = "rexel"
    PUBLISH_DATE = "2024-12-28"
    TITLE = "Rexel part import"

    SETTINGS = {
        'USERNAME': {
            'name': ('username'),
            'description': ('username van je rexel account'),
            'default': '',
        },
        'PASSWORD': {
            'name': ('IP Address'),
            'description': ('password van je rexel account'),
            'default': '',
        },
        'BUILD_ORDER_HISTORY': {
            'name': 'Build Order History',
            'description': 'Enable build order history tracking',
            'default': True,
            'validator': bool,
        },
        'PURCHASE_ORDER_HISTORY': {
            'name': 'Purchase Order History',
            'description': 'Enable purchase order history tracking',
            'default': True,
            'validator': bool,
        },
        'SALES_ORDER_HISTORY': {
            'name': 'Sales Order History',
            'description': 'Enable sales order history tracking',
            'default': True,
            'validator': bool,
        },
        'RETURN_ORDER_HISTORY': {
            'name': 'Return Order History',
            'description': 'Enable return order history tracking',
            'default': True,
            'validator': bool,
        },
        'USER_GROUP': {
            'name': 'Allowed Group',
            'description': 'The user group that is allowed to view order history',
            'model': 'auth.group',
        }
    }

    def setup_urls(self):
        """Returns the URLs defined by this plugin."""

        from django.urls import path
        from .views import RexelView

        return [
            path('rexel/', RexelView.as_view(), name='import-rexel-part'),
        ]

    def is_panel_visible(self, target: str, pk: int) -> bool:
        """Determines whether the order history panel should be visible."""

        # Display for the 'build index' page
        if target == 'partcategory':
            return self.plugin_settings.get('BUILD_ORDER_HISTORY')

        # No other targets are supported
        return False

    def get_ui_panels(self, request, context=None, **kwargs):
        """Return a list of UI panels to be rendered in the InvenTree user interface."""

        user = request.user

        if not user or not user.is_authenticated:
            return []

        # Cache the settings for this plugin
        self.plugin_settings = self.get_settings_dict()

        # Check that the user is part of the allowed group
        if group := self.plugin_settings.get('USER_GROUP'):
            if not user.groups.filter(pk=group).exists():
                return []

        target = context.get('target_model')
        pk = context.get('target_id')

        # Panel should not be visible for this target!
        if not self.is_panel_visible(target, pk):
            return []

        return [
            {
                'key': 'rexel',
                'title': 'import from rexel',
                'description': 'search parts from rexel',
                'icon': 'ti:cloud-download:outline',
                'source': self.plugin_static_file(
                    'RexelPanel.js:renderPanel'
                ),
                'context': {
                    'settings': self.plugin_settings,
                }
            }
        ]
