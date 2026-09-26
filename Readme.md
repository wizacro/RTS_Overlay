简介
============

> 🌐 本文档为中文译版（基于原项目 v2.15.0），英文原文参见 [CraftySalamander/RTS_Overlay](https://github.com/CraftySalamander/RTS_Overlay)。

**RTS Overlay** 是一款用于设计或导入即时战略（RTS）游戏建造顺序（build order）的工具。
建造顺序可以直接显示在游戏画面之上，因此单显示器即可使用。

在游戏中更新建造顺序步骤通过按钮/快捷键/计时器手动完成。
RTS Overlay 不会与游戏本身交互（不分析屏幕画面，也不进行任何操控）。

点击[这里](#主要说明与下载)阅读主要说明，开始使用悬浮窗。

![RTS Overlay](/docs/assets/common/icon/salamander_sword_shield_small.webp)


目录
=================

* [主要说明与下载](#主要说明与下载)
* [通过网页浏览器或 EXE 使用悬浮窗](#通过网页浏览器或-exe-使用悬浮窗)
* [支持的游戏](#支持的游戏)
* [网页版方案](#网页版方案)
    * [窗口置顶](#窗口置顶)
* [EXE/Python 版方案](#exepython-版方案)
    * [EXE 版](#exe-版)
    * [Python 配置](#python-配置)
    * [配置面板](#配置面板)
    * [建造顺序选择](#建造顺序选择)
* [网页版与 EXE/Python 版的通用说明](#网页版与-exepython-版的通用说明)
    * [设计建造顺序](#设计建造顺序)
    * [使用建造顺序面板](#使用建造顺序面板)
* [游戏专属说明](#游戏专属说明)
    * [帝国时代2（AoE2）](#帝国时代2aoe2)
    * [帝国时代4（AoE4）](#帝国时代4aoe4)
    * [神话时代（AoM）](#神话时代aom)
    * [星际争霸2（SC2）](#星际争霸2sc2)
    * [魔兽争霸3（WC3）](#魔兽争霸3wc3)
* [故障排查](#故障排查)
    * [网页版](#网页版)
    * [EXE/Python 版](#exepython-版)
* [补充说明](#补充说明)


# 主要说明与下载

如[下一节](#通过网页浏览器或-exe-使用悬浮窗)所述，使用悬浮窗有两种方式：
* 通过网页浏览器
    * [YouTube 演示](https://youtu.be/dst2b8b4_fo)
    * 访问 [rts-overlay.github.io](https://rts-overlay.github.io/) 并按照页面说明操作。
* 使用 EXE 版（或直接从 Python 源代码运行）
    * [YouTube 演示](https://youtu.be/qFBkpTnRzWQ)
    * 通过以下链接下载 EXE（仅支持 Windows，链接指向原项目发布页）：
        * [帝国时代2](https://github.com/CraftySalamander/RTS_Overlay/releases/download/2.15.0/aoe2_overlay.zip)
        * [帝国时代4](https://github.com/CraftySalamander/RTS_Overlay/releases/download/2.14.0/aoe4_overlay.zip)
        * [神话时代](https://github.com/CraftySalamander/RTS_Overlay/releases/download/2.12.0/aom_overlay.zip)
        * [星际争霸2](https://github.com/CraftySalamander/RTS_Overlay/releases/download/2.12.0/sc2_overlay.zip)
        * [魔兽争霸3](https://github.com/CraftySalamander/RTS_Overlay/releases/download/2.12.0/wc3_overlay.zip)
    * 也可以从 Python 源代码运行，具体步骤见 [Python 配置](#python-配置)一节。


# 通过网页浏览器或 EXE 使用悬浮窗

RTS Overlay 既可以通过[网页浏览器](https://rts-overlay.github.io/)使用，也可以作为 EXE/Python 版使用（EXE 版可通过[这里](#主要说明与下载)下载预编译文件，或直接从 Python 源代码运行）。

网页版更易于上手，是初次体验 *RTS Overlay* 的良好起点。
EXE/Python 版（源代码运行或预编译）额外提供以下功能：
1. *更少的干扰*：无标题栏、半透明（可调透明度），且不阻挡鼠标点击。
2. *全局快捷键*：两个版本都支持快捷键，但网页版只有在悬浮窗获得焦点时才响应快捷键；EXE/Python 版即使焦点在游戏上也能响应快捷键。

运行方式：
* **网页版**：访问 [rts-overlay.github.io](https://rts-overlay.github.io/) 并按照页面说明操作。
    * 有两种模式："画中画"（Picture-in-Picture，通常会将悬浮窗自动置于游戏之上）和"经典窗口"。若使用"经典窗口"模式并希望悬浮窗保持在游戏之上，请借助*窗口置顶*类工具。Windows 平台上推荐 [PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/)——免费、由微软开发，可从 [Microsoft Store](https://apps.microsoft.com/) 获取。
    * 你也可以下载本地版以提升速度、离线使用并自定义体验：[点击此处](https://github.com/CraftySalamander/RTS_Overlay/archive/refs/heads/master.zip)下载压缩包，解压后用任意网页浏览器打开 *docs/index.html*。也可以点击浏览器地址栏中的安装按钮（Chrome 和 Edge）将其安装到本地。
    * 开发版（非稳定版）见[这里](https://craftysalamander.github.io/RTS_Overlay/)。
* **EXE/Python 版**：从[这里](#主要说明与下载)下载 EXE，或按照[这里](#python-配置)的 Python 说明操作。
    * EXE 是预编译版本（由 Python 源代码编译得到），打包为 zip 压缩包。无需安装 Python 环境，解压后点击对应游戏的 EXE 即可（位于 *overlay* 子文件夹中）。注意：某些杀毒软件不信任从网上下载的 zip 包里的 EXE 文件（如果你选择这种方式，可能需要为其添加例外规则）。


# 支持的游戏

目前支持以下游戏：

* [帝国时代2 决定版（Age of Empires II Definitive Edition）](https://www.ageofempires.com/games/aoeiide/)
    * 从 [buildorderguide.com](https://www.buildorderguide.com)（点击 *Export for RTS*）或 [RTS Builds](https://craftysalamander.github.io/rtsbuilds/?gameId=aoe2)（点击 *Open in RTS Overlay*）下载任意建造顺序。
    * YouTube 演示见[这里](https://youtu.be/tONaR2oOt3I)（网页版）或[这里](https://youtu.be/qFBkpTnRzWQ)（EXE/Python 版）。

[![帝国时代2建造顺序实际效果](/readme/aoe2_build_order_demo.webp)](https://youtu.be/tONaR2oOt3I)

* [帝国时代4（Age of Empires IV）](https://www.ageofempires.com/games/age-of-empires-iv/)
    * 从 [aoe4guides.com](https://aoe4guides.com) 或 [RTS Builds](https://craftysalamander.github.io/rtsbuilds/?gameId=aoe4)（点击 *Open in RTS Overlay*）下载任意建造顺序（[age4builder.com](https://age4builder.com) 也曾提供 RTS Overlay 格式的建造顺序，但该项目似乎已下线）。
    * YouTube 演示见[这里](https://youtu.be/RmsofE58YEg)。

[![帝国时代4建造顺序实际效果](/readme/aoe4_build_order_demo.webp)](https://youtu.be/RmsofE58YEg)

* [神话时代（Age of Mythology）](https://www.ageofempires.com/games/aom/age-of-mythology-retold/)
    * 从 [RTS Builds](https://craftysalamander.github.io/rtsbuilds/?gameId=aom)（点击 *Open in RTS Overlay*）下载任意建造顺序（[thedodclan.com](https://thedodclan.com/) 曾提供导出至 RTS Overlay 的功能，但网站改版后已移除该功能）。
    * YouTube 演示见[这里](https://youtu.be/f11ISkuVhnU)。

[![神话时代建造顺序实际效果](/readme/aom_build_order_demo.webp)](https://youtu.be/f11ISkuVhnU)

* [星际争霸2（StarCraft II）](https://starcraft2.com)

![星际争霸2建造顺序实际效果](/readme/sc2_build_order_demo.webp)

* [魔兽争霸3（Warcraft III）](https://warcraft3.blizzard.com/)


# 网页版方案

[网页版](https://rts-overlay.github.io/)的主页面如下图所示。
完整使用说明可将鼠标悬停在页面右上角的 "i" 图标上查看。

![网页版 RTS Overlay](/readme/rts_overlay_web.webp)

## 窗口置顶

建造顺序就绪后，点击 *Display overlay*（显示悬浮窗）按钮，会生成一个新的（小）窗口并显示所选建造顺序。

在"经典窗口"模式下，请务必借助*窗口置顶*类工具将其保持在游戏之上（"画中画"模式无需此操作）。

[Microsoft PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/) 是一个不错的选择。它免费、由微软开发，可在 *Microsoft Store* 获取。
从 *Microsoft Store* 下载后，为*窗口置顶*（Always On Top）功能配置快捷键（也可以配置边框颜色），然后对 *RTS Overlay* 窗口使用该功能。

# EXE/Python 版方案

从下面两种方式中选择其一（*EXE 版*或 *Python 配置*）。如上文所述，相比网页版它们有两大额外优势：*更少的干扰*和*全局快捷键*。

## EXE 版

这种方式更简单，运行的是编译版本（效率也更高）。
Python 代码连同全部依赖库一起编译并打包为 zip 压缩包。
注意：某些杀毒软件不信任从网上下载的、含有可执行文件和依赖库的 zip 包，可能会报误报警告。
具体步骤如下：

1. 从[这里](#主要说明与下载)下载对应游戏的 zip 压缩包。在某些电脑上，解压前可能需要先"解除锁定"（右键点击压缩包 → 选择属性 → 勾选"解除锁定"）。
2. 将其解压到电脑上的任意位置（最好放在不需要特殊系统权限的目录）。
3. 启动程序：直接运行对应游戏的可执行文件即可（这些可执行文件都位于 *overlay* 子文件夹中，各游戏的具体细节见对应章节）。

要更新到新版本，只需删除旧文件夹并换上新版本文件夹。
注意：你的配置和建造顺序保存在用户数据目录（例如 *C:\Users\XXXXX\AppData\Local\RTS_Overlay*）中，因此更新版本不会丢失原有配置和建造顺序。
如果你想使用本地配置文件夹，请在 *overlay* 子文件夹中创建名为 *"local_config"* 的文件夹，配置（和建造顺序）将保存在那里。

如果遇到问题，请参阅[故障排查](#故障排查)一节。

## Python 配置

你可以使用 Python 从源代码运行本程序。即使没有任何编程基础，做起来也不难。
具体步骤如下：

1. 如果你还没有 Python 环境，可以通过 [Anaconda 安装包](https://www.anaconda.com/download)下载并安装带 conda 包管理器的 Python 发行版（其他发行版也可以，如 [Miniforge](https://github.com/conda-forge/miniforge#miniforge3)）。
可选：将程序（如 Anaconda3）加入 PATH 环境变量（以便在任意终端中运行）。
2. 下载 RTS Overlay 的代码：点击[此页面](https://github.com/CraftySalamander/RTS_Overlay)顶部的 *Code* 按钮，再点击 *Download ZIP* 并解压压缩包（或使用 [Git](https://git-scm.com/) 克隆仓库）。
3. 打开 *Anaconda Prompt*。如果你已将 Python 路径加入 PATH 环境变量，也可以打开任意终端（如 Windows 上的 *Command Prompt*）。
4. 进入解压后文件夹中的 python 目录（例如 `cd RTS_Overlay-master/python`）。
5. 创建 Conda 环境：`conda create --name rts_overlay python=3.8`
6. 激活环境：`conda activate rts_overlay`
7. 安装依赖库：`pip install -r utilities/requirements.txt`
8. （可选）运行 `pip install python-Levenshtein==0.12.2`（可略微提升性能）。
9. 运行程序：`python main_aoe2.py`（以 AoE2 为例，其他游戏类似）。

每次运行程序前，需要重新执行第 3、4、6、9 步。

如果想把程序打包为 *exe* 程序：在 `cd utilities` 之后运行 `python prepare_release.py`，会生成独立的库并为发布准备附加文件（需要先 `pip install nuitka==1.0.6` 和 `pip install orderedset==2.0.3`）。


## 配置面板

启动 EXE/Python 版 *RTS Overlay* 后，首先看到的是*配置面板*。
它用于配置界面布局和建造顺序。

![配置面板](/readme/aoe2_panel_configuration.webp)

第一行从左到右依次是以下操作按钮：

* [退出程序](docs/assets/common/action_button/leave.webp)：退出本工具。
* [保存设置](docs/assets/common/action_button/save.webp)：将配置保存到设置文件（如 *aoe2_settings.py*）。
* [加载设置](docs/assets/common/action_button/load.webp)：加载上述设置文件（程序启动时会自动加载该文件）。
* [配置](docs/assets/common/action_button/gears.webp)：配置快捷键（支持键盘和/或鼠标输入），并打开保存相应配置文件的文件夹。该文件夹同时存放设置和建造顺序。要添加建造顺序，先获取其 JSON 文件（来自 [craftysalamander.github.io/rtsbuilds](https://craftysalamander.github.io/rtsbuilds)、第三方网站，或在 [rts-overlay.github.io](https://rts-overlay.github.io) 上自行设计），然后放入该配置文件夹下的 `build_orders` 子文件夹。以 AoE2 为例，该子文件夹通常是 *C:\Users\XXXXX\AppData\Local\RTS_Overlay\aoe2\build_orders*。
* [添加/编辑建造顺序](docs/assets/common/action_button/feather.webp)：通过粘贴建造顺序文本来添加/移除建造顺序，或打开建造顺序文件夹手动删除。
* 选择文本字体大小。
* 选择界面布局的缩放比例（图片、间距等）。
    * 例如使用 4K 显示器时，可将此值设为 *200 %*。
* [下一面板](docs/assets/common/action_button/to_end.webp)：切换到下一个面板（在*配置*和*建造顺序*之间循环）。

以下快捷键是"全局"的，即即使焦点不在悬浮窗上（比如正在玩游戏时）也能使用：
* *next_panel*：切换到下一个面板
* *show_hide*：显示/隐藏程序
* *build_order_previous_step*：建造顺序上一步，或将计时器减 1 秒（见下文）
* *build_order_next_step*：建造顺序下一步，或将计时器加 1 秒（见下文）
* *switch_timer_manual*：在手动切换和计时器模式之间切换（见下文）
* *start_timer*：启动计时器
* *stop_timer*：停止计时器
* *start_stop_timer*：启动或停止计时器
* *reset_timer*：将计时器重置为 *0:00*

可以用鼠标左键拖放移动窗口。由于窗口大小会随内容变化，真正重要的是窗口右上角的位置。该右上角位置会被保持（并通过[保存设置](docs/assets/common/action_button/save.webp)按钮存入设置文件）。

悬浮窗应始终保持在其他程序（包括游戏）之上。有时启动时可能不生效，点击一次[下一面板](docs/assets/common/action_button/to_end.webp)按钮通常即可解决。

设置文件中还有更多选项（字体、图片尺寸等）。点击[配置](docs/assets/common/action_button/gears.webp)，再点击 `Open settings folder` 即可找到。可以用任意文本编辑器编辑该文件（JSON 格式）并重新加载（通过[加载设置](docs/assets/common/action_button/load.webp)按钮，或退出并重启程序）。

## 建造顺序选择

在配置面板中可以找到 **Build Order**（建造顺序）搜索栏。要选择要显示的建造顺序，先输入几个关键词，最多会列出 10 条匹配的建造顺序。这里使用的是模糊搜索。你也可以在上述设置文件（JSON 格式）中通过 `bo_list_fuzz_search` 开关关闭（或调整）模糊搜索：设为 False 时，以空格分隔的所有关键词都必须出现在所选建造顺序的名称中。另外，如果只输入一个空格字符，会显示前 10 条建造顺序。悬浮窗还提供筛选功能，可选择你的阵营或通用建造顺序（以及可能的对手阵营）。

按 *Enter* 选中以粗体显示的建造顺序。默认选中的是列表第一条，也可以用 *Tab* 选择其他条目，或者直接用鼠标点击想要的建造顺序。


# 网页版与 EXE/Python 版的通用说明

## 设计建造顺序

如果条件允许，设计建造顺序最简单的方法是通过专门的网站，直接输出正确格式的建造顺序（例如 AoE2 的 [buildorderguide.com](https://www.buildorderguide.com)）。这些网站上可以找到大量现成的建造顺序。

你也可以在建造顺序设计面板中手动编写：在[网页版](https://rts-overlay.github.io/)中点击 **Design your own**（见[这里](https://youtu.be/dst2b8b4_fo)的演示）；EXE/Python 版则使用[添加/编辑建造顺序按钮](docs/assets/common/action_button/feather.webp)。
两个版本生成的建造顺序完全相同（网页版与 EXE/Python 版）。

![建造顺序设计](/readme/rts_overlay_aoe2_editor.gif)

## 使用建造顺序面板

在 EXE/Python 版中，除第一行的按钮外，你无法点击悬浮窗本身（这样可以继续点击它后面的游戏画面）。网页版没有这一特性（即对鼠标交互不透明）。

可以使用两个[箭头按钮](docs/assets/common/action_button/previous.webp)选择建造顺序的步骤，当前步骤序号显示在按钮旁边。也可以使用前述快捷键切换步骤，即使焦点不在悬浮窗上也有效。

如果计时器功能可用且与当前建造顺序兼容，会出现[羽毛笔/沙漏按钮](docs/assets/common/action_button/manual_timer_switch.webp)。点击后，建造顺序将按照时间说明自动更新。开始/停止计时可点击[对应按钮](docs/assets/common/action_button/start_stop.webp)。此时[箭头按钮](docs/assets/common/action_button/previous.webp)变为将计时器增减 1 秒，[重置按钮](docs/assets/common/action_button/timer_0.webp)将计时器归零为 *0:00*。计时运行时，当前指令会高亮显示，同时也会显示上一条和下一条指令。以上所有操作都有对应的快捷键。

建造顺序通常标明每种资源应分配多少村民、村民/人口总数以及一些注意事项。
如适用，还会标明需要达到的时代、时间和/或建造者数量。

![建造顺序面板](/readme/aoe2_panel_build_order.webp)


# 游戏专属说明

## 帝国时代2（AoE2）

运行方式：选择帝国时代2（网页版），或启动 *aoe2_overlay.exe*（从[这里](#主要说明与下载)下载，或从 [Python 源代码](#python-配置)运行）。


## 帝国时代4（AoE4）

运行方式：选择帝国时代4（网页版），或启动 *aoe4_overlay.exe*（从[这里](#主要说明与下载)下载，或从 [Python 源代码](#python-配置)运行）。


## 神话时代（AoM）

运行方式：选择神话时代（网页版），或启动 *aom_overlay.exe*（从[这里](#主要说明与下载)下载，或从 [Python 源代码](#python-配置)运行）。


## 星际争霸2（SC2）

运行方式：选择星际争霸2（网页版），或启动 *sc2_overlay.exe*（从[这里](#主要说明与下载)下载，或从 [Python 源代码](#python-配置)运行）。


## 魔兽争霸3（WC3）

运行方式：选择魔兽争霸3（网页版），或启动 *wc3_overlay.exe*（从[这里](#主要说明与下载)下载，或从 [Python 源代码](#python-配置)运行）。


# 故障排查

遇到问题时，先尝试下面的建议。如果都无法解决，可以在 GitHub 上提交 issue（https://github.com/CraftySalamander/RTS_Overlay/issues）描述你的问题（细节越丰富越好）。
使用 EXE/Python 版时，请务必注明版本号（位于文件夹根目录的 *version.json* 中）。

## 网页版

如果网页版出现问题，可以换一个网页浏览器（Chrome、Edge 等）试试，看问题是否依旧。就本悬浮窗而言，Edge 和 Chrome 通常比 Firefox 等其他浏览器表现更好。

## EXE/Python 版

在某些电脑上，你可能需要允许访问该可执行文件或整个文件夹。特别是当看到 "cannot proceed because python38.dll was not found" 时，必须在解压前先解除 zip 包的锁定（右键点击压缩包 → 选择属性 → 勾选"解除锁定"）。

同样，Windows（或杀毒软件）可能将 *.exe* 文件识别为威胁并删除，此时你可能需要添加 Defender 例外规则。

如果程序已启动（任务栏能看到图标）但窗口不可见，可能是悬浮窗出现在了屏幕之外（例如曾使用多显示器、后来拔掉了一台）。检查设置文件是否正常（文件通常位于 *C:\Users\xxx\AppData\Local\RTS_Overlay\xxx\settings\xxx_settings.json*）。例如，悬浮窗上角位置保存在设置项 `layout > upper_right_position`（`overlay_on_right_side` 为 `True` 时）和 `layout > upper_left_position`（`overlay_on_right_side` 为 `False` 时）中。

在 Linux 上，如果悬浮窗无法保持在其他程序之上，可用 `Alt+Space` 呼出 Gnome 中非 GTK 程序的标题栏菜单，然后选择 "Always on top"（置顶）。
已在 Linux 的 X11 环境下测试通过。

如果以上方法都不奏效，可以尝试直接从源代码运行程序（使用 Python）。
具体见 [Python 配置](#python-配置)一节（即使没有 Python 基础也不难）。


# 补充说明
**RTS Overlay** 与上述游戏的开发商/发行商没有任何关联。

对于暴雪-微软系游戏，**RTS Overlay** 是依据微软"[Game Content Usage Rules](https://www.xbox.com/en-us/developers/rules)"（游戏内容使用规则）使用相应游戏素材创建的，未获得微软的认可，也与微软无从属关系。
