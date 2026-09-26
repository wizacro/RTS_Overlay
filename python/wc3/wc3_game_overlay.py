# WC3 game overlay
import os

from PyQt5.QtWidgets import QApplication

from common.rts_overlay import RTSGameOverlay
from common.rts_overlay_images import RTSOverlayImages

from wc3.wc3_settings import WC3OverlaySettings
from wc3.wc3_build_order import check_valid_wc3_build_order
from wc3.wc3_race_icon import wc3_race_icon, get_wc3_faction_selection


class WC3Images(RTSOverlayImages):
    """WC3 images"""

    def __init__(self):
        """Constructor"""
        super().__init__()

        self.food: str = 'resource/food.webp'  # food cap
        self.gold: str = 'resource/gold.webp'  # gold
        self.lumber: str = 'resource/lumber.webp'  # lumber


class WC3GameOverlay(RTSGameOverlay):
    """Game overlay application for WC3."""

    def __init__(self, app: QApplication, directory_main: str):
        """Constructor

        Parameters
        ----------
        app               Main application instance.
        directory_main    Directory where the main file is located.
        """
        super().__init__(
            app=app,
            directory_main=directory_main,
            name_game='wc3',
            settings_name='wc3_settings.json',
            images=WC3Images,
            settings_class=WC3OverlaySettings,
            check_valid_build_order=check_valid_wc3_build_order,
            get_faction_selection=get_wc3_faction_selection,
            build_order_category_name='race',
        )

        # race filter specifications (used by the manager window)
        # player race: 'Any' not allowed; opponent race: 'Any' allowed
        race_items_all = [
            (race_name, os.path.join(self.directory_game_pictures, 'race', race_image[1]))
            for race_name, race_image in wc3_race_icon.items()
        ]
        race_items_player = [item for item in race_items_all if (item[0] != 'Any')]
        self.faction_filter_specs = [
            {'key': 'race', 'tooltip': 'select race', 'items': race_items_player},
            {'key': 'opponent_race', 'tooltip': 'select race', 'items': race_items_all},
        ]

        self.update_panel_elements()  # update the current panel elements

    def reload(self, update_settings):
        """Reload the application settings, build orders...

        Parameters
        ----------
        update_settings   True to update (reload) the settings, False to keep the current ones.
        """
        super().reload(update_settings=update_settings)

        self.update_panel_elements()  # update the current panel elements

    def update_build_order(self):
        """Update the build order panel."""
        super().update_build_order()

        # valid build order selected
        if (self.selected_build_order is not None) and ('build_order' in self.selected_build_order):

            layout = self.settings.layout
            spacing = ' ' * layout.build_order.resource_spacing  # space between the elements

            # get selected steps and corresponding IDs
            selected_steps, selected_steps_ids = self.get_build_order_selected_steps_and_ids()

            # resource line
            images = self.images
            resource_step = selected_steps[selected_steps_ids[-1]]  # ID of the step to use to display the resources
            resources_line = ''

            if ('gold' in resource_step) and (resource_step['gold'] >= 0):
                resources_line += spacing + '@' + images.gold + '@ ' + str(resource_step['gold'])
            if ('lumber' in resource_step) and (resource_step['lumber'] >= 0):
                resources_line += spacing + '@' + images.lumber + '@ ' + str(resource_step['lumber'])
            if ('food' in resource_step) and (resource_step['food'] >= 0):
                resources_line += spacing + '@' + images.food + '@ ' + str(resource_step['food'])
            if layout.show_time_resource and ('time' in resource_step) and (resource_step['time'] != ''):
                resources_line += spacing + '@' + images.time + '@ ' + str(resource_step['time'])

            self.show_resources = resources_line != ''
            if self.show_resources:
                resources_line = resources_line[layout.build_order.resource_spacing :]  # remove initial spacing
                self.build_order_resources.add_row_from_picture_line(parent=self, line=str(resources_line))

            # update the notes of the build order
            self.update_build_order_notes(selected_steps, selected_steps_ids)

        self.build_order_panel_layout()  # update layout
