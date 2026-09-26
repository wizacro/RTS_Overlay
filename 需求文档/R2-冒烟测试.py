# -*- coding: utf-8 -*-
"""R2 冒烟测试 + 覆盖率检查。

用法：在仓库根目录执行  python 需求文档/R2-冒烟测试.py

第一部分：每个游戏入口在独立子进程中离屏实例化（与真实使用一致：一次一个进程），
         断言关键控件显示中文，并执行面板切换等操作路径。
第二部分：AST 扫描全部 UI 字符串调用点，与翻译字典比对，输出未覆盖清单。

说明：pynput 全局鼠标监听器与界面汉化无关，子进程中以桩替换，避免在无头
环境中启动真实监听线程；子进程结束用 os._exit 跳过 Qt 拆解段错误。
"""
import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY_DIR = REPO / "python"

failures = []

# ---------------------------------------------------------------------------
# 子进程运行器：构建单个游戏窗口并断言中文文本
# ---------------------------------------------------------------------------
RUNNER = r'''
import os, sys
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

from PyQt5.QtWidgets import QApplication
from common.chinese_locale import install
install()
app = QApplication([])
module = __import__(f"{game_key}.{game_key}_game_overlay", fromlist=[class_name])
window = getattr(module, class_name)(app=app, directory_main=str(py_dir))
app.processEvents()

failures = []
def check(label, actual, expected):
    if actual == expected:
        print(f"  OK {label}: {actual!r}")
    else:
        failures.append(f"{label}: 期望 {expected!r} 实际 {actual!r}")
        print(f"  FAIL {label}: 期望 {expected!r} 实际 {actual!r}")

check("窗口标题", window.windowTitle(), expected_title)
check("建造顺序面板标题", window.build_order_title.text(), "建造顺序")
check("搜索框占位符", window.build_order_search.placeholderText(), "关键词或空格")
check("步骤计数初值", window.build_order_step_time.text(), "步骤: 0/0")
try:
    window.update_build_order_step_label()
    if hasattr(window, "next_panel"):
        window.next_panel()
    app.processEvents()
    print("  OK 面板切换调用成功")
except Exception as exc:
    failures.append(f"面板切换异常: {exc}")
    print(f"  FAIL 面板切换异常: {exc}")

# 快捷键窗口（仅 AoE2 检查一次，由外部参数指定）
if len(sys.argv) > 5 and sys.argv[5] == "with_hotkeys_window":
    from common.hotkeys_window import HotkeysWindow
    hw = HotkeysWindow(
        parent=window,
        hotkeys=window.unscaled_settings.hotkeys,
        game_icon=window.game_icon,
        mouse_image=os.path.join(window.directory_common_pictures, window.images.mouse),
        configuration_folder=window.directory_config_game,
        panel_settings=window.settings.panel_hotkeys,
        timer_flag=True,
    )
    app.processEvents()
    check("快捷键窗口标题", hw.windowTitle(), "快捷键配置")
    check("更新按钮", hw.update_button.text(), "更新快捷键")
    check("配置文件夹按钮", hw.folder_button.text(), "打开配置文件夹")
    hw.close()
    window.close()
    app.processEvents()

print("SUBPROCESS-RESULT:", "PASS" if not failures else f"FAIL {failures}")
sys.stdout.flush(); sys.stderr.flush()
os._exit(0 if not failures else 1)
'''


def part1_smoke():
    print("===== 第一部分：离屏冒烟测试（每游戏独立子进程）=====")
    games = [
        ("aoe2", "AoE2GameOverlay", "帝国时代2悬浮窗", True),
        ("aoe4", "AoE4GameOverlay", "帝国时代4悬浮窗", False),
        ("aom", "AoMGameOverlay", "神话时代悬浮窗", False),
        ("sc2", "SC2GameOverlay", "星际争霸2悬浮窗", False),
        ("wc3", "WC3GameOverlay", "魔兽争霸3悬浮窗", False),
    ]
    for game_key, class_name, expected_title, with_hotkeys in games:
        print(f"-- {class_name}")
        args = [sys.executable, "-u", "-c", RUNNER, game_key, class_name, expected_title, str(PY_DIR)]
        if with_hotkeys:
            args.append("with_hotkeys_window")
        result = subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, errors="replace")
        for line in result.stdout.splitlines():
            if line.startswith("  OK") or line.startswith("  FAIL") or line.startswith("SUBPROCESS-RESULT"):
                print("   " + line.strip())
        if result.returncode != 0 or "SUBPROCESS-RESULT: PASS" not in result.stdout:
            failures.append(f"{class_name} 子进程失败 (exit={result.returncode})")
            print(f"   FAIL {class_name} 子进程失败 (exit={result.returncode})")
            for line in result.stderr.splitlines()[-8:]:
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
                      "http", "\\", "/", " %")  # 路径/文件名/单位等非翻译对象
    real_misses = {loc: s for loc, s in uncovered.items()
                   if not any(m in s for m in exempt_markers)}
    print(f"调用点静态字符串未入字典且疑似界面文本: {len(real_misses)} 条")
    for loc, s in sorted(real_misses.items()):
        print(f"  {loc}: {s!r}")
    if real_misses:
        failures.append(f"覆盖率: {len(real_misses)} 条未覆盖")

    # --- 2b: 任意调用中 tooltip/text/title/placeholder 关键字参数（R2 第二轮新增，覆盖 TwinHoverButton 等辅助函数）---
    kw_misses = []
    # --- 2c: 赋值给 *tooltip* / *title* 变量的字符串（含 IfExp 两个分支）---
    var_misses = []
    # --- 2d: return 语句返回的疑似界面文案 ---
    ret_misses = []

    def prose(s):
        return bool(s) and " " in s and sum(c.isascii() and c.isalpha() for c in s) >= 4

    for root, dirs, files in os.walk(PY_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = Path(root) / fn
            rel = str(path.relative_to(REPO))
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    for kw in node.keywords:
                        if (kw.arg in ("tooltip", "text", "title", "placeholder")
                                and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str)
                                and kw.value.value and kw.value.value not in TRANSLATIONS):
                            kw_misses.append(f"{rel}:{node.lineno}: {kw.value.value!r}")
                elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = []
                    if isinstance(node, ast.Assign):
                        targets = node.targets
                    elif node.target is not None:
                        targets = [node.target]
                    names = []
                    for tgt in targets:
                        if isinstance(tgt, ast.Name):
                            names.append(tgt.id.lower())
                        elif isinstance(tgt, ast.Attribute):
                            names.append(tgt.attr.lower())
                    if not any(("tooltip" in n) or n == "title" or n.endswith("_title") for n in names):
                        continue
                    value = node.value
                    constants = []
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        constants.append(value.value)
                    elif isinstance(value, ast.IfExp):
                        for branch in (value.body, value.orelse):
                            if isinstance(branch, ast.Constant) and isinstance(branch.value, str):
                                constants.append(branch.value)
                    for s in constants:
                        if s and s not in TRANSLATIONS:
                            var_misses.append(f"{rel}:{node.lineno}: {s!r}")
                elif isinstance(node, ast.Return):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        s = node.value.value
                        if prose(s) and s not in TRANSLATIONS:
                            ret_misses.append(f"{rel}:{node.lineno}: {s!r}")

    for label, misses in [("tooltip/text/title 关键字参数", kw_misses),
                          ("tooltip/title 变量赋值", var_misses),
                          ("return 界面文案", ret_misses)]:
        print(f"{label} 未入字典: {len(misses)} 条")
        for m in misses:
            print(f"  {m}")
        if misses:
            failures.append(f"覆盖率({label}): {len(misses)} 条未覆盖")

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
