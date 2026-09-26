# AoM game overlay
import os

from PyQt5.QtWidgets import QApplication

from common.rts_overlay import RTSGameOverlay, scale_list_int
from common.rts_overlay_images import RTSOverlayImages

from aom.aom_settings import AoMOverlaySettings
from aom.aom_build_order import check_valid_aom_build_order
from aom.aom_major_god_icon import aom_major_god_icon, get_aom_faction_selection


class AoMImages(RTSOverlayImages):
    """AoM images"""

    def __init__(self):
        """Constructor"""
        super().__init__()

        self.food: str = 'resource/food.webp'  # food resource
        self.wood: str = 'resource/wood.webp'  # wood resource
        self.gold: str = 'resource/gold.webp'  # gold resource
        self.favor: str = 'resource/favor.webp'  # favor resource
        self.builder: str = 'resource/repair.webp'  # builder icon
        self.worker: str = 'resource/worker.webp'  # worker icon
        self.age_1: str = 'age/archaic_age.webp'  # first age image (Archaic Age)
        self.age_2: str = 'age/classical_age.webp'  # second age image (Classical Age)
        self.age_3: str = 'age/heroic_age.webp'  # third age image (Heroic Age)
        self.age_4: str = 'age/mythic_age.webp'  # fourth age image (Mythic Age)
        self.age_5: str = 'age/wonder_age.webp'  # fifth age image (Wonder Age)


class AoMGameOverlay(RTSGameOverlay):
    """Game overlay application for AoM."""

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
            name_game='aom',
            settings_name='aom_settings.json',
            images=AoMImages,
            settings_class=AoMOverlaySettings,
            check_valid_build_order=check_valid_aom_build_order,
            get_faction_selection=get_aom_faction_selection,
            build_order_category_name='major_god',
            build_order_timer_step_starting_flag=False,
        )

        # major god filter specification (used by the manager window)
        self.faction_filter_specs = [
            {
                'key': 'major_god',
                'tooltip': 'select major god',
                'items': [
                    (major_god_name, os.path.join(self.directory_game_pictures, 'major_god', letters_icon[1]))
                    for major_god_name, letters_icon in aom_major_god_icon.items()
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

        self.settings.layout.configuration.major_god_select_size = scale_list_int(
            scaling, self.unscaled_settings.layout.configuration.major_god_select_size
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
        elif age_id == 5:
            return self.images.age_5
        else:
            raise Exception('Unknown age: ' + str(age_id))

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
            target_favor = target_resources['favor']
            target_builder = target_resources['builder'] if ('builder' in target_resources) else -1
            target_worker = resource_step['worker_count']

            # line to display the target resources
            display_age = 1 <= resource_step['age'] <= 5
            display_time = layout.show_time_resource and ('time' in resource_step) and (resource_step['time'] != '')
            if (
                (target_food >= 0)
                or (target_wood >= 0)
                or (target_gold >= 0)
                or (target_favor >= 0)
                or (target_builder >= 0)
                or (target_worker >= 0)
                or display_age
                or display_time
            ):
                resources_line = images.food + '@ ' + (str(target_food) if (target_food >= 0) else ' ')
                resources_line += spacing + '@' + images.wood + '@ ' + (str(target_wood) if (target_wood >= 0) else ' ')
                resources_line += spacing + '@' + images.gold + '@ ' + (str(target_gold) if (target_gold >= 0) else ' ')
                resources_line += (
                    spacing + '@' + images.favor + '@ ' + (str(target_favor) if (target_favor >= 0) else ' ')
                )
                if target_builder >= 0:  # add builders count if indicated
                    resources_line += spacing + '@' + images.builder + '@ ' + str(target_builder)
                if target_worker >= 0:
                    resources_line += spacing + '@' + images.worker + '@ ' + str(target_worker)
                if display_age:
                    resources_line += spacing + '@' + self.get_age_image(resource_step['age'])
                # add time if indicated
                if display_time:
                    resources_line += '@' + spacing + '@' + self.images.time + '@' + resource_step['time']

                self.build_order_resources.add_row_from_picture_line(parent=self, line=str(resources_line))

            # update the notes of the build order
            self.update_build_order_notes(selected_steps, selected_steps_ids)

        self.build_order_panel_layout()  # update layout
