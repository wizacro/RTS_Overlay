# Game overlay application for Age of Empires II (AoE2)
import sys
import pathlib
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from aoe2.aoe2_game_overlay import AoE2GameOverlay
from common.manager_window import ManagerWindow

# install the Chinese UI layer before creating any window
from common.chinese_locale import install as install_chinese_ui
install_chinese_ui()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AoE2GameOverlay(app=app, directory_main=str(pathlib.Path(__file__).parent.resolve()))
    manager = ManagerWindow(app=app, overlay=window)
    manager.show()

    # timer to call the functions related to mouse and keyboard inputs
    timer = QTimer()
    timer.timeout.connect(manager.timer_build_order_call)
    timer.timeout.connect(manager.timer_mouse_keyboard_call)
    timer.setInterval(window.settings.call_ms)
    timer.start()

    exit_event = app.exec()
    sys.exit(exit_event)
