# AoE4 game overlay
import os

from PyQt5.QtWidgets import QApplication

from common.rts_overlay import RTSGameOverlay, scale_list_int
from common.rts_overlay_images import RTSOverlayImages

from aoe4.aoe4_settings import AoE4OverlaySettings
from aoe4.aoe4_build_order import check_valid_aoe4_build_order
from aoe4.aoe4_civ_icon import aoe4_civilization_icon, get_aoe4_faction_selection


class AoE4Images(RTSOverlayImages):
    """AoE4 images"""

    def __init__(self):
        """Constructor"""
        super().__init__()

        self.wood: str = 'resource/resource_wood.webp'  # wood resource
        self.food: str = 'resource/resource_food.webp'  # food resource
        self.gold: str = 'resource/resource_gold.webp'  # gold resource
        self.stone: str = 'resource/resource_stone.webp'  # stone resource
        self.builder: str = 'resource/repair.webp'  # builder icon
        self.population: str = 'building_economy/house.webp'  # population icon
        self.villager: str = 'unit_worker/villager.webp'  # villager icon
        self.age_unknown: str = 'age/age_unknown.webp'  # unknown age image
        self.age_1: str = 'age/age_1.webp'  # first age image (Dark Age)
        self.age_2: str = 'age/age_2.webp'  # second age image (Feudal Age)
        self.age_3: str = 'age/age_3.webp'  # third age image (Castle Age)
        self.age_4: str = 'age/age_4.webp'  # fourth age image (Imperial Age)


class AoE4GameOverlay(RTSGameOverlay):
    """Game overlay application for AoE4."""

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
            name_game='aoe4',
            settings_name='aoe4_settings.json',
            images=AoE4Images,
            settings_class=AoE4OverlaySettings,
            check_valid_build_order=check_valid_aoe4_build_order,
            get_faction_selection=get_aoe4_faction_selection,
            build_order_category_name='civilization',
            build_order_timer_step_starting_flag=False,
        )

        # civilization filter specification (used by the manager window)
        self.faction_filter_specs = [
            {
                'key': 'civilization',
                'tooltip': 'select civilization',
                'items': [
                    (civ_name, os.path.join(self.directory_game_pictures, 'civilization_flag', letters_icon[1]))
                    for civ_name, letters_icon in aoe4_civilization_icon.items()
                ],
            }
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

        self.settings.layout.configuration.flag_select_size = scale_list_int(
            scaling, self.unscaled_settings.layout.configuration.flag_select_size
        )

    def get_age_image(self, age_id: int) -> str:
        """Get the image for a requested age.

        Parameters
        ----------
        age_id    ID of the age.

        Returns
        -------
        age image with path
        """
        if age_id == 1:
            return self.images.age_1
        elif age_id == 2:
            return self.images.age_2
        elif age_id == 3:
            return self.images.age_3
        elif age_id == 4:
            return self.images.age_4
        else:
            return self.images.age_unknown

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

            # target resources
            target_resources = resource_step['resources']
            target_food = target_resources['food']
            target_wood = target_resources['wood']
            target_gold = target_resources['gold']
            target_stone = target_resources['stone']
            target_builder = target_resources['builder'] if ('builder' in target_resources) else -1
            target_villager = resource_step['villager_count']
            target_population = resource_step['population_count']

            # line to display the target resources
            resources_line = images.food + '@ ' + (str(target_food) if (target_food >= 0) else ' ')
            resources_line += spacing + '@' + images.wood + '@ ' + (str(target_wood) if (target_wood >= 0) else ' ')
            resources_line += spacing + '@' + images.gold + '@ ' + (str(target_gold) if (target_gold >= 0) else ' ')
            resources_line += spacing + '@' + images.stone + '@ ' + (str(target_stone) if (target_stone >= 0) else ' ')
            if target_builder > 0:  # add builders count if indicated
                resources_line += spacing + '@' + images.builder + '@ ' + str(target_builder)
            if target_villager >= 0:
                resources_line += spacing + '@' + images.villager + '@ ' + str(target_villager)
            if target_population >= 0:
                resources_line += spacing + '@' + images.population + '@ ' + str(target_population)
            if 1 <= resource_step['age'] <= 4:
                resources_line += spacing + '@' + self.get_age_image(resource_step['age'])
            # add time if indicated
            if layout.show_time_resource and ('time' in resource_step) and (resource_step['time'] != ''):
                resources_line += '@' + spacing + '@' + self.images.time + '@' + resource_step['time']

            self.build_order_resources.add_row_from_picture_line(parent=self, line=str(resources_line))

            # update the notes of the build order
            self.update_build_order_notes(selected_steps, selected_steps_ids)

        self.build_order_panel_layout()  # update layout
