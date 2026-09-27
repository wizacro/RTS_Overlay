import os
import json
import re
import shutil
import time
import appdirs
from math import floor
from enum import Enum
from copy import deepcopy
from thefuzz import process
from typing import Dict, Union

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QShortcut, QWidget
from PyQt5.QtGui import QKeySequence, QFont, QIcon, QCursor
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer

from common.chinese_locale import t  # Chinese UI layer (translation of dynamic message parts)

from common.build_order_tools import (
    get_build_orders,
    check_build_order_key_values,
    get_build_order_timer_steps,
    get_build_order_timer_step_ids,
    get_build_order_timer_steps_display,
)
from common.label_display import MultiQLabelDisplay
from common.useful_tools import (
    TwinHoverButton,
    scale_int,
    scale_list_int,
    set_background_opacity,
    widget_x_end,
    popup_message,
)
from common.keyboard_mouse import KeyboardMouseManagement
from common.rts_settings import KeyboardMouse


# icon folders used by the highlights fallback classification (AoE2 layout; daughter
# classes replace these through 'icon_unit_folders' etc. if their layout differs)
ICON_UNIT_FOLDERS = {'stable', 'archery_range', 'barracks', 'siege_workshop', 'monastery', 'castle', 'dock', 'unique_unit'}
ICON_TECH_FOLDERS = {'blacksmith', 'mill', 'lumber_camp', 'mining_camp', 'town_center', 'university'}
ICON_EXCLUDED_FOLDERS = {'resource', 'animal', 'age', 'other', 'civilization', 'defensive_structures', 'hero'}


# ID of the overlay state (the manager window switches between the two)
class PanelID(Enum):
    CONFIG = 0  # Arrange state (pre-game): whole window draggable
    BUILD_ORDER = 1  # In-game state: no dragging, buttons clickable, rest click-through


class RTSGameOverlay(QMainWindow):
    """RTS game overlay application (display only, managed by the manager window)."""

    def __init__(
        self,
        app: QApplication,
        directory_main: str,
        name_game: str,
        settings_name: str,
        images,
        settings_class,
        check_valid_build_order,
        get_faction_selection,
        build_order_category_name: str = None,
        build_order_timer_available: bool = True,
        build_order_timer_step_starting_flag: bool = True,
    ):
        """Constructor

        Parameters
        ----------
        app                                     Main application instance.
        directory_main                          Directory where the main file is located.
        name_game                               Name of the game (for pictures folder).
        settings_name                           Name of the settings (to load/save).
        images                                  Main images for the overlay window.
        settings_class                          Settings class.
        check_valid_build_order                 Function to check if a build order is valid.
        get_faction_selection                   Function to get the faction selection dictionary.
        build_order_category_name               If not None, accept build orders with same name,
                                                provided they are in different categories.
        build_order_timer_available             True if the build order timer feature is available.
        build_order_timer_step_starting_flag    True if the timer steps starts at the requested time,
                                                False if ending at this time.
        """
        super().__init__()

        # application instance
        self.app = app

        # initialization not yet done
        self.init_done = False

        self.selected_panel = PanelID.CONFIG  # overlay state (arrange by default, manager opens it)

        self.show_resources = True  # True to show the resources in the build order current display

        # images
        self.images = images()

        # directories
        self.name_game = name_game
        self.directory_main = directory_main  # main file
        # assets folder: next to the launcher (packaged) or one level above (source run)
        docs_candidates = [
            os.path.join(self.directory_main, 'docs'),  # packaged layout
            os.path.join(self.directory_main, '..', 'docs'),  # source layout
        ]
        docs_dir = next((c for c in docs_candidates if os.path.isdir(c)), docs_candidates[0])
        self.directory_game_pictures = os.path.join(docs_dir, 'assets', name_game)  # game pictures
        self.directory_common_pictures = os.path.join(docs_dir, 'assets', 'common')  # common pictures
        # common configuration: portable mode - kept inside the tool directory (no C: system folders)
        self.directory_config_rts_overlay = os.path.join(self.directory_main, 'local_config')
        if not os.path.isdir(self.directory_config_rts_overlay):
            legacy_root = os.path.join(appdirs.user_data_dir(), 'RTS_Overlay')
            if os.path.isdir(legacy_root):  # one-time migration: copy the old AppData configuration (original kept)
                try:
                    shutil.copytree(legacy_root, self.directory_config_rts_overlay)
                    print(f'Migrated the configuration from {legacy_root} to {self.directory_config_rts_overlay}.')
                except Exception as e:
                    print(f'Could not migrate the old configuration ({e}); using it in place instead.')
                    self.directory_config_rts_overlay = legacy_root
        self.directory_config_game = os.path.join(self.directory_config_rts_overlay, name_game)  # game configuration
        self.directory_settings = os.path.join(self.directory_config_game, 'settings')  # settings file
        self.directory_build_orders = os.path.join(self.directory_config_game, 'build_orders')  # build orders

        # settings
        self.unscaled_settings = settings_class()
        self.default_settings = deepcopy(self.unscaled_settings)
        self.settings_file = os.path.join(self.directory_settings, settings_name)

        # check if settings can be loaded from existing file
        if os.path.exists(self.settings_file):  # settings file found
            try:
                with open(self.settings_file, 'rb') as f:
                    dict_data = json.load(f)
                    self.unscaled_settings.from_dict(dict_data)
                print(f'Loading parameters from {self.settings_file}.')
            except KeyError as e:
                print(f'Obtained KeyError {e} while reading the parameters from {self.settings_file}.')
                print('Loading default parameters.')
                del self.unscaled_settings
                self.unscaled_settings = settings_class()
            self.screen_position_safety()

        else:  # no settings file found
            print('Loading default parameters.')

            self.screen_position_safety()

            # save the settings
            self.save_settings()

        # scaling the settings
        self.settings = deepcopy(self.unscaled_settings)
        self.settings_scaling()

        # title and icon
        images = self.images
        self.setWindowTitle(self.settings.title)
        self.game_icon = os.path.join(self.directory_common_pictures, images.game_icon)
        self.setWindowIcon(QIcon(self.game_icon))

        # display panel: the overlay starts closed, the manager window opens it
        self.hidden = True

        # mouse position
        self.mouse_x = 0
        self.mouse_y = 0

        self.stop_application = False  # True if application must be stopped

        # build order selection
        print('Loading the build orders.')
        self.valid_build_orders = []  # valid build orders names
        self.build_order_selection_id = 0  # ID selection of the build order in list
        self.selected_build_order = None  # selected build order
        self.selected_build_order_name = None  # selected build order name
        self.selected_build_order_step_count = 0  # selected build order count of steps
        self.selected_build_order_step_id = -1  # selected build order step ID
        self.check_valid_build_order = check_valid_build_order
        self.get_faction_selection = get_faction_selection
        self.build_order_category_name = build_order_category_name
        self.build_orders = get_build_orders(
            self.directory_build_orders, check_valid_build_order, category_name=self.build_order_category_name
        )
        self.valid_key_build_orders_count = len(self.build_orders) # will be updated to the correct key count later
        self.last_filter_condition = None  # last key condition used by the manager search

        # faction filter specifications for the manager window (daughter classes may set this)
        self.faction_filter_specs = []

        # icon classification for the highlights window (daughter classes may set this)
        self.icon_classification = {}
        self.icon_unit_folders = set(ICON_UNIT_FOLDERS)
        self.icon_tech_folders = set(ICON_TECH_FOLDERS)
        self.icon_excluded_folders = set(ICON_EXCLUDED_FOLDERS)

        # manager callback to notify overlay state changes
        self.mode_callback = None

        # move window
        self.setMouseTracking(True)  # mouse tracking
        self.left_click_start = False  # left click pressing started
        self.old_pos = self.pos()  # old position of the window
        self.init_x = self.frameGeometry().x()  # initial mouse X position
        self.init_y = self.frameGeometry().y()  # initial mouse Y position
        self.adapt_notes_to_columns = -1  # columns size adaptation for the notes

        # build order display elements
        layout = self.settings.layout
        self.build_order_step_time = QLabel('Step: 0/0', self)
        self.build_order_step_time_styling()

        self.build_order_resources = MultiQLabelDisplay(
            font_police=layout.font_police,
            font_size=layout.font_size,
            image_height=layout.build_order.image_height,
            border_size=layout.border_size,
            vertical_spacing=layout.vertical_spacing,
            color_default=layout.color_default,
            game_pictures_folder=self.directory_game_pictures,
            common_pictures_folder=self.directory_common_pictures,
        )

        color_row_emphasis = layout.build_order.color_row_emphasis if self.settings.timer_available else [0, 0, 0]
        extra_emphasis_height = layout.build_order.extra_emphasis_height if self.settings.timer_available else 0
        self.build_order_notes = MultiQLabelDisplay(
            font_police=layout.font_police,
            font_size=layout.font_size,
            image_height=layout.build_order.image_height,
            extra_emphasis_height=extra_emphasis_height,
            border_size=layout.border_size,
            vertical_spacing=layout.vertical_spacing,
            color_default=layout.color_default,
            color_row_emphasis=color_row_emphasis,
            game_pictures_folder=self.directory_game_pictures,
            common_pictures_folder=self.directory_common_pictures,
        )

        # build order timer elements
        self.build_order_timer: Dict[
            str, Union[bool, bool, bool, float, float, int, int, float, str, list, list, list, list]
        ] = {
            # True if the build order timer feature is available
            'available': build_order_timer_available and self.settings.timer_available,
            # True if the timer steps starts at the indicated time, False if ending at this time
            'step_starting_flag': build_order_timer_step_starting_flag,
            'use_timer': False,  # True to update BO with timer, False for manual selection
            'run_timer': False,  # True if the BO timer is running (False to stop)
            'absolute_time_init': time.time(),  # last absolute time when the BO timer run started [sec]
            'time_sec': 0.0,  # time for the BO [sec]
            'time_int': 0,  # 'time_sec' with a cast to integer
            'last_time_int': 0,  # last value for 'time_int' [sec]
            'time_sec_init': 0.0,  # value of 'time_sec' when run started [sec]
            'last_time_label': '',  # last string value for the time label
            'steps': [],  # steps adapted for the timer feature
            'steps_ids': [],  # IDs to select the current steps from 'steps'
            'last_steps_ids': [],  # last value for 'steps_ids'
        }

        # window color and position
        self.upper_left_position = [0, 0]
        self.upper_right_position = [0, 0]
        self.window_color_position_initialization()

        # overlay buttons (start/stop timer, previous step, next step)
        action_button_qsize = QSize(self.settings.layout.action_button_size, self.settings.layout.action_button_size)

        bo_previous_tooltip = (
            'previous build order step / -1 sec' if build_order_timer_available else 'previous build order step'
        )
        self.build_order_previous_button = TwinHoverButton(
            parent=self,
            click_connect=self.build_order_previous_step,
            icon=QIcon(os.path.join(self.directory_common_pictures, images.build_order_previous_step)),
            button_qsize=action_button_qsize,
            tooltip=bo_previous_tooltip,
        )

        bo_next_tooltip = 'next build order step / +1 sec' if build_order_timer_available else 'next build order step'
        self.build_order_next_button = TwinHoverButton(
            parent=self,
            click_connect=self.build_order_next_step,
            icon=QIcon(os.path.join(self.directory_common_pictures, images.build_order_next_step)),
            button_qsize=action_button_qsize,
            tooltip=bo_next_tooltip,
        )

        if self.settings.timer_available:
            self.build_order_start_stop_timer = TwinHoverButton(
                parent=self,
                click_connect=self.overlay_start_timer_button,
                icon=QIcon(os.path.join(self.directory_common_pictures, images.start_stop_timer)),
                button_qsize=action_button_qsize,
                tooltip='start/stop the BO timer',
            )
        else:
            self.build_order_start_stop_timer = None

        # hide button (two clicks required, to avoid hiding the overlay by mistake)
        self.hide_button_armed = False
        self.build_order_hide_button = TwinHoverButton(
            parent=self,
            click_connect=self.hide_button_clicked,
            icon=QIcon(os.path.join(self.directory_common_pictures, images.hide_panel)),
            button_qsize=action_button_qsize,
            tooltip='Click twice to hide',
        )

        # lock button: shows the current overlay state (locked = fixed, unlocked = move), click to toggle
        self.build_order_lock_button = TwinHoverButton(
            parent=self,
            click_connect=self.next_panel,
            icon=QIcon(os.path.join(self.directory_common_pictures, images.lock_open)),
            button_qsize=action_button_qsize,
            tooltip='Click to switch between move and fixed modes',
        )
        self.update_lock_button_icon()

        # select the next build order (global shortcut, works with the manager search results)
        hotkeys = self.settings.hotkeys
        self.hotkey_next_build_order = QShortcut(QKeySequence(hotkeys.select_next_build_order), self)
        self.hotkey_next_build_order.activated.connect(self.select_next_build_order)

        # keyboard and mouse global hotkeys
        self.hotkey_names = ['next_panel', 'show_hide', 'build_order_previous_step', 'build_order_next_step']
        if self.build_order_timer['available']:
            self.hotkey_names.extend(
                ['switch_timer_manual', 'start_timer', 'stop_timer', 'start_stop_timer', 'reset_timer']
            )

        self.keyboard_mouse = KeyboardMouseManagement(print_unset=False)

        self.mouse_buttons_dict = dict()  # dictionary as {keyboard_name: mouse_button_name}
        self.set_keyboard_mouse()

        # configure hotkeys window (opened from the manager, parented to the overlay)
        self.panel_config_hotkeys = None

        # create build orders folder
        os.makedirs(self.directory_build_orders, exist_ok=True)

        # initialization done
        self.init_done = True

    def reload(self, update_settings):
        """Reload the application settings, build orders...

        Parameters
        ----------
        update_settings   True to update (reload) the settings, False to keep the current ones.
        """

        # re-initialization not yet done
        self.init_done = False

        # settings
        if update_settings:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'rb') as f:
                    dict_data = json.load(f)
                    self.unscaled_settings.from_dict(dict_data)
                print(f'Reloading parameters from {self.settings_file}.')
            else:
                self.unscaled_settings = deepcopy(self.default_settings)
                print('No user settings file saved, resetting to default values.')
        else:
            print('Reload without updating the settings.')

        # scaling the settings
        self.settings = deepcopy(self.unscaled_settings)
        self.settings_scaling()

        # title and icon
        images = self.images
        self.setWindowTitle(self.settings.title)
        self.game_icon = os.path.join(self.directory_common_pictures, images.game_icon)
        self.setWindowIcon(QIcon(self.game_icon))

        # reset build order selection
        print('Reloading the build orders.')
        self.valid_build_orders = []
        self.build_order_selection_id = 0
        self.selected_build_order = None
        self.selected_build_order_name = None
        self.selected_build_order_step_count = 0
        self.selected_build_order_step_id = -1
        self.build_orders = get_build_orders(
            self.directory_build_orders, self.check_valid_build_order, category_name=self.build_order_category_name
        )
        self.valid_key_build_orders_count = len(self.build_orders)

        # move window
        self.left_click_start = False  # left click pressing started
        self.old_pos = self.pos()  # old position of the window
        self.init_x = self.frameGeometry().x()  # initial mouse X position
        self.init_y = self.frameGeometry().y()  # initial mouse Y position

        # build order display elements
        layout = self.settings.layout
        self.build_order_step_time_styling()

        # display build order
        self.build_order_resources.update_settings(
            font_police=layout.font_police,
            font_size=layout.font_size,
            image_height=layout.build_order.image_height,
            border_size=layout.border_size,
            vertical_spacing=layout.vertical_spacing,
            color_default=layout.color_default,
        )

        color_row_emphasis = layout.build_order.color_row_emphasis if self.settings.timer_available else [0, 0, 0]
        extra_emphasis_height = layout.build_order.extra_emphasis_height if self.settings.timer_available else 0
        self.build_order_notes.update_settings(
            font_police=layout.font_police,
            font_size=layout.font_size,
            image_height=layout.build_order.image_height,
            extra_emphasis_height=extra_emphasis_height,
            border_size=layout.border_size,
            vertical_spacing=layout.vertical_spacing,
            color_default=layout.color_default,
            color_row_emphasis=color_row_emphasis,
        )

        self.deactivate_timer(self.build_order_timer['use_timer'])  # build order timer elements

        # window color and position
        self.window_color_position_initialization()

        # overlay buttons
        action_button_qsize = QSize(self.settings.layout.action_button_size, self.settings.layout.action_button_size)

        self.build_order_previous_button.update_icon_size(
            QIcon(os.path.join(self.directory_common_pictures, images.build_order_previous_step)), action_button_qsize
        )

        self.build_order_next_button.update_icon_size(
            QIcon(os.path.join(self.directory_common_pictures, images.build_order_next_step)), action_button_qsize
        )

        if self.build_order_start_stop_timer is not None:
            self.update_build_order_start_stop_timer_icon()

        self.update_lock_button_icon()  # lock icon follows the current overlay state

        # keyboard and mouse global hotkeys
        self.set_keyboard_mouse()

        # re-initialization done
        self.init_done = True

    def update_build_order_start_stop_timer_icon(self):
        """Update the icon for 'build_order_start_stop_timer'."""
        images = self.images
        action_button_qsize = QSize(self.settings.layout.action_button_size, self.settings.layout.action_button_size)
        selected_image = (
            images.start_stop_timer_active if self.build_order_timer['run_timer'] else images.start_stop_timer
        )

        self.build_order_start_stop_timer.update_icon_size(
            QIcon(os.path.join(self.directory_common_pictures, selected_image)), action_button_qsize
        )

    def update_lock_button_icon(self):
        """Update the lock button icon to reflect the current overlay state
        (closed lock = fixed mode, open lock = move mode)."""
        images = self.images
        action_button_qsize = QSize(self.settings.layout.action_button_size, self.settings.layout.action_button_size)
        selected_image = images.lock_closed if (self.selected_panel == PanelID.BUILD_ORDER) else images.lock_open

        self.build_order_lock_button.update_icon_size(
            QIcon(os.path.join(self.directory_common_pictures, selected_image)), action_button_qsize
        )

    def deactivate_timer(self, build_order_timer_flag: bool = False):
        """Deactivate the timer functionalities (e.g. non valid BO for timer).

        Parameters
        ----------
        build_order_timer_flag   True to update BO with timer, False for manual selection.
        """
        self.build_order_timer['use_timer'] = build_order_timer_flag
        self.build_order_timer['run_timer'] = False
        self.build_order_timer['absolute_time_init'] = time.time()
        self.build_order_timer['time_sec'] = 0.0
        self.build_order_timer['time_int'] = 0
        self.build_order_timer['last_time_int'] = 0
        self.build_order_timer['time_sec_init'] = 0.0
        self.build_order_timer['last_time_label'] = ''
        self.build_order_timer['steps'] = []
        self.build_order_timer['steps_ids'] = []
        self.build_order_timer['last_steps_ids'] = []

    def screen_position_safety(self):
        """Check that the upper left/right corner is inside the screen."""
        screen_size = self.app.primaryScreen().size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        layout = self.unscaled_settings.layout
        upper_position = layout.upper_right_position if layout.overlay_on_right_side else layout.upper_left_position

        if upper_position[0] >= screen_width:
            print(f'Upper right corner X position set to {(screen_width - 20)} (to stay inside screen).')
            upper_position[0] = screen_width - 20

        if upper_position[1] >= screen_height:
            print(f'Upper right corner Y position set to {(screen_height - 40)} (to stay inside screen).')
            upper_position[1] = screen_height - 40

    def set_keyboard_mouse(self):
        """Set the keyboard and mouse hotkey inputs."""

        # selection keys
        hotkey_settings = self.unscaled_settings.hotkeys
        self.hotkey_next_build_order.setKey(QKeySequence(hotkey_settings.select_next_build_order))

        self.mouse_buttons_dict.clear()  # clear mouse buttons
        print('Update hotkeys')

        # loop on all the hotkeys
        for hotkey_name in self.hotkey_names:
            if hasattr(hotkey_settings, hotkey_name):
                value = getattr(hotkey_settings, hotkey_name)
                if isinstance(value, KeyboardMouse):
                    # keyboard keys
                    keyboard_value = value.keyboard
                    self.keyboard_mouse.update_keyboard_hotkey(hotkey_name, keyboard_value)

                    # mouse buttons
                    mouse_value = value.mouse
                    if mouse_value != '':
                        mouse_button_names = self.keyboard_mouse.mouse_button_names
                        if mouse_value in mouse_button_names:
                            assert hotkey_name not in self.mouse_buttons_dict
                            self.mouse_buttons_dict[hotkey_name] = mouse_value
                        else:
                            print(f'Invalid mouse value: {mouse_value} | options: {mouse_button_names}')

                    # print
                    print_keyboard = 'not-set' if (keyboard_value == '') else keyboard_value
                    print_mouse = 'not-set' if (mouse_value == '') else mouse_value
                    print(f'    {hotkey_name}: keyboard:{print_keyboard} | mouse:{print_mouse}')
                else:
                    print(f'    KeyboardMouse instance expected for hotkey \'{hotkey_name}\'.')
            else:
                print(f'    Hotkey \'{hotkey_name}\' not found.')

        # all flags to not set
        self.keyboard_mouse.set_all_flags(False)

    def build_order_step_time_styling(self):
        """Styling of the build order step label (common to constructor and reload)."""
        layout = self.settings.layout
        color_default_str = f'color: rgb({layout.color_default[0]}, {layout.color_default[1]}, {layout.color_default[2]})'
        self.build_order_step_time.setStyleSheet(color_default_str)
        self.build_order_step_time.setFont(QFont(layout.font_police, layout.font_size))
        self.build_order_step_time.adjustSize()

    def settings_scaling(self):
        """Apply the scaling on the settings (scaling value from the settings)."""
        scaling = self.unscaled_settings.layout.scaling / 100.0
        layout = self.settings.layout
        unscaled_layout = self.unscaled_settings.layout

        layout.border_size = scale_int(scaling, unscaled_layout.border_size)
        layout.vertical_spacing = scale_int(scaling, unscaled_layout.vertical_spacing)
        layout.horizontal_spacing = scale_int(scaling, unscaled_layout.horizontal_spacing)
        layout.action_button_size = scale_int(scaling, unscaled_layout.action_button_size)
        layout.action_button_spacing = scale_int(scaling, unscaled_layout.action_button_spacing)

        build_order = layout.build_order
        unscaled_build_order = unscaled_layout.build_order
        build_order.image_height = scale_int(scaling, unscaled_build_order.image_height)
        build_order.resource_spacing = scale_int(scaling, unscaled_build_order.resource_spacing)
        build_order.bo_next_tab_spacing = scale_int(scaling, unscaled_build_order.bo_next_tab_spacing)

        panel_hotkeys = self.settings.panel_hotkeys
        unscaled_panel_hotkeys = self.unscaled_settings.panel_hotkeys
        panel_hotkeys.border_size = scale_int(scaling, unscaled_panel_hotkeys.border_size)
        panel_hotkeys.edit_width = scale_int(scaling, unscaled_panel_hotkeys.edit_width)
        panel_hotkeys.edit_height = scale_int(scaling, unscaled_panel_hotkeys.edit_height)
        panel_hotkeys.button_margin = scale_int(scaling, unscaled_panel_hotkeys.button_margin)
        panel_hotkeys.vertical_spacing = scale_int(scaling, unscaled_panel_hotkeys.vertical_spacing)
        panel_hotkeys.horizontal_spacing = scale_int(scaling, unscaled_panel_hotkeys.horizontal_spacing)

    def _resolve_icon_path(self, icon_ref: str):
        """Resolve an '@folder/name.ext@' icon reference to an existing file path
        (tries the original extension, then webp/png/jpg)."""
        base = os.path.splitext(os.path.join(self.directory_game_pictures, icon_ref.replace('/', os.sep)))[0]
        for candidate in (base + os.path.splitext(icon_ref)[1], base + '.webp', base + '.png', base + '.jpg'):
            if os.path.isfile(candidate):
                return candidate
        return None

    def get_build_order_highlights(self) -> dict:
        """Extract the main units and technologies from the selected build order notes.

        Icons are classified through 'icon_classification' (daughter classes provide the
        per-game table); unknown icons fall back to their building folder. Villager,
        resource, animal, age and building icons are excluded.

        Returns
        -------
        Dictionary with 'units' and 'techs' lists of {'stem', 'name', 'icon'} in
        first-appearance order.
        """
        highlights = {"units": [], "techs": []}
        if self.selected_build_order is None or 'build_order' not in self.selected_build_order:
            return highlights

        seen = set()
        for step in self.selected_build_order['build_order']:
            for note in step.get('notes', []):
                for icon in re.findall(r'@([^@]+)@', note):
                    folder, _, fname = icon.partition('/')
                    stem = os.path.splitext(fname)[0]
                    if folder in self.icon_excluded_folders or stem in seen:
                        continue

                    info = self.icon_classification.get(stem)
                    if info is not None:
                        kind = info.get('type')
                        name = info.get('name', stem)
                        if kind not in ('unit', 'tech'):
                            continue
                    elif folder in self.icon_unit_folders:
                        kind, name = 'unit', stem  # unknown icon: English fallback
                    elif folder in self.icon_tech_folders:
                        kind, name = 'tech', stem
                    else:
                        continue

                    icon_path = self._resolve_icon_path(icon)
                    if icon_path is None:
                        continue
                    seen.add(stem)
                    highlights['units' if kind == 'unit' else 'techs'].append(
                        {'stem': stem, 'name': name, 'icon': icon_path}
                    )
        return highlights

    def get_filter_specs(self):
        """Get the faction filter specifications for the manager window.

        Returns
        -------
        List of dictionaries with keys: 'key' (build order key), 'tooltip', 'items'
        (list of tuples (name, icon path)).
        """
        return self.faction_filter_specs

    def get_build_order_names(self, key_condition: dict = None, search_string: str = ''):
        """Filter the build orders for the manager search.

        Parameters
        ----------
        key_condition   Dictionary with the keys to look for and their value, None to skip it.
        search_string   Search string from the manager search bar.

        Returns
        -------
        List of valid build order names, message to display when no match (None otherwise).
        """
        self.last_filter_condition = key_condition
        self.get_valid_build_orders(key_condition, search_string)
        if len(self.valid_build_orders) > 0:
            return list(self.valid_build_orders), None
        return [], self.get_no_build_order_text(search_string)

    def get_no_build_order_text(self, search_string: str = ''):
        """Get a message when no build order matches the search."""
        if len(self.build_orders) == 0:
            return 'No valid build order in the build order folder.'
        elif self.valid_key_build_orders_count == 0:
            return 'No valid build order for this faction.'
        elif search_string == '':
            return 'Select build order with search bar.'
        else:
            return 'No valid build order found with these keywords.'

    def next_panel(self):
        """Switch between the arrange (pre-game) and in-game overlay states."""

        # saving the upper right corner position
        if self.selected_panel == PanelID.CONFIG:
            self.save_upper_corner_positions()

        if self.selected_panel == PanelID.CONFIG:
            self.selected_panel = PanelID.BUILD_ORDER
        elif self.selected_panel == PanelID.BUILD_ORDER:
            self.selected_panel = PanelID.CONFIG

        self.update_panel_elements()  # update the elements of the state to display
        self.update_position()  # restoring the upper right corner position

        if self.mode_callback is not None:  # notify the manager window
            self.mode_callback(self.selected_panel)

    def overlay_visible(self) -> bool:
        """True if the overlay is currently open (from the manager perspective)."""
        return (not self.hidden) and self.isVisible()

    def open_overlay(self):
        """Show the overlay (requested from the manager window)."""
        self.hidden = False
        self.update_panel_elements()
        self.setWindowOpacity(self.settings.layout.opacity)
        self.update_position()

    def close_overlay(self):
        """Hide the overlay (requested from the manager window)."""
        self.hidden = True
        self.setWindowOpacity(0.0)
        self.hide()

    def update_panel_elements(self):
        """Update the elements of the overlay state to display."""
        if self.hidden:
            self.update_build_order()  # keep the display data up to date even while hidden
            return

        if self.selected_panel == PanelID.CONFIG:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        else:
            QApplication.restoreOverrideCursor()

        # in-game state: window is transparent to mouse events, except for the buttons (children)
        self.setAttribute(
            Qt.WA_TransparentForMouseEvents, self.selected_panel != PanelID.CONFIG
        )

        # lock button icon follows the current state
        self.update_lock_button_icon()

        # remove the window title and stay always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # hide the elements by default
        self.hide_elements()

        # both states display the build order content
        self.update_build_order()

        # show the main window
        self.show()

    def mouseMoveEvent(self, event):
        """Actions related to the mouse moving events (drag in the arrange state).

        Parameters
        ----------
        event    Mouse event.
        """
        if self.selected_panel == PanelID.CONFIG:  # only needed when in the arrange state
            self.move_window(event)

    def quit_application(self):
        """Quit the application."""
        self.stop_application = True
        print('Stopping the application.')

        self.hide()  # hide the application while closing it

        self.build_order_previous_button.close()
        self.build_order_next_button.close()
        if self.build_order_start_stop_timer is not None:
            self.build_order_start_stop_timer.close()
        self.build_order_hide_button.close()
        self.build_order_lock_button.close()

        if (self.panel_config_hotkeys is not None) and self.panel_config_hotkeys.isVisible():
            self.panel_config_hotkeys.close()
            self.panel_config_hotkeys = None

        self.keyboard_mouse.shutdown()  # release global hotkeys
        self.close()
        QApplication.quit()

    def get_hotkey_mouse_flag(self, name: str) -> bool:
        """Get the flag value for a global hotkey and/or mouse input.

        Parameters
        ----------
        name    Field to check.

        Returns
        -------
        True if flag activated, False if not activated or not found.
        """
        valid_keyboard = (name in self.keyboard_mouse.keyboard_hotkeys) and (
            self.keyboard_mouse.keyboard_hotkeys[name].sequence != ''
        )
        mouse_button_name = self.mouse_buttons_dict[name] if (name in self.mouse_buttons_dict) else None
        valid_mouse = (mouse_button_name is not None) and (mouse_button_name in self.keyboard_mouse.mouse_button_names)

        if valid_keyboard and valid_mouse:  # both mouse and hotkey must be pressed
            if self.keyboard_mouse.is_keyboard_hotkey_pressed(name) and self.keyboard_mouse.get_mouse_flag(
                mouse_button_name
            ):
                return (
                    self.keyboard_mouse.get_mouse_elapsed_time(mouse_button_name)
                    < self.unscaled_settings.hotkeys.mouse_max_time
                )
            else:
                return False

        elif valid_keyboard:  # check keyboard
            return self.keyboard_mouse.get_keyboard_hotkey_flag(name)

        elif valid_mouse:  # check mouse
            return self.keyboard_mouse.get_mouse_flag(mouse_button_name)

        return False  # not set

    def timer_build_order_call(self):
        """Function called on a timer for build order timer update."""
        if self.build_order_timer['run_timer']:
            elapsed_time = time.time() - self.build_order_timer['absolute_time_init']
            if hasattr(self.settings, 'timer_speed_factor'):  # in case timer value is not the same as real-time
                elapsed_time *= self.settings.timer_speed_factor
            self.build_order_timer['time_sec'] = self.build_order_timer['time_sec_init'] + elapsed_time
            self.build_order_timer['time_int'] = int(floor(self.build_order_timer['time_sec']))

            if not self.hidden:  # update build order panel display
                self.update_build_order_time_label()

                # time was updated (or no valid note ID)
                if (self.build_order_timer['last_time_int'] != self.build_order_timer['time_int']) or (
                    not self.build_order_timer['last_steps_ids']
                ):
                    self.build_order_timer['last_time_int'] = self.build_order_timer['time_int']

                    # compute current note ID
                    self.build_order_timer['steps_ids'] = get_build_order_timer_step_ids(
                        self.build_order_timer['steps'],
                        self.build_order_timer['time_int'],
                        self.build_order_timer['step_starting_flag'],
                    )

                    # note ID was updated
                    if self.build_order_timer['last_steps_ids'] != self.build_order_timer['steps_ids']:
                        self.build_order_timer['last_steps_ids'] = self.build_order_timer['steps_ids']

                        self.update_build_order()

    def timer_mouse_keyboard_call(self):
        """Function called on a timer for mouse and keyboard inputs."""
        self.update_mouse()  # update the mouse position

        # keyboard action flags
        if (self.panel_config_hotkeys is None) or (not self.panel_config_hotkeys.isVisible()):

            # switch the overlay state (arrange <-> in-game)
            if self.get_hotkey_mouse_flag('next_panel'):
                self.next_panel()

            if self.get_hotkey_mouse_flag('show_hide'):  # show/hide overlay
                self.show_hide()

            # select previous step of the build order
            if self.get_hotkey_mouse_flag('build_order_previous_step') and (not self.hidden):
                self.build_order_previous_step()

            # select next step of the build order
            if self.get_hotkey_mouse_flag('build_order_next_step') and (not self.hidden):
                self.build_order_next_step()

            if self.build_order_timer['available']:
                # switch build order between timer/manual
                if self.get_hotkey_mouse_flag('switch_timer_manual') and (not self.hidden):
                    self.switch_build_order_timer_manual()

                # check if timer update can be applied
                apply_timer_update = (
                    self.build_order_timer['use_timer']
                    and (not self.hidden)
                    and self.build_order_timer['steps']
                )

                # start the build order timer
                if self.get_hotkey_mouse_flag('start_timer'):
                    if apply_timer_update:
                        self.start_stop_build_order_timer(invert_run=False, run_value=True)

                # stop the build order timer
                if self.get_hotkey_mouse_flag('stop_timer'):
                    if apply_timer_update:
                        self.start_stop_build_order_timer(invert_run=False, run_value=False)

                # start/stop the build order timer
                if self.get_hotkey_mouse_flag('start_stop_timer'):
                    if apply_timer_update:
                        self.start_stop_build_order_timer(invert_run=True)

                # reset the build order timer
                if self.get_hotkey_mouse_flag('reset_timer'):
                    if apply_timer_update:
                        self.reset_build_order_timer()

        if (not self.hidden) and self.is_mouse_in_window():
            self.build_order_previous_button.hovering_show(self.is_mouse_in_roi_widget)
            self.build_order_next_button.hovering_show(self.is_mouse_in_roi_widget)
            self.build_order_lock_button.hovering_show(self.is_mouse_in_roi_widget)
            if self.build_order_timer['available'] and self.build_order_timer['steps']:
                self.build_order_start_stop_timer.hovering_show(self.is_mouse_in_roi_widget)

    def show_hide(self):
        """Show or hide the overlay (global hotkey)."""
        self.hidden = not self.hidden  # change the hidden state

        if self.hidden:
            self.setWindowOpacity(0.0)
            self.hide()
        else:
            self.show()
            self.setWindowOpacity(self.settings.layout.opacity)
            self.update_position()

    def update_hotkeys(self):
        """Update the hotkeys and the settings file."""
        config_hotkeys = self.panel_config_hotkeys.hotkeys
        config_mouse_checkboxes = self.panel_config_hotkeys.mouse_checkboxes
        config_field_to_mouse = self.panel_config_hotkeys.field_to_mouse

        def split_keyboard_mouse(str_input: str):
            """Split an input between keyboard and mouse parts.

            Parameters
            ----------
            str_input    Input string from 'OverlaySequenceEdit'.

            Returns
            -------
            Keyboard input, '' if no keyboard input.
            Mouse input, '' if no valid mouse input.
            """
            if '+' not in str_input:  # single input
                if str_input in config_field_to_mouse:  # only mouse
                    return '', config_field_to_mouse[str_input]
                else:  # only keyboard
                    return str_input, ''

            else:  # several inputs
                in_split = str_input.split('+')
                keyboard_out = ''
                mouse_out = ''
                for elem in in_split:
                    if elem != '':
                        if elem in config_field_to_mouse:  # mouse part
                            mouse_out = config_field_to_mouse[elem]  # only one mouse input possible (take the last)
                        else:  # keyboard part
                            if keyboard_out == '':
                                keyboard_out = elem
                            else:
                                keyboard_out += '+' + elem
                return keyboard_out, mouse_out

        # update the hotkeys
        print('Hotkeys update:')
        for hotkey_name in self.hotkey_names:
            if hasattr(self.unscaled_settings.hotkeys, hotkey_name):
                hotkey_settings = getattr(self.unscaled_settings.hotkeys, hotkey_name)
                hotkey_str = config_hotkeys[hotkey_name].get_str()

                if config_mouse_checkboxes[hotkey_name].isChecked():  # consider mouse as input
                    keyboard_in, mouse_in = split_keyboard_mouse(hotkey_str)
                    hotkey_settings.keyboard = keyboard_in
                    hotkey_settings.mouse = mouse_in
                else:  # do not consider mouse as input
                    hotkey_settings.keyboard = hotkey_str
                    hotkey_settings.mouse = ''

        self.set_keyboard_mouse()
        self.save_settings()

    def save_settings(self):
        """Save the settings."""
        msg_text = f'Settings saved in {self.settings_file}.'  # message to display
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            f.write(json.dumps(self.unscaled_settings.to_dict(), sort_keys=False, indent=4))
            print(msg_text)

        # open popup message
        popup_message('RTS Overlay - Settings saved', msg_text)

    def update_mouse(self):
        """Update the mouse position."""
        pos = QCursor().pos()
        self.mouse_x = pos.x()
        self.mouse_y = pos.y()

    def is_mouse_in_roi(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if the last updated mouse position (using 'update_mouse') is in a ROI.

        Parameters
        ----------
        x         X position of the ROI (on the screen).
        y         Y position of the ROI (on the screen).
        width     Width of the ROI.
        height    Height of the ROI.

        Returns
        -------
        True if in the ROI.
        """
        return (x <= self.mouse_x <= x + width) and (y <= self.mouse_y <= y + height)

    def is_mouse_in_window(self) -> bool:
        """Checks if the mouse is in the current window.

        Returns
        -------
        True if mouse is in the window.
        """
        return self.is_mouse_in_roi(self.x(), self.y(), self.width(), self.height())

    def is_mouse_in_roi_widget(self, widget: QWidget) -> bool:
        """Check if the last updated mouse position (using 'update_mouse') is in the ROI of a widget.

        Parameters
        ----------
        widget    Widget to check.

        Returns
        -------
        True if mouse is in the ROI.
        """
        return self.is_mouse_in_roi(
            x=self.x() + widget.x(), y=self.y() + widget.y(), width=widget.width(), height=widget.height()
        )

    def move_window(self, event):
        """Move the window according to the mouse motion (arrange state only).

        Parameters
        ----------
        event    Mouse event.
        """
        QApplication.setOverrideCursor(Qt.ArrowCursor)  # set arrow cursor

        if event.buttons() == Qt.NoButton:  # no button pressed
            self.left_click_start = False
        elif event.buttons() == Qt.LeftButton:  # pressing the left button
            if not self.left_click_start:  # starting to press the button
                self.init_x = self.frameGeometry().x()
                self.init_y = self.frameGeometry().y()
                self.old_pos = event.globalPos()
                self.left_click_start = True

            delta = QPoint(event.globalPos() - self.old_pos)  # motion of the mouse
            self.move(self.init_x + delta.x(), self.init_y + delta.y())  # moving the window accordingly
            # update the window position in the settings (for potential save)
            self.settings.layout.upper_left_position = [self.x(), self.y()]
            self.unscaled_settings.layout.upper_left_position = [self.x(), self.y()]
            self.settings.layout.upper_right_position = [widget_x_end(self), self.y()]
            self.unscaled_settings.layout.upper_right_position = [widget_x_end(self), self.y()]

    def save_upper_corner_positions(self):
        """Save of the upper left and right corner positions (kept in sync with the settings)."""
        self.upper_left_position = [self.x(), self.y()]
        self.upper_right_position = [widget_x_end(self), self.y()]
        self.settings.layout.upper_left_position = list(self.upper_left_position)
        self.unscaled_settings.layout.upper_left_position = list(self.upper_left_position)
        self.settings.layout.upper_right_position = list(self.upper_right_position)
        self.unscaled_settings.layout.upper_right_position = list(self.upper_right_position)

    def update_position(self):
        """Update the position to stick to the saved upper left/right corner (read from the settings,
        so that a window drag - which updates the settings - is never reverted)."""
        layout = self.settings.layout
        if layout.overlay_on_right_side:
            self.move(layout.upper_right_position[0] - self.width(), layout.upper_right_position[1])
        else:
            self.move(layout.upper_left_position[0], layout.upper_left_position[1])

    def build_order_previous_step(self):
        """Select the previous page of the build order (or update to -1 sec for timer feature)."""
        if not self.hidden:

            if self.build_order_timer['use_timer']:  # update timer
                self.build_order_timer['time_sec'] -= 1.0
                self.build_order_timer['absolute_time_init'] += 1.0  # like the timer was started 1 sec later
                self.build_order_timer['time_int'] = int(floor(self.build_order_timer['time_sec']))
                self.update_build_order_time_label()
            else:  # update step: go back to the start of the previous page
                build_order_content = self.selected_build_order['build_order']
                rows = max(1, int(getattr(self.settings.layout.build_order, 'display_rows', 1)))

                old_selected_build_order_step_id = self.selected_build_order_step_id
                new_start = old_selected_build_order_step_id
                if new_start > 0:
                    lines = 0
                    while (new_start > 0) and (lines < rows):
                        new_start -= 1
                        lines += len(build_order_content[new_start].get('notes', []) or [])
                if new_start != old_selected_build_order_step_id:
                    self.selected_build_order_step_id = new_start
                    self.update_build_order()  # update the rendering

    def build_order_next_step(self):
        """Select the next page of the build order (or update to +1 sec for timer feature)."""
        if not self.hidden:

            if self.build_order_timer['use_timer']:  # update timer
                self.build_order_timer['time_sec'] += 1.0
                self.build_order_timer['absolute_time_init'] -= 1.0  # like the timer was started 1 sec earlier
                self.build_order_timer['time_int'] = int(floor(self.build_order_timer['time_sec']))
                self.update_build_order_time_label()
            else:  # update step: jump to the start of the next page
                build_order_content = self.selected_build_order['build_order']

                old_selected_build_order_step_id = self.selected_build_order_step_id
                _, page_end = self._get_manual_page_range()
                new_start = min(page_end + 1, len(build_order_content) - 1)
                if new_start != old_selected_build_order_step_id:
                    self.selected_build_order_step_id = new_start
                    self.update_build_order()  # update the rendering

    def select_next_build_order(self):
        """Select the next valid build order (global shortcut, uses the last manager filter)."""
        if self.select_build_order_id(-1):
            return self.select_build_order(self.last_filter_condition)
        return False

    def select_build_order_id(self, build_order_id: int = -1) -> bool:
        """Select build order ID.

        Parameters
        ----------
        build_order_id    ID of the build order, negative to select next build order.

        Returns
        -------
        True if valid build order selection.
        """
        if len(self.valid_build_orders) >= 1:  # at least one build order
            if build_order_id >= 0:  # build order ID given
                if 0 <= build_order_id < len(self.valid_build_orders):
                    self.build_order_selection_id = build_order_id
                else:
                    return False
            else:  # select next build order
                self.build_order_selection_id += 1
                if self.build_order_selection_id >= len(self.valid_build_orders):
                    self.build_order_selection_id = 0
            return True
        return False

    def get_valid_build_orders(self, key_condition: dict = None, search_string: str = ''):
        """Get the names of the valid build orders (with search string from the manager).

        Parameters
        ----------
        key_condition   Dictionary with the keys to look for and their value (to consider as valid), None to skip it.
        search_string   Search string from the manager search bar.
        """
        self.valid_build_orders = []  # reset the list

        # only keep build orders with valid key conditions
        if key_condition is not None:
            valid_key_build_orders = [
                build_order
                for build_order in self.build_orders
                if check_build_order_key_values(build_order, key_condition)
            ]
        else:
            valid_key_build_orders = self.build_orders

        self.valid_key_build_orders_count = len(valid_key_build_orders) # Number of valid build orders for the selected keys

        configuration = self.settings.layout.configuration
        if search_string == '' or search_string == ' ':
            # empty search (or single space): list all build orders for the current filter, up to the limit count
            for count, build_order in enumerate(valid_key_build_orders):
                if count >= configuration.bo_list_max_count:
                    break
                self.valid_build_orders.append(build_order['name'])

        elif configuration.bo_list_fuzz_search:  # do a fuzzy search for matching build orders
            self.valid_build_orders = [
                match[0]
                for match in process.extractBests(
                    search_string,
                    [build_order['name'] for build_order in valid_key_build_orders],
                    score_cutoff=configuration.bo_list_fuzz_score_cutoff,
                    limit=configuration.bo_list_max_count,
                )
            ]

        else:  # search by splitting the words
            search_split = search_string.split(' ')  # split according to spaces

            for build_order in self.build_orders:
                if len(self.valid_build_orders) >= configuration.bo_list_max_count:
                    break

                valid_name = True  # assumes valid name
                build_order_name = build_order['name']
                for search_part in search_split:  # loop on the sub-parts to find
                    if search_part.lower() not in build_order_name.lower():
                        valid_name = False
                        break
                if valid_name:  # add valid build order
                    self.valid_build_orders.append(build_order_name)

        # check all elements are unique
        assert len(set(self.valid_build_orders)) == len(self.valid_build_orders)

        # limit build order selection ID
        if self.build_order_selection_id >= len(self.valid_build_orders):
            self.build_order_selection_id = max(0, len(self.valid_build_orders) - 1)

    def select_build_order(self, key_condition: dict = None) -> bool:
        """Select the requested valid build order and display it on the overlay.

        Parameters
        ----------
        key_condition   Dictionary with the keys to look for and their value, None to skip it.

        Returns
        -------
        True if a valid build order was selected.
        """
        if len(self.valid_build_orders) == 0:
            return False

        assert 0 <= self.build_order_selection_id < len(self.valid_build_orders)
        self.selected_build_order_name = self.valid_build_orders[self.build_order_selection_id]

        self.selected_build_order = None
        for build_order in self.build_orders:
            if (build_order['name'] == self.selected_build_order_name) and (
                (key_condition is None) or check_build_order_key_values(build_order, key_condition)
            ):
                self.selected_build_order = build_order
                break
        if self.selected_build_order is None:
            return False

        self.selected_build_order_step_id = 0
        self.selected_build_order_step_count = len(self.selected_build_order['build_order'])
        assert self.selected_build_order_step_count > 0

        # obtain build order time notes
        if self.build_order_timer['available']:
            self.build_order_timer['steps'] = get_build_order_timer_steps(self.selected_build_order)
            if not self.build_order_timer['steps']:  # non valid timer BO
                self.deactivate_timer()
            else:  # valid timer BO
                self.build_order_timer['steps_ids'] = [0]
                self.build_order_timer['last_steps_ids'] = []
                self.reset_build_order_timer()
                self.start_stop_build_order_timer(invert_run=False, run_value=False)

        self.update_build_order()  # display the selected build order (both states)
        return True

    def hide_elements(self):
        """Hide elements."""
        self.build_order_step_time.hide()
        self.build_order_previous_button.hide()
        self.build_order_next_button.hide()
        if self.build_order_start_stop_timer is not None:
            self.build_order_start_stop_timer.hide()
        self.build_order_hide_button.hide()
        self.build_order_lock_button.hide()

        # display build order
        self.build_order_resources.hide()
        self.build_order_notes.hide()

    def window_color_position_initialization(self):
        """Main window color and position initialization (common to constructor and reload)."""
        layout = self.settings.layout
        color_background = layout.color_background

        # color and opacity
        set_background_opacity(self, color_background, layout.opacity)

        # upper left and right positions
        self.upper_left_position = [layout.upper_left_position[0], layout.upper_left_position[1]]
        self.upper_right_position = [layout.upper_right_position[0], layout.upper_right_position[1]]
        self.update_position()

    def update_build_order(self):
        """Update the build order panel."""
        # clear the elements (also hide them)
        self.build_order_resources.clear()
        self.build_order_notes.clear()

        if self.selected_build_order is None:  # no build order selected
            self.build_order_notes.add_row_from_picture_line(parent=self, line=t('No build order selected.'))

        elif 'build_order' not in self.selected_build_order:  # only display notes
            assert 'notes' in self.selected_build_order
            for note in self.selected_build_order['notes']:
                self.build_order_notes.add_row_from_picture_line(parent=self, line=note)

        self.adapt_notes_to_columns = -1  # no column adaptation by default

        # valid build order selected
        if (self.selected_build_order is not None) and ('build_order' in self.selected_build_order):

            # display selected step
            if self.build_order_timer['use_timer']:
                self.update_build_order_time_label()
            else:
                self.update_build_order_step_label()

    def _get_manual_page_range(self) -> (int, int):
        """Get the range of build order steps displayed as one page in the manual mode.

        The page starts at the current step and accumulates steps until the requested
        count of note lines ('display_rows' setting) is reached.

        Returns
        -------
        (page start step ID, page end step ID), both inclusive.
        """
        build_order_content = self.selected_build_order['build_order']
        count = len(build_order_content)
        rows = max(1, int(getattr(self.settings.layout.build_order, 'display_rows', 1)))

        start = min(max(0, self.selected_build_order_step_id), count - 1)
        lines = len(build_order_content[start].get('notes', []) or [])
        end = start
        while (end + 1 < count) and (lines < rows):
            end += 1
            lines += len(build_order_content[end].get('notes', []) or [])
        return start, end

    def get_build_order_selected_steps_and_ids(self) -> (list, list):
        """Get the build order steps to display.

        Returns
        -------
        Step IDs of the output list (see below).
        List of steps to display.
        """

        if self.build_order_timer['use_timer'] and self.build_order_timer['steps']:
            # get steps to display
            selected_steps_ids, selected_steps = get_build_order_timer_steps_display(
                self.build_order_timer['steps'], self.build_order_timer['steps_ids']
            )
        else:
            # manual mode: display one page of steps (up to 'display_rows' note lines)
            build_order_content = self.selected_build_order['build_order']
            start, end = self._get_manual_page_range()
            selected_steps = build_order_content[start : end + 1]
            assert len(selected_steps) > 0
            selected_steps_ids = list(range(len(selected_steps)))
        assert (len(selected_steps) > 0) and (len(selected_steps_ids) > 0)

        return selected_steps, selected_steps_ids

    def update_build_order_notes(self, selected_steps, selected_steps_ids):
        """Update the notes of the build order.

        Parameters
        ----------
        selected_steps        Step IDs of the output list (see below).
        selected_steps_ids    List of steps to display.
        """

        layout = self.settings.layout
        spacing = ' ' * layout.build_order.resource_spacing  # space between the elements

        # line before notes
        self.build_order_notes.add_row_color(
            parent=self, height=layout.build_order.height_line_notes, color=layout.build_order.color_line_notes
        )

        # loop on the steps for notes
        for step_id, selected_step in enumerate(selected_steps):

            # check if emphasis must be added on the corresponding note
            emphasis_flag = self.build_order_timer['run_timer'] and (step_id in selected_steps_ids)

            notes = selected_step['notes']
            for note_id, note in enumerate(notes):
                # add time if running timer and time available
                line = ''
                resource_step = selected_steps[selected_steps_ids[-1]]  # ID of the step to use to display the resources
                if (
                    (self.build_order_timer['use_timer'])
                    and ('time' in resource_step)
                    and hasattr(layout.build_order, 'show_time_in_notes')
                    and layout.build_order.show_time_in_notes
                ):
                    line += (str(selected_step['time']) if (note_id == 0) else ' ') + '@' + spacing + '@'
                    self.adapt_notes_to_columns = 1
                line += note
                self.build_order_notes.add_row_from_picture_line(parent=self, line=line, emphasis_flag=emphasis_flag)

    def build_order_panel_layout(self):
        """Layout of the build order display (used for both overlay states):
        step label at the left edge, buttons at the right edge."""

        # show elements
        self.build_order_notes.show()
        if self.show_resources:
            self.build_order_resources.show()
        self.build_order_lock_button.show()  # mode switch: available in both states
        if self.selected_build_order is not None:
            self.build_order_step_time.show()
            self.build_order_previous_button.show()
            self.build_order_next_button.show()
            self.build_order_hide_button.show()
            # start/stop timer button only for build orders with time parameters
            show_start_stop = (
                self.build_order_start_stop_timer is not None
                and self.build_order_timer['available']
                and self.build_order_timer['steps']
            )
            if show_start_stop:
                self.build_order_start_stop_timer.show()

        # size and position
        layout = self.settings.layout
        border_size = layout.border_size
        vertical_spacing = layout.vertical_spacing
        action_button_size = layout.action_button_size
        action_button_spacing = layout.action_button_spacing
        bo_next_tab_spacing = layout.build_order.bo_next_tab_spacing

        next_y = border_size + action_button_size + vertical_spacing

        if self.selected_build_order is not None:
            self.build_order_step_time.adjustSize()
            next_y = max(next_y, border_size + self.build_order_step_time.height() + vertical_spacing)

        # build order resources
        if self.show_resources:
            self.build_order_resources.update_size_position(init_y=next_y)
            next_y += self.build_order_resources.row_total_height + vertical_spacing

        # maximum width
        buttons_count = 4  # previous step + next step + hide button + lock button
        show_start_stop = (
            self.build_order_start_stop_timer is not None
            and self.build_order_timer['available']
            and self.build_order_timer['steps']
        )
        if show_start_stop:
            buttons_count += 1
        max_x = max(
            (
                self.build_order_step_time.width()
                + buttons_count * action_button_size
                + (buttons_count - 1) * action_button_spacing
                + bo_next_tab_spacing
            ),
            self.build_order_resources.row_max_width,
        )

        # build order notes
        self.build_order_notes.update_size_position(
            init_y=next_y, panel_init_width=max_x + 2 * border_size, adapt_to_columns=self.adapt_notes_to_columns
        )

        # resize of the full window
        max_x = max(max_x, self.build_order_notes.row_max_width)
        self.resize(max_x + 2 * border_size, next_y + self.build_order_notes.row_total_height + border_size)

        button_space_size = action_button_size + action_button_spacing

        # buttons at the right edge (from right to left: next, previous, start/stop timer, hide, lock)
        next_x = self.width() - border_size - action_button_size
        self.build_order_next_button.move(next_x, border_size)

        next_x -= button_space_size
        self.build_order_previous_button.move(next_x, border_size)

        next_x -= button_space_size
        if show_start_stop:
            self.build_order_start_stop_timer.move(next_x, border_size)
            next_x -= button_space_size

        self.build_order_hide_button.move(next_x, border_size)

        next_x -= button_space_size
        self.build_order_lock_button.move(next_x, border_size)

        # step label at the left edge
        self.build_order_step_time.move(border_size, border_size)

        # position update to stay with the same upper right corner position
        self.update_position()

    def switch_build_order_timer_manual(self):
        """Switch the build order mode between timer and manual."""
        if self.build_order_timer['available'] and self.build_order_timer['steps']:
            self.build_order_timer['use_timer'] = not self.build_order_timer['use_timer']

            if self.build_order_timer['use_timer']:  # timer feature
                self.update_build_order_time_label()
            else:  # manual step selection
                self.build_order_timer['run_timer'] = False
                self.update_build_order_step_label()

            self.build_order_timer['last_time_label'] = ''
            self.build_order_timer['last_steps_ids'] = []

            # select current step
            if (not self.build_order_timer['use_timer']) and (len(self.build_order_timer['steps_ids']) > 0):
                self.selected_build_order_step_id = self.build_order_timer['steps_ids'][0]

            self.update_build_order_start_stop_timer_icon()
            self.update_build_order()
        else:
            self.build_order_timer['use_timer'] = False

    def start_stop_build_order_timer(self, invert_run: bool = True, run_value: bool = True):
        """Start or stop the build order timer.

        Parameters
        ----------
        invert_run    True to invert the running state.
        run_value     Value to set for the running state (ignored for invert_run set to True).
        """
        if self.build_order_timer['use_timer']:
            new_run_state = (not self.build_order_timer['run_timer']) if invert_run else run_value

            if new_run_state != self.build_order_timer['run_timer']:  # only update if change
                self.build_order_timer['run_timer'] = new_run_state

                # panel display
                self.update_build_order_start_stop_timer_icon()  # update icon
                self.build_order_timer['last_time_label'] = ''
                self.build_order_panel_layout()

                # time
                self.build_order_timer['absolute_time_init'] = time.time()
                self.build_order_timer['time_sec_init'] = self.build_order_timer['time_sec']

                self.update_build_order()

    def overlay_start_timer_button(self):
        """Action of the overlay start/stop timer button (switch to timer mode first if needed)."""
        if self.build_order_timer['use_timer']:
            self.start_stop_build_order_timer(invert_run=True)
        elif self.build_order_timer['available'] and self.build_order_timer['steps']:
            self.switch_build_order_timer_manual()  # switch to timer mode
            self.start_stop_build_order_timer(invert_run=False, run_value=True)

    def hide_button_clicked(self):
        """Action of the overlay hide button: two clicks required, to avoid hiding it by mistake."""
        if self.hide_button_armed:
            self.disarm_hide_button()
            self.show_hide()
        else:
            self.hide_button_armed = True
            self.build_order_hide_button.button.setToolTip(t('Click again to hide'))
            self.build_order_hide_button.button.setStyleSheet('border: 2px solid #e05555; border-radius: 4px;')
            QTimer.singleShot(2000, self.disarm_hide_button)

    def disarm_hide_button(self):
        """Disarm the hide button (restore its normal look)."""
        if self.hide_button_armed:
            self.hide_button_armed = False
            self.build_order_hide_button.button.setToolTip(t('Click twice to hide'))
            self.build_order_hide_button.button.setStyleSheet('')

    def shutdown(self):
        """Stop this overlay and release its global hotkeys (before discarding it, e.g. game switch)."""
        self.stop_application = True
        self.hidden = True
        self.setWindowOpacity(0.0)
        self.hide()
        self.keyboard_mouse.shutdown()

    def update_build_order_step_label(self):
        """Update the build order step label (shows the last row of the displayed page)."""
        if not self.hidden:
            _, page_end = self._get_manual_page_range()
            self.build_order_step_time.setText(
                f'{t("Step")}: {page_end + 1}/{self.selected_build_order_step_count}'
            )
            self.build_order_step_time.adjustSize()  # refresh width to avoid overlapping the buttons

    def update_build_order_time_label(self):
        """Update the build order time label."""
        if not self.hidden:

            # check if time is negative
            if self.build_order_timer['time_int'] < 0:
                negative_time = True
                build_order_time_sec = -self.build_order_timer['time_int']
            else:
                negative_time = False
                build_order_time_sec = self.build_order_timer['time_int']

            # convert to 'x:xx' format
            time_min = build_order_time_sec // 60
            time_sec = build_order_time_sec % 60
            negative_str = '-' if (negative_time and (build_order_time_sec != 0)) else ''
            time_label = negative_str + str(time_min) + ':' + str('{:02d}'.format(time_sec))

            if time_label != self.build_order_timer['last_time_label']:
                # update label and layout
                self.build_order_step_time.setText(time_label)
                self.build_order_step_time.adjustSize()  # refresh width to avoid overlapping the buttons
                self.build_order_panel_layout()

                self.build_order_timer['last_time_label'] = time_label

    def reset_build_order_timer(self):
        """Reset the build order timer (set to 0 sec)."""
        if self.build_order_timer['use_timer']:
            self.build_order_timer['time_sec'] = 0.0
            self.build_order_timer['time_int'] = 0
            self.build_order_timer['last_time_int'] = 0
            self.build_order_timer['time_sec_init'] = 0.0
            self.build_order_timer['last_time_label'] = ''
            self.build_order_timer['absolute_time_init'] = time.time()
            self.build_order_timer['steps_ids'] = [0]
            self.build_order_timer['last_steps_ids'] = []
            if self.build_order_timer['use_timer']:
                self.update_build_order_time_label()
            else:
                self.update_build_order_step_label()
            self.update_build_order()
            self.build_order_panel_layout()
