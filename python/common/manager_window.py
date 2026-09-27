import json
import os
import re
import shutil
import subprocess
import webbrowser

from PyQt5.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap

from common.chinese_locale import t  # Chinese UI layer
from common.rts_overlay import PanelID
from common.hotkeys_window import HotkeysWindow


# registry of the supported games (used by the game selector in the manager)
GAME_REGISTRY = {
    'aoe2': {
        'module': 'aoe2.aoe2_game_overlay', 'class': 'AoE2GameOverlay',
        'display_name': '帝国时代2（AoE2）',
        'website': 'https://www.buildorderguide.com', 'website_name': 'buildorderguide.com',
    },
    'aoe4': {
        'module': 'aoe4.aoe4_game_overlay', 'class': 'AoE4GameOverlay',
        'display_name': '帝国时代4（AoE4）',
        'website': 'https://aoe4guides.com', 'website_name': 'aoe4guides.com',
    },
    'aom': {
        'module': 'aom.aom_game_overlay', 'class': 'AoMGameOverlay',
        'display_name': '神话时代（AoM）',
        'website': 'https://craftysalamander.github.io/rtsbuilds/?gameId=aom',
        'website_name': 'rtsbuilds.com（RTS Builds）',
    },
    'sc2': {
        'module': 'sc2.sc2_game_overlay', 'class': 'SC2GameOverlay',
        'display_name': '星际争霸2（SC2）',
        'website': 'https://craftysalamander.github.io/rtsbuilds/?gameId=sc2',
        'website_name': 'rtsbuilds.com（RTS Builds）',
    },
    'wc3': {
        'module': 'wc3.wc3_game_overlay', 'class': 'WC3GameOverlay',
        'display_name': '魔兽争霸3（WC3）',
        'website': 'https://craftysalamander.github.io/rtsbuilds/?gameId=wc3',
        'website_name': 'rtsbuilds.com（RTS Builds）',
    },
}


LIGHT_QSS = """
QMainWindow, QWidget { background-color: #f5f5f5; color: #222222; font-size: 15px; }
QLabel { background: transparent; }
QPushButton { background-color: #ffffff; border: 1px solid #9a9a9a; border-radius: 4px; padding: 6px 14px; }
QPushButton:hover { background-color: #e8f0fe; }
QPushButton:pressed, QPushButton:checked { background-color: #d8e7fb; color: #14406e; font-weight: bold; }
QPushButton#primaryBtn { background-color: #d8e7fb; border-color: #4a86d8; color: #14406e; font-weight: bold; }
QPushButton#guideBtn { border: 1px solid #9a9a9a; }
QPushButton[flashHighlight="true"] { border: 2px solid #f0a500; background-color: #fff3d6; }
QLineEdit, QPlainTextEdit { background-color: #ffffff; border: 1px solid #bbbbbb; border-radius: 4px; padding: 4px; }
QListWidget { background-color: #ffffff; border: 1px solid #bbbbbb; border-radius: 4px; }
QListWidget::item { padding: 6px; }
QListWidget::item:selected { background-color: #d8e7fb; color: #14406e; }
QComboBox { background-color: #ffffff; border: 1px solid #9a9a9a; border-radius: 4px; padding: 3px 8px; }
QComboBox QAbstractItemView { background-color: #ffffff; color: #222222; selection-background-color: #d8e7fb; selection-color: #14406e; }
QTabWidget::pane { border: 1px solid #bbbbbb; top: -1px; }
QTabBar::tab { background: #e8e8e8; color: #666666; padding: 8px 28px; border: 1px solid #bbbbbb; border-bottom: none; }
QTabBar::tab:selected { background: #ffffff; color: #14406e; font-weight: bold; }
QSlider::groove:horizontal { height: 4px; background: #bbbbbb; border-radius: 2px; }
QSlider::handle:horizontal { width: 12px; margin: -5px 0px; border-radius: 6px; background: #555555; }
QMessageBox { background-color: #f5f5f5; }
QLabel#selectHint { font-size: 18px; font-weight: bold; color: #14406e; }
"""

DARK_QSS = """
QMainWindow, QWidget { background-color: #1e1e1e; color: #dddddd; font-size: 15px; }
QLabel { background: transparent; }
QPushButton { background-color: #2b2b2b; border: 1px solid #777777; border-radius: 4px; padding: 6px 14px; color: #eeeeee; }
QPushButton:hover { background-color: #3a3a3a; }
QPushButton:pressed, QPushButton:checked { background-color: #1d3a5f; color: #ffffff; font-weight: bold; }
QPushButton#primaryBtn { background-color: #1d3a5f; border-color: #4a9eff; color: #ffffff; font-weight: bold; }
QPushButton#guideBtn { border: 1px solid #777777; }
QPushButton[flashHighlight="true"] { border: 2px solid #f0a500; background-color: #4a3a10; }
QLineEdit, QPlainTextEdit { background-color: #000000; border: 1px solid #777777; border-radius: 4px; padding: 4px; color: #eeeeee; }
QListWidget { background-color: #000000; border: 1px solid #777777; border-radius: 4px; color: #eeeeee; }
QListWidget::item { padding: 6px; }
QListWidget::item:selected { background-color: #1d3a5f; color: #ffffff; }
QComboBox { background-color: #2b2b2b; border: 1px solid #777777; border-radius: 4px; padding: 3px 8px; color: #eeeeee; }
QComboBox QAbstractItemView { background-color: #2b2b2b; color: #eeeeee; selection-background-color: #1d3a5f; selection-color: #ffffff; }
QTabWidget::pane { border: 1px solid #555555; top: -1px; }
QTabBar::tab { background: #252525; color: #999999; padding: 8px 28px; border: 1px solid #555555; border-bottom: none; }
QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; font-weight: bold; }
QSlider::groove:horizontal { height: 4px; background: #555555; border-radius: 2px; }
QSlider::handle:horizontal { width: 12px; margin: -5px 0px; border-radius: 6px; background: #cccccc; }
QMessageBox { background-color: #1e1e1e; }
QLabel#selectHint { font-size: 18px; font-weight: bold; color: #ffffff; }
"""


class ManagerWindow(QMainWindow):
    """Manager window: hosts all the management UI, controls the overlay window."""

    def __init__(self, app: QApplication, overlay):
        """Constructor

        Parameters
        ----------
        app       Main application instance.
        overlay   The RTSGameOverlay instance managed by this window.
        """
        super().__init__()

        self.app = app
        self.overlay = overlay
        self.overlay.mode_callback = self.on_overlay_mode_changed
        self.last_valid_names = []  # build order names currently displayed in the results list
        self.updating_ui = False  # guard to distinguish programmatic UI updates
        self.filter_combos = []  # list of (key, QComboBox)

        self.setWindowTitle(t('RTS Overlay Manager'))
        self.setWindowIcon(QIcon(self.overlay.game_icon))
        self.resize(880, 720)

        self._build_ui()
        self.initialize_appearance_combos()
        self.apply_theme(self.overlay.unscaled_settings.manager_theme)
        self.refresh_filter_combos()
        self.refresh_results()
        self.update_overlay_controls()
        self.update_guide()
        self.resize_to_guide_bar()

    def resize_to_guide_bar(self):
        """Set the default/minimum window width to exactly fit the guide bar
        (the widest of the two guide rows, since the header is on its own row)."""
        buttons_row = sum(button.sizeHint().width() + 6 for button in self.guide_buttons)
        buttons_row += 3 * (QLabel('→').sizeHint().width() + 6)  # arrows between steps
        buttons_row += self.help_button.sizeHint().width()
        header_row = QLabel(t('Usage steps: (click any step to jump to the corresponding part)')).sizeHint().width()
        width = max(buttons_row, header_row) + 26  # root margins + spacing
        width = max(width, 640)
        self.setMinimumWidth(width)
        self.resize(width, 720)

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        """Build the whole manager interface."""
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(10, 8, 10, 8)

        # --- guide bar (clickable steps: jump to the related tab and highlight the relevant widgets)
        guide_root = QVBoxLayout()
        guide_root.addWidget(QLabel(t('Usage steps: (click any step to jump to the corresponding part)')))
        guide = QHBoxLayout()
        self.guide_buttons = []
        self.guide_base_texts = [
            t('1. Import build orders'),
            t('2. Select and configure'),
            t('3. Show the overlay'),
            t('4. Fix the overlay (in-game state)'),
        ]
        for index, base_text in enumerate(self.guide_base_texts):
            if index > 0:
                guide.addWidget(QLabel('→'))
            button = QPushButton(base_text)
            button.setObjectName('guideBtn')
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked=False, idx=index: self.open_guide_step(idx))
            self.guide_buttons.append(button)
            guide.addWidget(button)
        guide.addStretch()
        self.help_button = QPushButton(t('Help'))
        self.help_button.clicked.connect(self.show_help)
        guide.addWidget(self.help_button)
        guide_root.addLayout(guide)
        root.addLayout(guide_root)

        # --- tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)
        self.tabs.addTab(self._build_import_tab(), t('Import'))
        self.tabs.addTab(self._build_display_tab(), t('Display'))

        # --- bottom bar
        bottom = QHBoxLayout()
        pictures = self.overlay.directory_common_pictures

        save_button = QPushButton(QIcon(os.path.join(pictures, 'action_button', 'save.webp')), t('save settings'))
        save_button.clicked.connect(self.overlay.save_settings)
        bottom.addWidget(save_button)

        settings_folder_button = QPushButton(
            QIcon(os.path.join(pictures, 'action_button', 'gears.webp')), t('Open Settings Folder')
        )
        settings_folder_button.clicked.connect(
            lambda: subprocess.run(['explorer', self.overlay.directory_settings])
        )
        bottom.addWidget(settings_folder_button)

        bottom.addStretch()

        bottom.addWidget(QLabel(t('UI theme')))
        self.theme_light_button = QPushButton(t('Light'))
        self.theme_light_button.setCheckable(True)
        self.theme_light_button.clicked.connect(lambda: self.set_theme('light'))
        bottom.addWidget(self.theme_light_button)
        self.theme_dark_button = QPushButton(t('Dark'))
        self.theme_dark_button.setCheckable(True)
        self.theme_dark_button.clicked.connect(lambda: self.set_theme('dark'))
        bottom.addWidget(self.theme_dark_button)

        quit_button = QPushButton(QIcon(os.path.join(pictures, 'action_button', 'leave.webp')), t('Quit'))
        quit_button.clicked.connect(self.close)
        bottom.addWidget(quit_button)
        root.addLayout(bottom)

    def _build_import_tab(self) -> QWidget:
        """Build the import tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        pictures = self.overlay.directory_common_pictures

        # --- game selection (switching games rebuilds the content and the overlay)
        game_row = QHBoxLayout()
        game_row.addWidget(QLabel(t('Game')))
        self.game_combo = QComboBox()
        for game_key, spec in GAME_REGISTRY.items():
            self.game_combo.addItem(spec['display_name'], game_key)
        self.game_combo.setCurrentIndex(list(GAME_REGISTRY.keys()).index(self.overlay.name_game))
        self.game_combo.currentIndexChanged.connect(self.on_game_changed)
        game_row.addWidget(self.game_combo)
        game_row.addStretch()
        layout.addLayout(game_row)

        # --- find build orders (count for the selected game + website button)
        find_section = QHBoxLayout()
        find_section.addWidget(QLabel(t('Find build orders')))
        self.bo_count_label = QLabel()
        find_section.addWidget(self.bo_count_label)
        find_section.addStretch()
        self.website_button = QPushButton(t('Open build order website'))
        self.website_button.clicked.connect(self.open_build_order_website)
        find_section.addWidget(self.website_button)
        layout.addLayout(find_section)
        self.update_website_button()
        self.update_bo_count()

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # --- import area
        layout.addWidget(QLabel(t('Build order name (leave empty to use the clipboard build order name):')))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        buttons = QHBoxLayout()
        clipboard_button = QPushButton(
            QIcon(os.path.join(pictures, 'action_button', 'feather.webp')), t('Import from clipboard')
        )
        clipboard_button.setObjectName('primaryBtn')
        clipboard_button.clicked.connect(self.import_from_clipboard)
        buttons.addWidget(clipboard_button)
        self.import_buttons = [clipboard_button]

        bo_folder_button = QPushButton(t('Open build order folder'))
        bo_folder_button.clicked.connect(lambda: subprocess.run(['explorer', self.overlay.directory_build_orders]))
        buttons.addWidget(bo_folder_button)
        buttons.addStretch()
        layout.addLayout(buttons)

        layout.addWidget(QLabel(t('The build order is read from the clipboard; if the name field is empty, the name inside the build order is used.')))
        layout.addStretch(2)
        return tab

    def on_game_changed(self):
        """Switch the managed game (rebuild the overlay and the manager content)."""
        if self.updating_ui:
            return
        game_key = self.game_combo.currentData()
        if game_key and (game_key != self.overlay.name_game):
            self.switch_game(game_key)

    def open_build_order_website(self):
        """Open the build order website of the selected game."""
        spec = GAME_REGISTRY[self.overlay.name_game]
        webbrowser.open(spec['website'])

    def update_website_button(self):
        """Refresh the website button tooltip for the selected game."""
        spec = GAME_REGISTRY[self.overlay.name_game]
        self.website_button.setToolTip(spec['website_name'] + ' — ' + spec['website'])

    def update_bo_count(self):
        """Refresh the build order count label for the selected game."""
        self.bo_count_label.setText(f"{t('Existing build orders')}: {len(self.overlay.build_orders)}")

    def switch_game(self, game_key: str):
        """Switch the managed game: create the new overlay, discard the old one, refresh everything."""
        if game_key not in GAME_REGISTRY:
            return
        spec = GAME_REGISTRY[game_key]
        module = __import__(spec['module'], fromlist=[spec['class']])
        new_overlay = getattr(module, spec['class'])(app=self.app, directory_main=self.overlay.directory_main)

        old_overlay = self.overlay
        self.overlay = new_overlay
        new_overlay.mode_callback = self.on_overlay_mode_changed
        new_overlay.unscaled_settings.manager_theme = self.theme
        old_overlay.shutdown()  # release its global hotkeys and hide it
        old_overlay.deleteLater()

        # rebuild the manager content for the new game
        self.initialize_appearance_combos()
        self.refresh_filter_combos()
        self.apply_theme(self.theme)
        self.update_website_button()
        self.update_bo_count()
        self.opacity_slider.setSliderPosition(int(round(new_overlay.settings.layout.opacity * 100)))
        self.refresh_results()
        self.update_overlay_controls()
        self.update_guide()

    def _make_collapsible(self, title: str, content: QWidget, collapsed: bool = True):
        """Create a collapsible section (header button + content widget)."""
        header = QPushButton(('▶ ' if collapsed else '▼ ') + title)
        header.setCheckable(True)
        header.setChecked(not collapsed)
        content.setVisible(not collapsed)

        def toggle(checked: bool):
            content.setVisible(checked)
            header.setText(('▼ ' if checked else '▶ ') + title)

        header.clicked.connect(toggle)
        return header

    def _build_display_tab(self) -> QWidget:
        """Build the display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        pictures = self.overlay.directory_common_pictures

        # --- reminder at the top (large and bold) + highlights button
        rem_row = QHBoxLayout()
        select_label = QLabel(t('Select a build order'))
        select_label.setObjectName('selectHint')
        rem_row.addWidget(select_label)
        rem_row.addStretch()
        highlights_button = QPushButton(t('Build order highlights'))
        highlights_button.clicked.connect(lambda: self.show_highlights_window(False))
        rem_row.addWidget(highlights_button)
        layout.addLayout(rem_row)

        # --- selection (filter combos are inserted by 'refresh_filter_combos')
        selection_row = QHBoxLayout()
        selection_row.addWidget(QLabel(t('Faction')))
        self.filters_layout = QHBoxLayout()
        selection_row.addLayout(self.filters_layout)
        selection_row.addStretch()
        selection_row.addWidget(QLabel(t('Search')))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(t('Filter build orders by keywords...'))
        self.search_edit.textChanged.connect(self.refresh_results)
        self.search_edit.returnPressed.connect(self.select_current_result)
        selection_row.addWidget(self.search_edit, 2)
        layout.addLayout(selection_row)

        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_result_clicked)
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_results_menu)
        layout.addWidget(self.results_list, 1)

        # --- overlay state
        overlay_section = QHBoxLayout()
        overlay_section.addWidget(QLabel(t('Overlay')))
        self.overlay_toggle_button = QPushButton()
        self.overlay_toggle_button.clicked.connect(self.toggle_overlay)
        overlay_section.addWidget(self.overlay_toggle_button)
        overlay_section.addWidget(QLabel(t('State')))
        self.state_move_button = QPushButton(t('Move mode'))
        self.state_move_button.setCheckable(True)
        self.state_move_button.clicked.connect(lambda: self.set_overlay_state(True))
        overlay_section.addWidget(self.state_move_button)
        self.state_fixed_button = QPushButton(t('Fixed mode'))
        self.state_fixed_button.setCheckable(True)
        self.state_fixed_button.clicked.connect(lambda: self.set_overlay_state(False))
        overlay_section.addWidget(self.state_fixed_button)
        overlay_section.addWidget(QLabel(t('Fixed mode: no drag, buttons clickable, other areas click-through')))
        overlay_section.addStretch()
        layout.addLayout(overlay_section)

        # --- appearance (collapsible, collapsed by default)
        appearance_content = QWidget()
        appearance_layout = QHBoxLayout(appearance_content)
        appearance_layout.setContentsMargins(0, 0, 0, 0)
        appearance_layout.addWidget(QLabel(t('Background color')))
        self.bg_color_button = QPushButton(t('Background color'))
        self.bg_color_button.clicked.connect(self.choose_background_color)
        appearance_layout.addWidget(self.bg_color_button)
        appearance_layout.addWidget(QLabel(t('Opacity')))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setFixedWidth(120)
        self.opacity_slider.setSliderPosition(int(round(self.overlay.settings.layout.opacity * 100)))
        self.opacity_slider.valueChanged.connect(self.update_opacity_label)
        self.opacity_slider.sliderReleased.connect(self.apply_opacity)
        appearance_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel()
        appearance_layout.addWidget(self.opacity_label)
        appearance_layout.addWidget(QLabel(t('Font size')))
        self.font_size_combo = QComboBox()
        appearance_layout.addWidget(self.font_size_combo)
        appearance_layout.addWidget(QLabel(t('Scaling')))
        self.scaling_combo = QComboBox()
        appearance_layout.addWidget(self.scaling_combo)
        appearance_layout.addWidget(QLabel(t('Display rows')))
        self.display_rows_combo = QComboBox()
        appearance_layout.addWidget(self.display_rows_combo)
        appearance_layout.addStretch()
        self.appearance_header = self._make_collapsible(t('Appearance'), appearance_content, collapsed=True)
        layout.addWidget(self.appearance_header)
        layout.addWidget(appearance_content)

        # --- display control (collapsible, collapsed by default)
        control_content = QWidget()
        control_layout = QHBoxLayout(control_content)
        control_layout.setContentsMargins(0, 0, 0, 0)
        start_stop_button = QPushButton(
            QIcon(os.path.join(pictures, 'action_button', 'start_stop.webp')), t('Start/Stop timer')
        )
        start_stop_button.clicked.connect(self.overlay.overlay_start_timer_button)
        control_layout.addWidget(start_stop_button)
        previous_button = QPushButton(
            QIcon(os.path.join(pictures, 'action_button', 'previous.webp')), t('Previous step')
        )
        previous_button.clicked.connect(self.overlay.build_order_previous_step)
        control_layout.addWidget(previous_button)
        next_button = QPushButton(QIcon(os.path.join(pictures, 'action_button', 'next.webp')), t('Next step'))
        next_button.clicked.connect(self.overlay.build_order_next_step)
        control_layout.addWidget(next_button)
        reset_button = QPushButton(QIcon(os.path.join(pictures, 'action_button', 'timer_0.webp')), t('Reset timer'))
        reset_button.clicked.connect(self.overlay.reset_build_order_timer)
        control_layout.addWidget(reset_button)
        control_layout.addStretch()
        self.control_header = self._make_collapsible(t('Display control'), control_content, collapsed=True)
        layout.addWidget(self.control_header)
        layout.addWidget(control_content)

        # --- hotkeys (collapsible, collapsed by default)
        hotkeys_content = QWidget()
        hotkeys_layout = QHBoxLayout(hotkeys_content)
        hotkeys_layout.setContentsMargins(0, 0, 0, 0)
        hotkeys_button = QPushButton(
            QIcon(os.path.join(pictures, 'action_button', 'gears.webp')), t('Open hotkeys configuration')
        )
        hotkeys_button.clicked.connect(self.open_hotkeys_window)
        hotkeys_layout.addWidget(hotkeys_button)
        hotkeys_layout.addWidget(QLabel(t('Global hotkeys work even while playing (no need to focus the overlay)')))
        hotkeys_layout.addStretch()
        self.hotkeys_header = self._make_collapsible(t('Hotkeys'), hotkeys_content, collapsed=True)
        layout.addWidget(self.hotkeys_header)
        layout.addWidget(hotkeys_content)

        layout.addStretch()
        return tab

    def open_hotkeys_window(self):
        """Open/close the hotkeys configuration window."""
        if (self.overlay.panel_config_hotkeys is not None) and self.overlay.panel_config_hotkeys.isVisible():
            self.overlay.panel_config_hotkeys.close()
            self.overlay.panel_config_hotkeys = None
            self.overlay.keyboard_mouse.set_all_flags(False)
        else:
            self.overlay.panel_config_hotkeys = HotkeysWindow(
                parent=self.overlay,
                hotkeys=self.overlay.unscaled_settings.hotkeys,
                game_icon=self.overlay.game_icon,
                mouse_image=os.path.join(self.overlay.directory_common_pictures, self.overlay.images.mouse),
                configuration_folder=self.overlay.directory_config_game,
                panel_settings=self.overlay.settings.panel_hotkeys,
                timer_flag=self.overlay.build_order_timer['available'],
            )

    def show_results_menu(self, pos):
        """Right-click menu on the results list: rename or remove (to the '弃用区' folder)."""
        item = self.results_list.itemAt(pos)
        if item is None:
            return
        row = self.results_list.row(item)
        if not (0 <= row < len(self.last_valid_names)):
            return
        build_order_name = self.last_valid_names[row]

        menu = QMenu(self)
        rename_action = menu.addAction(t('Rename'))
        delete_action = menu.addAction(t('Delete (to deprecation folder)'))
        action = menu.exec_(self.results_list.mapToGlobal(pos))
        if action == rename_action:
            self.rename_build_order(build_order_name)
        elif action == delete_action:
            self.delete_build_order(build_order_name)

    # ------------------------------------------------------- import actions

    def import_from_clipboard(self):
        """Import the build order from the clipboard content."""
        name_override = self.name_edit.text().strip()
        self.save_build_order_from_text(self.app.clipboard().text(), name_override)

    def save_build_order_from_text(self, pasted_text: str, name_override: str = ''):
        """Check, save the build order text and reload the build orders."""
        if not pasted_text.strip():
            self.show_message(t('Error'), t('No text was pasted.'))
            return

        try:
            json_data = json.loads(pasted_text)

            valid_bo, bo_error_msg = self.overlay.check_valid_build_order(json_data)
            if not valid_bo:
                self.show_message(t('Error'), t('Invalid build order format') + f': {bo_error_msg}')
                return

            if name_override:  # name field has priority
                build_order_name = name_override
            elif 'name' in json_data:
                build_order_name = json_data['name']
            else:
                self.show_message(t('Error'), t('Build order is missing a name.'))
                return
        except json.JSONDecodeError:
            self.show_message(t('Error'), t('Could not parse the build order. Invalid JSON format.'))
            return

        # sanitize the filename: replace ALL spaces with "_" and remove dangerous characters
        sanitized_name = build_order_name.replace(' ', '_')
        sanitized_name = re.sub(r'[\\/*?: "<>|]', '', sanitized_name)
        filename = f"{sanitized_name}.json"
        filepath = os.path.join(self.overlay.directory_build_orders, filename)

        if os.path.exists(filepath):
            self.show_message(t('Error'), t('Build order name already exists') + f": '{build_order_name}'")
            return

        try:
            os.makedirs(self.overlay.directory_build_orders, exist_ok=True)
            json_data['name'] = build_order_name  # keep the name consistent with the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(json_data, ensure_ascii=False, indent=4))

            self.show_message(t('Success'), t('Build order saved as') + f": {filename}")
            self.overlay.reload(update_settings=False)  # reload build orders
            self.update_bo_count()
            self.refresh_results()
            self.update_guide()
        except Exception as e:
            self.show_message(t('Error'), t('Failed to save build order') + f': {str(e)}')

    def find_build_order_file(self, build_order_name: str):
        """Find the JSON file containing a build order with the requested name (search is recursive)."""
        for root, dirs, files in os.walk(self.overlay.directory_build_orders):
            for file_name in files:
                if not file_name.endswith('.json'):
                    continue
                path = os.path.join(root, file_name)
                try:
                    with open(path, 'rb') as f:
                        data = json.load(f)
                except Exception:
                    continue
                if isinstance(data, dict) and (data.get('name') == build_order_name):
                    return path
        return None

    def rename_build_order(self, build_order_name: str):
        """Rename a build order file."""
        path = self.find_build_order_file(build_order_name)
        if path is None:
            self.show_message(t('Error'), t('Build order file not found.'))
            return

        new_name, ok = QInputDialog.getText(self, t('Rename'), t('New name:'), text=build_order_name)
        if not ok or not new_name.strip() or (new_name.strip() == build_order_name):
            return

        new_name = new_name.strip()
        sanitized_name = new_name.replace(' ', '_')
        sanitized_name = re.sub(r'[\\/*?: "<>|]', '', sanitized_name)
        new_path = os.path.join(os.path.dirname(path), f"{sanitized_name}.json")

        if os.path.exists(new_path):
            self.show_message(t('Error'), t('Build order name already exists') + f": '{new_name}'")
            return

        try:
            with open(path, 'rb') as f:
                data = json.load(f)
            data['name'] = new_name
            os.rename(path, new_path)
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=4))
            self.overlay.reload(update_settings=False)
            self.update_bo_count()
            self.refresh_results()
            self.update_guide()
        except Exception as e:
            self.show_message(t('Error'), t('Failed to save build order') + f': {str(e)}')

    def delete_build_order(self, build_order_name: str):
        """Remove a build order from the list by MOVING its file to the '弃用区' folder (never deleted)."""
        path = self.find_build_order_file(build_order_name)
        if path is None:
            self.show_message(t('Error'), t('Build order file not found.'))
            return

        answer = QMessageBox.question(
            self,
            t('Delete'),
            t('The build order file will be moved to the "弃用区" folder (not deleted). Continue?')
            + f'\n\n{build_order_name}',
        )
        if answer != QMessageBox.Yes:
            return

        try:
            # 弃用区放在 build_orders 的同级目录（避免被建造顺序扫描重新加载）
            deprecation_dir = os.path.join(os.path.dirname(self.overlay.directory_build_orders), '弃用区')
            os.makedirs(deprecation_dir, exist_ok=True)
            target = os.path.join(deprecation_dir, os.path.basename(path))
            if os.path.exists(target):  # never overwrite: add a numeric suffix
                base, ext = os.path.splitext(os.path.basename(path))
                count = 1
                while os.path.exists(target):
                    target = os.path.join(deprecation_dir, f"{base}_({count}){ext}")
                    count += 1
            shutil.move(path, target)
            self.overlay.reload(update_settings=False)
            self.update_bo_count()
            self.refresh_results()
            self.update_guide()
        except Exception as e:
            self.show_message(t('Error'), t('Failed to save build order') + f': {str(e)}')

    def show_message(self, title: str, text: str):
        """Display an information/warning message box."""
        message_box = QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.exec_()

    def show_help(self):
        """Display the how-to-use message box."""
        self.show_message(t('Help'), t('HOW_TO_USE_TEXT'))

    # ------------------------------------------------- display tab actions

    def current_key_condition(self) -> dict:
        """Build the key condition dictionary from the filter combo boxes."""
        key_condition = {}
        for key, combo in self.filter_combos:
            key_condition[key] = combo.currentText()
        return key_condition

    def refresh_filter_combos(self):
        """(Re)build the faction filter combo boxes from the overlay specifications."""
        self.updating_ui = True
        while self.filters_layout.count() > 0:
            item = self.filters_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self.filter_combos = []

        for spec in self.overlay.get_filter_specs():
            combo = QComboBox()
            for item_name, item_icon in spec['items']:
                if item_icon and os.path.exists(item_icon):
                    combo.addItem(QIcon(item_icon), item_name)
                else:
                    combo.addItem(item_name)
            combo.setCurrentIndex(0)
            combo.setToolTip(t(spec['tooltip']))
            combo.currentIndexChanged.connect(self.refresh_results)
            self.filters_layout.addWidget(combo)
            self.filter_combos.append((spec['key'], combo))
        self.updating_ui = False

    def refresh_results(self):
        """Refresh the build order results list from the current search."""
        if self.updating_ui:
            return
        key_condition = self.current_key_condition()
        search_string = self.search_edit.text()
        names, message = self.overlay.get_build_order_names(key_condition, search_string)
        self.last_valid_names = names

        self.results_list.blockSignals(True)
        self.results_list.clear()
        if names:
            for index, name in enumerate(names):
                item = QListWidgetItem(name)
                if index == self.overlay.build_order_selection_id:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.results_list.addItem(item)
        elif message:
            self.results_list.addItem(QListWidgetItem(message))
        self.results_list.blockSignals(False)

    def on_result_clicked(self, item: QListWidgetItem):
        """Select the clicked build order."""
        row = self.results_list.row(item)
        if 0 <= row < len(self.last_valid_names):
            if self.overlay.select_build_order_id(row):
                self.overlay.select_build_order(self.current_key_condition())
            self.refresh_results()
            self.update_guide()

    def select_current_result(self):
        """Select the currently highlighted build order (Enter key in the search bar)."""
        if len(self.last_valid_names) == 0:
            return
        if self.overlay.select_build_order_id(self.overlay.build_order_selection_id):
            self.overlay.select_build_order(self.current_key_condition())
        self.refresh_results()
        self.update_guide()

    # --------------------------------------------------- overlay controls

    def toggle_overlay(self):
        """Show/hide the overlay window (highlights window shown first when a build order is selected)."""
        if self.overlay.overlay_visible():
            self.overlay.close_overlay()
        elif self.overlay.selected_build_order is not None:
            self.show_highlights_window(start_overlay=True)
        else:
            self.overlay.open_overlay()
        self.update_overlay_controls()
        self.update_guide()

    def _open_overlay_after_highlights(self):
        """Called when the highlights window closes: open the overlay if requested."""
        if getattr(self, '_highlights_start_overlay', False):
            self._highlights_start_overlay = False
            self.overlay.open_overlay()
        self.update_overlay_controls()
        self.update_guide()

    def show_highlights_window(self, start_overlay: bool = False):
        """Show the build order highlights window (units and technologies)."""
        bo = self.overlay.selected_build_order
        if bo is None or 'build_order' not in bo:
            if start_overlay:
                self.toggle_overlay()
            return

        highlights = self.overlay.get_build_order_highlights()
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{t('Build order highlights')}：{self.overlay.selected_build_order_name or ''}")
        layout = QVBoxLayout(dialog)

        headline = QLabel(self.overlay.selected_build_order_name or '')
        headline.setObjectName('highlightsHeadline')
        layout.addWidget(headline)

        source = (bo.get('source') or '').replace('https://', '').replace('http://', '')
        layout.addWidget(QLabel(f"{t('Civilization')}：<b>{bo.get('civilization', '—')}</b>　｜　{t('Step')}：{len(bo['build_order'])}　｜　{t('Source')}：{source}"))

        def add_items(container, items):
            row = QHBoxLayout()
            for item in items:
                box = QVBoxLayout()
                icon_label = QLabel()
                icon_label.setPixmap(QPixmap(item['icon']).scaled(
                    44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setAlignment(Qt.AlignCenter)
                box.addWidget(icon_label)
                name_label = QLabel(item['name'])
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setWordWrap(True)
                box.addWidget(name_label)
                container.addLayout(box)

        if highlights['units']:
            layout.addWidget(QLabel(t('Main units (in build order appearance order)')))
            row = QHBoxLayout()
            add_items(row, highlights['units'])
            layout.addLayout(row)
        if highlights['techs']:
            layout.addWidget(QLabel(t('Main technologies (in build order appearance order)')))
            row = QHBoxLayout()
            add_items(row, highlights['techs'])
            layout.addLayout(row)
        if not highlights['units'] and not highlights['techs']:
            layout.addWidget(QLabel(t('No highlights found for this build order.')))

        tip = QLabel(t('HIGHLIGHTS_TIP'))
        tip.setWordWrap(True)
        layout.addWidget(tip)

        buttons = QHBoxLayout()
        buttons.addStretch()
        close_button = QPushButton(t('Start game, close'))
        close_button.setObjectName('primaryBtn')
        close_button.clicked.connect(dialog.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

        self._highlights_start_overlay = start_overlay
        dialog.finished.connect(self._open_overlay_after_highlights)
        self._highlights_dialog = dialog
        dialog.show()

    def set_overlay_state(self, arrange: bool):
        """Switch the overlay state (arrange pre-game / in-game)."""
        target = PanelID.CONFIG if arrange else PanelID.BUILD_ORDER
        if self.overlay.selected_panel != target:
            self.overlay.next_panel()  # notifies this window through the callback
        self.update_overlay_controls()

    def on_overlay_mode_changed(self, panel_id):
        """Called by the overlay when its state changed (e.g. global hotkey)."""
        self.update_overlay_controls()
        self.update_guide()

    def update_overlay_controls(self):
        """Refresh the overlay toggle button and state buttons."""
        visible = self.overlay.overlay_visible()
        self.overlay_toggle_button.setText(t('Hide overlay') if visible else t('Show overlay'))
        self.state_move_button.setChecked(self.overlay.selected_panel == PanelID.CONFIG)
        self.state_fixed_button.setChecked(self.overlay.selected_panel == PanelID.BUILD_ORDER)

    # ------------------------------------------------- timer call delegates

    def timer_build_order_call(self):
        """Delegate to the current overlay (the main timers stay bound to the manager)."""
        self.overlay.timer_build_order_call()

    def timer_mouse_keyboard_call(self):
        """Delegate to the current overlay (the main timers stay bound to the manager)."""
        self.overlay.timer_mouse_keyboard_call()

    # -------------------------------------------------------- appearance

    def initialize_appearance_combos(self):
        """Populate the font size and scaling combo boxes."""
        self.updating_ui = True
        layout = self.overlay.unscaled_settings.layout
        configuration = layout.configuration

        self.font_size_combo.clear()
        for font_size in range(configuration.font_size_limits[0], configuration.font_size_limits[1] + 1):
            self.font_size_combo.addItem(f'{font_size} p', font_size)
            if font_size == layout.font_size:
                self.font_size_combo.setCurrentIndex(self.font_size_combo.count() - 1)
        self.font_size_combo.currentIndexChanged.connect(self.on_font_size_changed)

        self.scaling_combo.clear()
        for scaling in configuration.scaling_list:
            self.scaling_combo.addItem(f'{scaling} %', scaling)
            if scaling == layout.scaling:
                self.scaling_combo.setCurrentIndex(self.scaling_combo.count() - 1)
        self.scaling_combo.currentIndexChanged.connect(self.on_scaling_changed)

        self.display_rows_combo.clear()
        for display_rows in range(1, 6):
            self.display_rows_combo.addItem(str(display_rows), display_rows)
            if display_rows == layout.build_order.display_rows:
                self.display_rows_combo.setCurrentIndex(self.display_rows_combo.count() - 1)
        self.display_rows_combo.currentIndexChanged.connect(self.on_display_rows_changed)
        self.updating_ui = False

    def on_display_rows_changed(self):
        """Apply the new count of displayed note lines per page to the overlay."""
        if self.updating_ui:
            return
        new_rows = self.display_rows_combo.currentData()
        if new_rows is None:
            return
        self.overlay.unscaled_settings.layout.build_order.display_rows = new_rows
        self.overlay.settings.layout.build_order.display_rows = new_rows
        self.overlay.update_build_order()  # re-render the current page

    def choose_background_color(self):
        """Choose the overlay background color."""
        current = self.overlay.settings.layout.color_background
        initial = QColor(current[0], current[1], current[2])
        color = QColorDialog.getColor(initial, self, t('Background color'))
        if color.isValid():
            new_color = [color.red(), color.green(), color.blue()]
            self.overlay.unscaled_settings.layout.color_background = new_color
            self.overlay.settings.layout.color_background = new_color
            self.overlay.window_color_position_initialization()

    def update_opacity_label(self):
        """Update the opacity label next to the slider."""
        self.opacity_label.setText(f'{self.opacity_slider.sliderPosition()} %')

    def apply_opacity(self):
        """Apply the opacity value to the overlay."""
        opacity = self.opacity_slider.sliderPosition() / 100.0
        self.overlay.unscaled_settings.layout.opacity = opacity
        self.overlay.settings.layout.opacity = opacity
        self.overlay.window_color_position_initialization()

    def on_font_size_changed(self):
        """Apply the new font size to the overlay."""
        if self.updating_ui:
            return
        new_font = self.font_size_combo.currentData()
        if new_font is None:
            return
        self.overlay.unscaled_settings.layout.font_size = new_font
        self.overlay.settings.layout.font_size = new_font
        self.overlay.unscaled_settings.panel_hotkeys.font_size = new_font
        self.overlay.settings.panel_hotkeys.font_size = new_font
        self.overlay.reload(update_settings=False)

    def on_scaling_changed(self):
        """Apply the new scaling value to the overlay."""
        if self.updating_ui:
            return
        new_scaling = self.scaling_combo.currentData()
        if new_scaling is None:
            return
        self.overlay.unscaled_settings.layout.scaling = new_scaling
        self.overlay.settings.layout.scaling = new_scaling
        self.overlay.reload(update_settings=False)

    # ------------------------------------------------------ theme & guide

    def set_theme(self, theme: str):
        """Switch the manager theme ('light' or 'dark')."""
        self.apply_theme(theme)
        self.overlay.unscaled_settings.manager_theme = theme

    def apply_theme(self, theme: str):
        """Apply the theme stylesheet and refresh the theme buttons."""
        self.theme = theme if theme in ('light', 'dark') else 'light'
        self.setStyleSheet(DARK_QSS if (self.theme == 'dark') else LIGHT_QSS)
        self.theme_light_button.setChecked(self.theme == 'light')
        self.theme_dark_button.setChecked(self.theme == 'dark')

    def open_guide_step(self, index: int):
        """Open the tab related to the guide step and highlight the relevant widgets."""
        if index == 0:  # import
            self.tabs.setCurrentIndex(0)
            targets = [self.name_edit] + self.import_buttons
        elif index == 1:  # select and configure
            self.tabs.setCurrentIndex(1)
            targets = [self.search_edit, self.results_list] + [combo for _, combo in self.filter_combos]
        elif index == 2:  # show the overlay (move state)
            self.tabs.setCurrentIndex(1)
            if not self.overlay.overlay_visible():
                self.toggle_overlay()
            targets = [self.overlay_toggle_button, self.state_move_button]
        else:  # fix the overlay: toggle between the fixed and move states
            self.tabs.setCurrentIndex(1)
            if not self.overlay.overlay_visible():
                self.toggle_overlay()
            # toggle: currently fixed -> switch to move; currently move -> switch to fixed
            self.set_overlay_state(self.overlay.selected_panel == PanelID.BUILD_ORDER)
            targets = [self.state_fixed_button, self.state_move_button]
        self.update_overlay_controls()
        self.update_guide()
        self.flash_widgets(targets)

    def flash_widgets(self, widgets):
        """Temporarily highlight the given widgets (yellow border, ~1.6 s)."""
        for widget in widgets:
            widget.setProperty('flashHighlight', True)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
        QTimer.singleShot(1600, lambda: self._clear_flash(widgets))

    def _clear_flash(self, widgets):
        """Clear the temporary highlight."""
        for widget in widgets:
            widget.setProperty('flashHighlight', False)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def update_guide(self):
        """Refresh the guide bar (✅ when the step is done, ⬜ otherwise)."""
        states = [
            len(self.overlay.build_orders) > 0,
            self.overlay.selected_build_order is not None,
            self.overlay.overlay_visible(),
            self.overlay.overlay_visible() and (self.overlay.selected_panel == PanelID.BUILD_ORDER),
        ]
        for button, base_text, done in zip(self.guide_buttons, self.guide_base_texts, states):
            button.setText(('✅ ' if done else '⬜ ') + base_text)

    # -------------------------------------------------------------- close

    def closeEvent(self, event):
        """Closing the manager quits the whole application."""
        self.overlay.quit_application()
        event.accept()
