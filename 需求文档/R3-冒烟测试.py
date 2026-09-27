# -*- coding: utf-8 -*-
"""R3/R6 冒烟测试 + 覆盖率检查（管理器 + 悬浮窗双窗口改版）。

用法：在仓库根目录执行  python 需求文档/R3-冒烟测试.py

每个游戏在独立子进程中离屏测试（与真实使用一致）：
  双窗构建 → 中文文案断言 → 便携式配置/迁移 → 导入（含非法内容拒绝）→
  搜索选择 → 要点提取与要点窗口 → 悬浮窗开关（经管理器，含要点弹窗处理）→
  位置回归 → 隐藏双击 → 锁按钮 → 状态切换 → 主题 → reload 联动 → 游戏切换。
第二部分：AST 扫描 UI 字符串调用点 + tooltip/变量赋值/返回值，与翻译字典比对。

说明：pynput 监听器与被测逻辑无关，子进程中以桩替换；模态弹窗（exec_/question/
QInputDialog）在离屏环境会崩溃或挂起，分别打桩或跳过；结束用 os._exit 跳过拆解段错误。
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY_DIR = REPO / "python"

failures = []

RUNNER = r'''
import json
import os
import sys
import tempfile
from pathlib import Path

game_key, class_name, expected_title = sys.argv[1], sys.argv[2], sys.argv[3]
py_dir = Path(sys.argv[4])
sys.path.insert(0, str(py_dir))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pynput.mouse as _pm
class _FakeListener:
    def __init__(self, *a, **k): pass
    def start(self): pass
    def stop(self): pass
    def join(self): pass
_pm.Listener = _FakeListener

from PyQt5.QtWidgets import QApplication, QMessageBox
from common.chinese_locale import install
install()
app = QApplication([])

# 离屏环境桩：模态弹窗会崩溃/挂起
QMessageBox.exec_ = lambda self, *a, **k: 0
QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.Yes)

from common.rts_overlay import PanelID
from common.manager_window import ManagerWindow

module = __import__(f"{game_key}.{game_key}_game_overlay", fromlist=[class_name])
overlay = getattr(module, class_name)(app=app, directory_main=str(py_dir))
manager = ManagerWindow(app=app, overlay=overlay)
app.processEvents()

failures = []
skips = []
def check(label, condition, detail=""):
    if condition:
        print(f"  OK {label}")
    else:
        failures.append(f"{label} {detail}")
        print(f"  FAIL {label} {detail}")

def close_highlights_if_any():
    """若要点窗口已弹出则关闭（按设计：关闭后悬浮窗才开启）。"""
    d = getattr(manager, "_highlights_dialog", None)
    if d is not None and d.isVisible():
        d.close()
        app.processEvents()

# --- 1. 双窗构建与文案
check("管理器标题", manager.windowTitle() == "RTS Overlay 管理器", manager.windowTitle())
check("悬浮窗标题", overlay.windowTitle() == expected_title, overlay.windowTitle())
check("悬浮窗初始隐藏", not overlay.overlay_visible())
check("开启按钮文案", manager.overlay_toggle_button.text() == "开启悬浮窗", manager.overlay_toggle_button.text())
check("指引按钮数", len(manager.guide_buttons) == 4)
check("指引完成前缀", manager.guide_buttons[3].text().startswith(("⬜", "✅")), manager.guide_buttons[3].text())
check("主题按钮", manager.theme_light_button.text() == "浅色" and manager.theme_dark_button.text() == "深色")
check("状态按钮文案", manager.state_move_button.text() == "移动模式" and manager.state_fixed_button.text() == "固定模式")

# --- 2. 便携式配置 + 迁移 + 导入（写入临时目录，不动用户真实配置）
check("便携式配置目录", "local_config" in overlay.directory_config_rts_overlay, overlay.directory_config_rts_overlay)
check("配置目录已创建/迁移", os.path.isdir(overlay.directory_config_rts_overlay))
check("素材目录解析(新布局)", os.path.isdir(overlay.directory_common_pictures), overlay.directory_common_pictures)
check("剪贴板导入封装存在", hasattr(manager, "import_from_clipboard"))

real_bo_dir = overlay.directory_build_orders
temp_bo_dir = Path(tempfile.mkdtemp(prefix="r3_test_bo_"))
overlay.directory_build_orders = str(temp_bo_dir)
existing = sorted(Path(real_bo_dir).rglob("*.json")) if Path(real_bo_dir).is_dir() else []
if existing:
    bo_data = json.loads(existing[0].read_text(encoding="utf-8"))
    bo_data["name"] = "R3测试用建造顺序"
    manager.save_build_order_from_text(json.dumps(bo_data, ensure_ascii=False), "")
    check("导入-文件写入", (temp_bo_dir / "R3测试用建造顺序.json").exists())
    check("导入-重载后可见", any(bo.get("name") == "R3测试用建造顺序" for bo in overlay.build_orders))
    bo_data["name"] = "R3自定义名称流程"
    manager.save_build_order_from_text(json.dumps(bo_data, ensure_ascii=False), "R3自定义名称流程")
    check("导入-名称栏覆盖", (temp_bo_dir / "R3自定义名称流程.json").exists())
else:
    skips.append("导入（真实建造顺序文件夹为空，无法构造有效样本）")
    print("  SKIP 导入（无真实建造顺序样本）")

manager.save_build_order_from_text("这不是JSON", "")
check("导入-非法内容安全拒绝", not any("这不是JSON" in f.name for f in temp_bo_dir.rglob("*.json")))

# --- 3. 搜索与选择（空搜索 = 显示全部）+ 要点提取
if len(overlay.build_orders) > 0:
    first_bo = overlay.build_orders[0]
    for key, combo in manager.filter_combos:
        expected = first_bo.get(key)
        target_index = -1
        for i in range(combo.count()):
            if combo.itemText(i) == expected or (expected is None and combo.itemText(i) in ("Generic", "Any", "all")):
                target_index = i
                break
        if target_index >= 0:
            combo.setCurrentIndex(target_index)
    manager.search_edit.setText("")  # 空搜索 = 直接显示全部
    app.processEvents()
    check("搜索结果列表", len(manager.last_valid_names) > 0, f"names={manager.last_valid_names}")
    if len(manager.last_valid_names) > 0:
        manager.on_result_clicked(manager.results_list.item(0))
        app.processEvents()
        check("选择建造顺序", overlay.selected_build_order is not None)

        # R6 要点提取
        hl = overlay.get_build_order_highlights()
        check("要点提取-结构", "units" in hl and "techs" in hl)
        check("要点提取-排除资源/动物/时代", all(
            ("/resource/" not in x["icon"]) and ("/animal/" not in x["icon"]) and ("/age/" not in x["icon"])
            for x in hl["units"] + hl["techs"]))
        if game_key == "aoe2":  # 分类表本期仅 AoE2 提供，其他游戏要点为空属预期
            check("要点提取-有内容", len(hl["units"]) + len(hl["techs"]) > 0,
                  f"units={len(hl['units'])} techs={len(hl['techs'])}")
else:
    skips.append("搜索与选择（无建造顺序数据）")
    print("  SKIP 搜索与选择")

# --- 4. 悬浮窗开关（经管理器，含要点窗口）+ 隐藏按钮双击 + 位置回归
def open_overlay_via_manager():
    """经管理器开启悬浮窗；若弹出要点窗口则关闭（按设计：关闭后悬浮窗开启）。"""
    manager.toggle_overlay()
    app.processEvents()
    close_highlights_if_any()

open_overlay_via_manager()
check("开启悬浮窗", overlay.overlay_visible())
manager.toggle_overlay()
app.processEvents()
check("关闭悬浮窗", not overlay.overlay_visible())
open_overlay_via_manager()  # 重新打开供后续状态测试

x_before_drag = 120
old_width = overlay.width()
overlay.move(x_before_drag, 140)
for attr in ("upper_left_position", "upper_right_position"):
    pos = [x_before_drag, 140] if attr == "upper_left_position" else [x_before_drag + old_width, 140]
    overlay.settings.layout.__dict__[attr] = pos
    overlay.unscaled_settings.layout.__dict__[attr] = pos
if overlay.selected_build_order is not None:
    overlay.build_order_next_step()  # 触发布局刷新（宽度可能变化）
overlay.update_position()
# 悬浮窗按 overlay_on_right_side 锚定边缘：拖动后应保持拖动时的锚定边（而非 x 不变）
if overlay.settings.layout.overlay_on_right_side:
    check("拖动后位置不回跳(右缘保持)", overlay.x() + overlay.width() == x_before_drag + old_width,
          f"x={overlay.x()} width={overlay.width()}")
else:
    check("拖动后位置不回跳(左缘保持)", overlay.x() == x_before_drag, f"x={overlay.x()}")

overlay.build_order_hide_button.button.click()
overlay.build_order_hide_button.button.click()
app.processEvents()
check("隐藏按钮双击才隐藏", not overlay.overlay_visible())
check("快捷键折叠项", hasattr(manager, "hotkeys_header") and hasattr(manager, "open_hotkeys_window"))
open_overlay_via_manager()

# --- 5. 状态切换（移动 <-> 固定）+ 锁按钮
check("默认移动模式", overlay.selected_panel == PanelID.CONFIG)
check("移动模式-可点击(不穿透)", not overlay.testAttribute(__import__("PyQt5.QtCore", fromlist=["Qt"]).Qt.WA_TransparentForMouseEvents))
manager.set_overlay_state(False)
app.processEvents()
check("切到固定模式", overlay.selected_panel == PanelID.BUILD_ORDER)
check("固定模式-穿透", overlay.testAttribute(__import__("PyQt5.QtCore", fromlist=["Qt"]).Qt.WA_TransparentForMouseEvents))
check("管理器状态按钮同步", manager.state_fixed_button.isChecked())
manager.set_overlay_state(True)
app.processEvents()
check("切回移动模式", overlay.selected_panel == PanelID.CONFIG)
check("移动模式-恢复不穿透", not overlay.testAttribute(__import__("PyQt5.QtCore", fromlist=["Qt"]).Qt.WA_TransparentForMouseEvents))

check("悬浮窗-上一步按钮", overlay.build_order_previous_button is not None)
check("悬浮窗-下一步按钮", overlay.build_order_next_button is not None)
check("悬浮窗-隐藏按钮", overlay.build_order_hide_button is not None)
check("悬浮窗-锁按钮", overlay.build_order_lock_button is not None)
panel_before = overlay.selected_panel
overlay.build_order_lock_button.button.click()
app.processEvents()
check("锁按钮点击切换状态", overlay.selected_panel != panel_before)
check("锁按钮图标有效", not overlay.build_order_lock_button.button.icon().isNull())
overlay.build_order_lock_button.button.click()
app.processEvents()
check("锁按钮再次点击切回", overlay.selected_panel == panel_before)
if overlay.selected_build_order is not None and not overlay.build_order_timer["steps"]:
    check("无时间参数-不显示计时按钮", not overlay.build_order_start_stop_timer.button.isVisible())

# --- 6. 主题切换
manager.set_theme("dark")
check("深色主题样式", "#1e1e1e" in manager.styleSheet())
check("深色主题按钮状态", manager.theme_dark_button.isChecked())
manager.set_theme("light")
check("浅色主题样式", "#f5f5f5" in manager.styleSheet())

# --- 7. reload 联动（外观变更路径）
overlay.unscaled_settings.layout.font_size = 12
overlay.reload(update_settings=False)
app.processEvents()
check("reload 后设置同步", overlay.settings.layout.font_size == 12)

# --- 8. 游戏切换（仅 AoE2 子进程覆盖全游戏注册表）
if game_key == "aoe2":
    manager.switch_game("wc3")
    app.processEvents()
    check("切换游戏-管理器绑定", manager.overlay.name_game == "wc3")
    check("切换游戏-悬浮窗标题", manager.overlay.windowTitle() == "魔兽争霸3悬浮窗")
    check("切换游戏-旧悬浮窗已隐藏", not overlay.overlay_visible())
    manager.switch_game("aoe2")
    app.processEvents()
    check("切回帝国时代2", manager.overlay.windowTitle() == "帝国时代2悬浮窗")
    check("切换后定时器委托可用", callable(manager.timer_build_order_call) and callable(manager.timer_mouse_keyboard_call))

print("SUBPROCESS-RESULT:", "PASS" if not failures else f"FAIL {failures}")
print("SKIPS:", skips)
sys.stdout.flush(); sys.stderr.flush()
os._exit(0 if not failures else 1)
'''


def part1_smoke():
    print("===== 第一部分：双窗冒烟测试（每游戏独立子进程）=====")
    games = [
        ("aoe2", "AoE2GameOverlay", "帝国时代2悬浮窗"),
        ("aoe4", "AoE4GameOverlay", "帝国时代4悬浮窗"),
        ("aom", "AoMGameOverlay", "神话时代悬浮窗"),
        ("sc2", "SC2GameOverlay", "星际争霸2悬浮窗"),
        ("wc3", "WC3GameOverlay", "魔兽争霸3悬浮窗"),
    ]
    for game_key, class_name, expected_title in games:
        print(f"-- {class_name}")
        args = [sys.executable, "-u", "-c", RUNNER, game_key, class_name, expected_title, str(PY_DIR)]
        result = subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, errors="replace")
        for line in result.stdout.splitlines():
            if line.startswith(("  OK", "  FAIL", "  SKIP", "SUBPROCESS-RESULT", "SKIPS")):
                print("   " + line.strip())
        if result.returncode != 0 or "SUBPROCESS-RESULT: PASS" not in result.stdout:
            failures.append(f"{class_name} 子进程失败 (exit={result.returncode})")
            print(f"   FAIL {class_name} 子进程失败 (exit={result.returncode})")
            for line in result.stderr.splitlines()[-10:]:
                if line.strip() and "QFontDatabase" not in line and "propagateSizeHints" not in line:
                    print("      stderr> " + line.strip())


def part2_coverage():
    print("===== 第二部分：UI 字符串覆盖率检查 =====")
    sys.path.insert(0, str(PY_DIR))
    from common.chinese_locale import TRANSLATIONS

    CALL_FUNCS = {"QLabel", "QPushButton", "QCheckBox", "QRadioButton", "QGroupBox", "QMessageBox",
                  "setText", "setWindowTitle", "setToolTip", "setPlaceholderText", "addItem", "addItems",
                  "setTitle", "insertItem", "setItemText", "setStatusTip", "setTabText", "show_message_box",
                  "getOpenFileName", "getSaveFileName", "QAction", "QToolButton"}

    uncovered = {}
    for root, dirs, files in os.walk(PY_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = Path(root) / fn
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    f = node.func
                    name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                    if name in CALL_FUNCS:
                        for a in node.args:
                            if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value:
                                if a.value not in TRANSLATIONS:
                                    uncovered.setdefault(str(path.relative_to(REPO)) + ":" + str(node.lineno), a.value)

    exempt_markers = ("webp", ".png", ".json", ".py", "explorer", "settings", "_overlay", "rts_overlay",
                      "http", "\\", "/", " %", "action_button", "resource/", "civilization", "major_god",
                      "race_icon", "age/", "icon/", "→")  # 路径/文件名/单位/装饰符号等非翻译对象
    real_misses = {loc: s for loc, s in uncovered.items()
                   if not any(m in s for m in exempt_markers)}
    print(f"调用点静态字符串未入字典且疑似界面文本: {len(real_misses)} 条")
    for loc, s in sorted(real_misses.items()):
        print(f"  {loc}: {s!r}")
    if real_misses:
        failures.append(f"覆盖率: {len(real_misses)} 条未覆盖")

    missing_t_keys = []
    for root, dirs, files in os.walk(PY_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = Path(root) / fn
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == "t" and node.args
                        and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                    if node.args[0].value not in TRANSLATIONS:
                        missing_t_keys.append(f"{path.relative_to(REPO)}:{node.lineno}: {node.args[0].value!r}")
    if missing_t_keys:
        failures.append("t() 键缺失: " + "; ".join(missing_t_keys))
    print(f"t() 调用键检查: {'全部在字典中' if not missing_t_keys else missing_t_keys}")


if __name__ == "__main__":
    part1_smoke()
    part2_coverage()
    print()
    if failures:
        print(f"!! 共 {len(failures)} 项失败:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("全部检查通过 PASS")
