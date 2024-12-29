"""rexel part import plugin for InvenTree."""

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin, UserInterfaceMixin
from .version import REXEL_PLUGIN_VERSION


class RexelPlugin(SettingsMixin, UrlsMixin, UserInterfaceMixin, InvenTreePlugin):
    """rexel part import plugin for InvenTree."""
    AUTHOR = "Philip van der honing"
    DESCRIPTION = "rexel parts import plugin"
    VERSION = REXEL_PLUGIN_VERSION
    MIN_VERSION = '0.17.0'
    NAME = "inventree_rexel"
    SLUG = "inventree_rexel"
    PUBLISH_DATE = "2024-12-28"
    TITLE = "inventree_rexel part import"

    SETTINGS = {
        'USERNAME': {
            'name': ('username'),
            'description': ('username van je rexel account'),
            'default': '',
        },
        'PASSWORD': {
            'name': ('password'),
            'description': ('password van je rexel account'),
            'default': '',
        }
    }

    def is_panel_visible(self, target: str, pk: int) -> bool:
        """Determines whether the order history panel should be visible."""

        # Display for the 'parts index' page
        if target == 'partcategory':
            return True

        # No other targets are supported
        return False

    def get_ui_panels(self, request, context=None, **kwargs):

        return [
            {
                'key': 'rexel',
                'title': 'import from rexel',
                'description': 'search parts from rexel',
                'icon': 'ti:cloud-download:outline',
                'source': self.plugin_static_file(
                    'RexelPanel.js:renderPanel'
                )
            }
        ]
