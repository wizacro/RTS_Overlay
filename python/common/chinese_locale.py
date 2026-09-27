# -*- coding: utf-8 -*-
"""中文界面层：在运行时把 Qt 界面文字从英文映射为简体中文。

设计原则（安全降级）：
- 仅当字符串与本模块字典中的键【精确匹配】时才替换为中文；
- 未命中的字符串一律原样通过——任何遗漏都只是显示英文，不影响任何功能；
- install() 必须在创建任何窗口之前调用（幂等，重复调用无副作用）；
- t() 可独立使用，用于动态拼接消息的静态部分。
"""

# ---------------------------------------------------------------------------
# 翻译字典：界面英文 -> 简体中文
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    # --- 主窗口（rts_overlay.py）---
    'Build order': '建造顺序',
    'keywords or space': '关键词或空格',  # (legacy, kept for old settings compatibility)
    'Filter build orders by keywords...': '输入关键词筛选建造顺序…',
    'Step: 0/0': '步骤: 0/0',
    'font size': '字体大小',
    'scaling of pictures, spacing...': '图片、间距等缩放',
    'build order keywords, separated by spaces': '建造顺序关键词，用空格分隔',
    'Paste Build Order Text': '粘贴建造顺序文本',
    'Paste your build order text (RTS Overlay format) here.\n\n'
    'Check rts-overlay.github.io (link below) to design your build order\n'
    'or to get links to third-party websites providing build orders in RTS Overlay format.':
        '在此粘贴你的建造顺序文本（RTS Overlay 格式）。\n\n'
        '访问 rts-overlay.github.io（见下方链接）可自行设计建造顺序，\n'
        '或获取提供 RTS Overlay 格式建造顺序的第三方网站链接。',
    'Open rts-overlay.github.io': '打开 rts-overlay.github.io',
    'Save Build Order': '保存建造顺序',
    'Open Build Order Folder': '打开建造顺序文件夹',
    'Open Settings Folder': '打开设置文件夹',
    'Error': '错误',
    'Success': '成功',
    'No text was pasted.': '未粘贴任何文本。',
    'Build order is missing a name.': '建造顺序缺少名称。',
    'Could not parse the build order. Invalid JSON format.': '无法解析建造顺序：JSON 格式无效。',

    # --- 动态消息的静态部分（t() 调用）---
    'Step': '步骤',
    'Invalid build order format': '建造顺序格式无效',
    'Build order name already exists': '已存在同名建造顺序',
    'Build order saved as': '建造顺序已保存为',
    'Failed to save build order': '保存建造顺序失败',

    # --- 快捷键配置窗口（hotkeys_window.py）---
    'Configuration': '快捷键配置',
    'Open configuration folder': '打开配置文件夹',
    'Click to edit, then input hotkey combination.': '点击编辑框后输入快捷键组合。',
    'Update hotkeys': '更新快捷键',
    'Set hotkey sequence or \'Esc\' to cancel. Click on \'Update hotkeys\' to confirm your choice.'
    '\n\nClick on the mouse checkbox to consider \'L\' as left click, \'R\' as right click, '
    '\'M\' as middle button,\n\'1\' as first extra button and \'2\' as second extra button.'
    '\nSo, the input \'Ctrl+1\' with mouse option means Ctrl + first extra button.'
    '\n\nNote that hotkeys are ignored while this window is open.':
        '设置快捷键组合，或按 \'Esc\' 取消。选择后点击\'更新快捷键\'确认。\n\n'
        '勾选鼠标复选框时：\'L\' 代表鼠标左键，\'R\' 代表右键，\'M\' 代表中键，\n'
        '\'1\' 代表第一个侧键，\'2\' 代表第二个侧键。\n'
        '例如鼠标选项下输入 \'Ctrl+1\' 表示 Ctrl + 第一个侧键。\n\n'
        '注意：本窗口打开期间快捷键暂时失效。',
    'Move to next panel :': '切换到下一个面板：',
    'Show/hide overlay :': '显示/隐藏悬浮窗：',
    'Previous step / Timer -1 sec :': '上一步 / 计时器 -1 秒：',
    'Next step / Timer +1 sec :': '下一步 / 计时器 +1 秒：',
    'Switch BO timer/manual :': '切换建造顺序计时/手动模式：',
    'Start BO timer :': '启动建造顺序计时：',
    'Stop BO timer :': '停止建造顺序计时：',
    'Start/stop BO timer :': '启动/停止建造顺序计时：',
    'Reset BO timer :': '重置建造顺序计时：',
    'Go to previous BO step :': '建造顺序上一步：',
    'Go to next BO step :': '建造顺序下一步：',

    # --- 窗口标题（*_settings.py）---
    'AoEII Overlay': '帝国时代2悬浮窗',
    'AoEIV Overlay': '帝国时代4悬浮窗',
    'AoM Overlay': '神话时代悬浮窗',
    'SC2 Overlay': '星际争霸2悬浮窗',
    'WC3 Overlay': '魔兽争霸3悬浮窗',

    # --- 各游戏入口（*_game_overlay.py）---
    'select your civilization (or use Generic)': '选择你的文明（或使用通用）',
    'select civilization': '选择文明',
    'select major god': '选择主神',
    'select race': '选择种族',

    # --- 动作按钮 tooltip（经 TwinHoverButton 的 tooltip 参数/变量传入，钩子在 setToolTip 出口翻译）---
    'next panel': '下一面板',
    'hide panel': '隐藏面板',
    'quit application': '退出程序',
    'save settings': '保存设置',
    'reload settings': '重载设置',
    'configure hotkeys': '配置快捷键',
    'add/edit build orders in BO folder': '添加/编辑建造顺序（BO 文件夹）',
    'previous build order step / -1 sec': '建造顺序上一步 / 计时器 -1 秒',
    'previous build order step': '建造顺序上一步',
    'next build order step / +1 sec': '建造顺序下一步 / 计时器 +1 秒',
    'next build order step': '建造顺序下一步',
    'switch BO mode between timer and manual': '在计时器和手动模式之间切换建造顺序',
    'start/stop the BO timer': '启动/停止建造顺序计时',
    'reset the BO timer': '重置建造顺序计时',

    # --- 无建造顺序提示（get_no_build_order_text 返回值，经 setText 出口翻译）---
    'No valid build order in the build order folder.': '建造顺序文件夹中没有有效的建造顺序。',
    'No valid build order for this faction.': '当前阵营没有有效的建造顺序。',
    'Select build order with search bar.': '使用搜索栏选择建造顺序。',
    'No valid build order found with these keywords.': '未找到符合这些关键词的建造顺序。',

    # --- R3 管理器窗口（manager_window.py）---
    'RTS Overlay Manager': 'RTS Overlay 管理器',
    '1. Import build orders': '① 导入建造顺序',
    '2. Select and configure': '② 选择与配置',
    '3. Show the overlay': '③ 开启悬浮窗',
    'Help': '帮助',
    'Import': '导入',
    'Display': '展示',
    'UI theme': '界面主题',
    'Light': '浅色',
    'Dark': '深色',
    'Quit': '退出',
    'Usage steps: (click any step to jump to the corresponding part)': '使用步骤：（每一步可以单击来转到对应部分）',
    '4. Fix the overlay (in-game state)': '④ 固定悬浮窗',
    'Game': '游戏',
    'Find build orders': '查找流程',
    'Existing build orders': '现有流程数量',
    'Open build order website': '打开流程网站',
    'Build order name (leave empty to use the clipboard build order name):':
        '流程名称（留空则使用剪贴板里流程的名称）：',
    'The build order is read from the clipboard; if the name field is empty, the name inside the build order is used.':
        '流程内容从剪贴板读取；名称栏留空时，使用流程文件内部的名称。',
    'Import from clipboard': '从剪贴板导入',
    'Open build order folder': '打开建造顺序文件夹',
    'Valid clipboard/pasted content is imported directly; otherwise a message is displayed.':
        '剪贴板/粘贴内容格式正确则直接导入保存；否则弹窗提示，不影响现有文件。',
    'Faction': '阵营',
    'Search': '搜索',
    'Select a build order': '选中一个流程',
    'Rename': '重命名',
    'New name:': '新名称：',
    'Delete (to deprecation folder)': '删除（移入弃用区）',
    'Delete': '删除',
    'Build order file not found.': '未找到流程文件。',
    'The build order file will be moved to the "弃用区" folder (not deleted). Continue?':
        '将把该流程文件移动到"弃用区"文件夹（不会真正删除），确定继续吗？',
    'Overlay': '悬浮窗',
    'State': '状态',
    'Show overlay': '开启悬浮窗',
    'Hide overlay': '关闭悬浮窗',
    'Move mode': '移动模式',
    'Fixed mode': '固定模式',
    'Fixed mode: no drag, buttons clickable, other areas click-through':
        '固定模式：不可拖动，按钮可点击，其余区域穿透',
    'Appearance': '外观',
    'Background color': '背景色',
    'Opacity': '不透明度',
    'Font size': '字号',
    'Scaling': '缩放',
    'Display rows': '显示行数',
    'Display control': '展示控制',
    'Hotkeys': '快捷键',
    'Open hotkeys configuration': '打开快捷键配置窗口',
    'Global hotkeys work even while playing (no need to focus the overlay)':
        '全局快捷键在游戏中也能使用（无需悬浮窗获得焦点）',
    'Start/Stop timer': '开始/停止计时',
    'Previous step': '上一步',
    'Next step': '下一步',
    'Reset timer': '归零',
    'No build order selected.': '未选择建造顺序。',
    'Click twice to hide': '连点两次隐藏悬浮窗',
    'Click again to hide': '再点一次确认隐藏',
    'Click to switch between move and fixed modes': '点击切换 移动模式/固定模式',
    'Build order highlights': '流程要点',
    'Main units (in build order appearance order)': '主要兵种（按流程出现顺序）',
    'Main technologies (in build order appearance order)': '主要科技（按流程出现顺序）',
    'Start game, close': '开始游戏，关闭',
    'Civilization': '文明',
    'Source': '来源',
    'No highlights found for this build order.': '未在该流程中识别到重点兵种或科技。',
    'HIGHLIGHTS_TIP': '建议进游戏前把流程说明浏览一遍，记住本页的重点科技与兵种；游戏内用悬浮窗按钮或全局快捷键逐步推进。',
    'HOW_TO_USE_TEXT':
        '使用说明：\n\n'
        '1. 导入建造顺序（"导入"标签页：从剪贴板导入，可先填流程名称）。\n'
        '2. 在"展示"标签页选择建造顺序、调整悬浮窗外观（外观与展示控制默认折叠）。\n'
        '3. 点"开启悬浮窗"，进入移动模式：整窗可拖动，可先点按钮测试流程。\n'
        '4. 进游戏前把状态切到"固定模式"：不可拖动、按钮可点、其余区域点击穿透。\n'
        '   游戏内也可以直接用全局快捷键推进步骤（见快捷键配置窗口）。\n\n'
        '提示：流程列表右键可重命名或删除（删除=移入"弃用区"文件夹，不会真正删除）；\n'
        '关闭管理器窗口即退出整个程序；最小化管理器不影响悬浮窗。',

    # --- R3 悬浮窗（rts_overlay.py，'Step' 等动态键沿用上方既有条目）---
}


def t(text):
    """翻译界面字符串：字典精确命中返回中文，否则原样返回。"""
    if isinstance(text, str):
        return TRANSLATIONS.get(text, text)
    return text


_installed = False


def install():
    """对 Qt 的界面文字出口安装映射钩子。必须在创建任何窗口之前调用。"""
    global _installed
    if _installed:
        return
    from PyQt5 import QtWidgets, QtGui

    def wrap(original):
        """把方法的 str 参数逐个过一遍 t()。"""
        def wrapper(self, *args, **kwargs):
            args = tuple(t(a) for a in args)
            kwargs = {key: t(value) for key, value in kwargs.items()}
            return original(self, *args, **kwargs)
        return wrapper

    # --- 文本设置方法（含继承覆盖面）---
    outlets = [
        (QtWidgets.QLabel, 'setText'),
        (QtWidgets.QAbstractButton, 'setText'),   # 覆盖 QPushButton/QCheckBox/QRadioButton/QToolButton
        (QtWidgets.QLineEdit, 'setText'),
        (QtWidgets.QLineEdit, 'setPlaceholderText'),
        (QtWidgets.QTextEdit, 'setText'),
        (QtWidgets.QTextEdit, 'setPlaceholderText'),
        (QtWidgets.QMessageBox, 'setText'),
        (QtWidgets.QGroupBox, 'setTitle'),
        (QtWidgets.QComboBox, 'addItem'),         # (str) 或 (QIcon, str) 两种重载均覆盖
        (QtWidgets.QComboBox, 'setItemText'),
        (QtWidgets.QTabWidget, 'setTabText'),
        (QtWidgets.QWidget, 'setWindowTitle'),
        (QtWidgets.QWidget, 'setToolTip'),
        (QtWidgets.QWidget, 'setStatusTip'),
        (QtWidgets.QWidget, 'setWhatsThis'),
        (QtWidgets.QAction, 'setText'),
        (QtWidgets.QAction, 'setToolTip'),
    ]
    for klass, method in outlets:
        setattr(klass, method, wrap(getattr(klass, method)))

    # --- QComboBox.addItems：参数是字符串列表 ---
    original_add_items = QtWidgets.QComboBox.addItems

    def add_items_wrapper(self, items, *args, **kwargs):
        if isinstance(items, (list, tuple)):
            items = [t(i) for i in items]
        return original_add_items(self, items, *args, **kwargs)

    QtWidgets.QComboBox.addItems = add_items_wrapper

    # --- 构造函数中的文本参数（QLabel 第一参数也可能是 QPixmap/parent，t() 会原样放行非 str）---
    for klass in [
        QtWidgets.QLabel,
        QtWidgets.QPushButton,
        QtWidgets.QCheckBox,
        QtWidgets.QRadioButton,
        QtWidgets.QToolButton,
        QtWidgets.QGroupBox,
    ]:
        klass.__init__ = wrap(klass.__init__)

    _installed = True
