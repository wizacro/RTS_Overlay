# SC2 game overlay
import os

from PyQt5.QtWidgets import QApplication

from common.rts_overlay import RTSGameOverlay, scale_list_int
from common.rts_overlay_images import RTSOverlayImages

from sc2.sc2_settings import SC2OverlaySettings
from sc2.sc2_build_order import check_valid_sc2_build_order
from sc2.sc2_race_icon import sc2_race_icon, get_sc2_faction_selection


class SC2Images(RTSOverlayImages):
    """SC2 images"""

    def __init__(self):
        """Constructor"""
        super().__init__()

        self.supply: str = 'icon/house.webp'  # supply
        self.minerals: str = 'resource/minerals.webp'  # minerals
        self.vespene_gas: str = 'resource/vespene_gas.webp'  # vespene gas


class SC2GameOverlay(RTSGameOverlay):
    """Game overlay application for SC2."""

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
            name_game='sc2',
            settings_name='sc2_settings.json',
            images=SC2Images,
            settings_class=SC2OverlaySettings,
            check_valid_build_order=check_valid_sc2_build_order,
            get_faction_selection=get_sc2_faction_selection,
            build_order_category_name='race',
        )

        # race filter specifications (used by the manager window)
        # player race: 'Any' not allowed; opponent race: 'Any' allowed
        race_items_all = [
            (race_name, os.path.join(self.directory_game_pictures, 'race_icon', race_image[1]))
            for race_name, race_image in sc2_race_icon.items()
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

    def settings_scaling(self):
        """Apply the scaling on the settings."""
        super().settings_scaling()
        scaling = self.unscaled_settings.layout.scaling / 100.0

        self.settings.layout.configuration.icon_select_size = scale_list_int(
            scaling, self.unscaled_settings.layout.configuration.icon_select_size
        )

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

            if ('minerals' in resource_step) and (resource_step['minerals'] >= 0):
                resources_line += spacing + '@' + images.minerals + '@ ' + str(resource_step['minerals'])
            if ('vespene_gas' in resource_step) and (resource_step['vespene_gas'] >= 0):
                resources_line += spacing + '@' + images.vespene_gas + '@ ' + str(resource_step['vespene_gas'])
            if ('supply' in resource_step) and (resource_step['supply'] >= 0):
                resources_line += spacing + '@' + images.supply + '@ ' + str(resource_step['supply'])
            if layout.show_time_resource and ('time' in resource_step) and (resource_step['time'] != ''):
                resources_line += spacing + '@' + images.time + '@ ' + str(resource_step['time'])

            self.show_resources = resources_line != ''
            if self.show_resources:
                resources_line = resources_line[layout.build_order.resource_spacing :]  # remove initial spacing
                self.build_order_resources.add_row_from_picture_line(parent=self, line=str(resources_line))

            # update the notes of the build order
            self.update_build_order_notes(selected_steps, selected_steps_ids)

        self.build_order_panel_layout()  # update layout
