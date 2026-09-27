# RTS Overlay 中文版（管理器 + 悬浮窗）

> 🌐 本项目是 [CraftySalamander/RTS_Overlay](https://github.com/CraftySalamander/RTS_Overlay) 的中文修改版（基于原项目 v2.15.0，遵循 GPL-3.0 开源协议）。
> 在原版基础上重新设计了**管理器 + 悬浮窗**双窗口界面，并完成了全部界面文案的简体中文汉化。

**RTS Overlay** 是一款用于设计或导入即时战略（RTS）游戏建造顺序（build order）的工具。
建造顺序可以直接显示在游戏画面之上，因此单显示器即可使用。

在游戏中更新建造顺序步骤通过悬浮窗按钮或全局快捷键手动完成。
RTS Overlay 不会与游戏本身交互（不分析屏幕画面，也不进行任何操控）。

使用步骤：（每一步可以单击来转到对应部分）
[① 导入建造顺序](#①-导入建造顺序) → [② 选择与配置](#②-选择与配置) → [③ 开启悬浮窗](#③-开启悬浮窗) → [④ 固定模式进游戏](#④-固定模式进游戏)

## 目录

* [界面总览](#界面总览)
* [快速上手](#快速上手)
* [管理器详解](#管理器详解)
    * [导入页](#导入页)
    * [展示页](#展示页)
    * [底部工具栏](#底部工具栏)
* [悬浮窗详解](#悬浮窗详解)
* [支持的游戏](#支持的游戏)
* [下载与运行](#下载与运行)
* [故障排查](#故障排查)
* [路线图](#路线图)
* [补充说明](#补充说明)


# 界面总览

本中文版由两个窗口组成：

* **管理器**（普通窗口，不置顶）：负责一切管理操作——导入流程、选择流程、调整悬浮窗外观、切换悬浮窗状态。启动程序后首先出现的就是管理器。
* **悬浮窗**（置顶、无边框）：只负责展示建造顺序，由管理器控制，有两种模式：
    * **移动模式**：整窗可拖动，用于把悬浮窗摆到游戏中合适的位置；也可以先点按钮预览流程。
    * **固定模式**：不可拖动，只有按钮可以点击，其余区域点击穿透直达游戏——进游戏后使用。

<table>
  <tr>
    <td align="center"><img src="/readme/manager_import.jpg" alt="管理器·导入页" width="420"/><br/><sub>管理器 · 导入页</sub></td>
    <td align="center"><img src="/readme/manager_display.png" alt="管理器·展示页" width="420"/><br/><sub>管理器 · 展示页</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="/readme/overlay_move_mode.png" alt="悬浮窗·移动模式" width="420"/><br/><sub>悬浮窗 · 移动模式</sub></td>
    <td align="center"><img src="/readme/overlay_fixed_mode.png" alt="悬浮窗·固定模式" width="420"/><br/><sub>悬浮窗 · 固定模式</sub></td>
  </tr>
</table>


# 快速上手

以帝国时代2为例，四步开始使用：

## ① 导入建造顺序

在管理器的"导入"页，先去流程网站复制要用的建造顺序（页面上有"打开流程网站"按钮），然后点击"**从剪贴板导入**"。
名称栏留空时使用流程自带的名称；也可以先填写名称再导入。

## ② 选择与配置

切换到"展示"页：列表会直接显示当前游戏的全部流程，单击流程即可选中。
如需调整悬浮窗的背景色、不透明度、字号、缩放或显示行数，展开"外观"折叠区。

## ③ 开启悬浮窗

点击"**开启悬浮窗**"，此时悬浮窗处于移动模式——按住悬浮窗任意位置拖动，摆到游戏中方便查看的位置；也可以先点按钮翻看流程。

## ④ 固定模式进游戏

把状态切换为"**固定模式**"（点击悬浮窗上的隐藏按钮左侧的状态按钮，或指引栏的"④ 固定悬浮窗"），然后进入游戏：
用悬浮窗上的按钮或全局快捷键推进步骤，其余区域点击会穿透到游戏，不影响操作。


# 管理器详解

## 导入页

* **选择游戏**：游戏下拉列表决定后续所有内容（流程列表、流程网站、悬浮窗），默认为帝国时代2（AoE2）。切换游戏会立即重建悬浮窗与流程列表。
* **查找流程**：显示当前游戏已导入的流程数量，方便决定是否需要额外获取；"打开流程网站"按钮根据所选游戏打开对应网站（帝国时代2 为 buildorderguide.com，帝国时代4 为 aoe4guides.com，其他游戏为 RTS Builds）。
* **导入流程**：从流程网站复制建造顺序后点击"从剪贴板导入"。名称栏留空时使用流程内部的名称，填写后以填写的名称保存（同名流程会提示冲突）。导入成功后流程立即出现在"展示"页的列表中；"打开流程文件夹"可查看已保存的流程文件。

## 展示页

* **选择流程**：列表默认显示当前游戏的全部流程，也可以输入关键词筛选、按文明/阵营下拉过滤。单击流程即可在悬浮窗中展示；**右键单击流程可重命名或删除**——删除会把流程文件移入游戏配置目录下的"弃用区"文件夹（不会真正删除，可自行清理）。
* **悬浮窗开关与状态**："开启悬浮窗 / 关闭悬浮窗"控制悬浮窗显示；状态按钮在"移动模式"和"固定模式"之间切换（见[悬浮窗详解](#悬浮窗详解)）。
* **外观（折叠区）**：
    * 背景色 / 不透明度：改动即时生效。
    * 字号 / 缩放：字体大小与整体布局缩放（4K 显示器可将缩放设为 200 %）。
    * **显示行数**（1-5，默认 3）：手动模式下悬浮窗一次显示的说明行数（见[显示行数与按页推进](#显示行数与按页推进)）。
* **展示控制（折叠区）**：与悬浮窗按钮等效的操作按钮——开始/停止计时、上一步、下一步、归零。
* **快捷键（折叠区）**："打开快捷键配置窗口"可自定义全部快捷键（支持键盘与鼠标组合）。全局快捷键在游戏中无需悬浮窗获得焦点即可使用。

## 底部工具栏

保存设置 / 打开设置文件夹 / 界面主题（浅色、深色，默认浅色）/ 退出。
提示：关闭管理器窗口即退出整个程序；最小化管理器不影响悬浮窗。


# 悬浮窗详解

## 按钮与信息

悬浮窗顶部一行从左到右：步骤进度（如"步骤: 3/14"）、按钮组。

* **开始/停止计时**：仅当流程包含时间参数时显示；手动模式下点击会自动切入计时模式并开始。
* **上一步 / 下一步**：翻动流程（手动模式下按页翻动，见下文）；计时运行时兼作 ±1 秒。
* **隐藏悬浮窗**：**连点两次**才会隐藏（第一次点击按钮会出现红色描边提示，2 秒内不点自动解除），防止误操作。

按钮平时隐藏，鼠标移入悬浮窗区域时浮现；固定模式下其余区域点击会穿透到游戏。

## 移动模式与固定模式

* **移动模式**：左键按住悬浮窗任意位置拖动；按钮可以点击，方便进游戏前预览流程。
* **固定模式**：窗口不可拖动；按钮可以点击；其余区域点击穿透到游戏。

## 显示行数与按页推进

手动模式下，悬浮窗一次显示最多 N 行说明（"外观"折叠区的"显示行数"，默认 3 行）：

* 从当前步开始累计说明行，凑满设定行数为一页；"下一步"翻到下一页，"上一步"回上一页。
* 一行说明的流程（如"15 min Knight Spam"）一页显示 3 步——少点几次按钮。
* 单步就有多行说明的流程（如"Hera Chinese"）自然一页一步，不会被截断。
* 设为 1 时与原版单步显示一致。
* 资源行显示页内最后一步的目标值；"步骤: X/Y"中的 X 为页内最后一行的序号。

## 位置记忆

悬浮窗位置自动记忆（默认锚定右上角，可在设置中改为左上角），重启程序后恢复到上次的位置。

## 全局快捷键

以下快捷键可在快捷键配置窗口中修改（支持键盘与鼠标组合）：

* 切换移动/固定模式、显示/隐藏悬浮窗
* 建造顺序上一步 / 下一步
* 计时器：开始、停止、开始/停止、归零、计时/手动切换
* 回车选择搜索结果、Tab 选择下一个流程

具体默认键位见快捷键配置窗口。


# 支持的游戏

目前支持以下游戏：

* [帝国时代2 决定版（Age of Empires II Definitive Edition）](https://www.ageofempires.com/games/aoeiide/)
    * 从 [buildorderguide.com](https://www.buildorderguide.com)（点击 *Export for RTS*）或 [RTS Builds](https://craftysalamander.github.io/rtsbuilds/?gameId=aoe2)（点击 *Open in RTS Overlay*）获取建造顺序。
    * YouTube 演示见[这里](https://youtu.be/tONaR2oOt3I)。

[![帝国时代2建造顺序实际效果](/readme/aoe2_build_order_demo.webp)](https://youtu.be/tONaR2oOt3I)

* [帝国时代4（Age of Empires IV）](https://www.ageofempires.com/games/age-of-empires-iv/)
    * 从 [aoe4guides.com](https://aoe4guides.com) 或 [RTS Builds](https://craftysalamander.github.io/rtsbuilds/?gameId=aoe4)（点击 *Open in RTS Overlay*）获取建造顺序。

[![帝国时代4建造顺序实际效果](/readme/aoe4_build_order_demo.webp)](https://youtu.be/RmsofE58YEg)

* [神话时代（Age of Mythology）](https://www.ageofempires.com/games/aom/age-of-mythology-retold/)
    * 从 [RTS Builds](https://craftysalamander.github.io/rtsbuilds/?gameId=aom)（点击 *Open in RTS Overlay*）获取建造顺序。
    * YouTube 演示见[这里](https://youtu.be/f11ISkuVhnU)。

[![神话时代建造顺序实际效果](/readme/aom_build_order_demo.webp)](https://youtu.be/f11ISkuVhnU)

* [星际争霸2（StarCraft II）](https://starcraft2.com)

![星际争霸2建造顺序实际效果](/readme/sc2_build_order_demo.webp)

* [魔兽争霸3（Warcraft III）](https://warcraft3.blizzard.com/)


# 下载与运行

## 从源码运行（本中文版，新界面）

本中文版的新界面目前通过源码运行（需要 Python 环境）：

1. 如果你还没有 Python 环境，可以通过 [Anaconda 安装包](https://www.anaconda.com/download)安装带 conda 包管理器的 Python 发行版（也可以用 [Miniforge](https://github.com/conda-forge/miniforge#miniforge3)）。
2. 下载本仓库代码：点击本页面顶部的 *Code* 按钮 → *Download ZIP* 并解压（或使用 [Git](https://git-scm.com/) 克隆）。
3. 打开 *Anaconda Prompt*，进入解压后文件夹中的 python 目录（例如 `cd RTS_Overlay-master/python`）。
4. 创建并激活 Conda 环境：`conda create --name rts_overlay python=3.8`，然后 `conda activate rts_overlay`
   （建议使用 Python 3.8：新版 Python 与依赖库 pynput 存在兼容性问题，会导致全局快捷键失效）。
5. 安装依赖：`pip install -r utilities/requirements.txt`
6. 运行：`python main_aoe2.py`（以 AoE2 为例，其他游戏运行对应的 main_*.py）。

每次运行程序前需要重新执行第 3 步的进入目录与第 4 步的激活环境（激活后第 5 步只需一次）。

流程与设置保存在 `python/local_config` 文件夹内（便携式，不写入系统目录），首次运行会自动迁移旧版本在系统 AppData 的配置（原数据保留）。

## 网页版（原项目逻辑，未汉化）

网页版保持原项目逻辑，可直接在浏览器使用：访问 [rts-overlay.github.io](https://rts-overlay.github.io/) 并按页面说明操作。
完整说明可鼠标悬停在页面右上角的 "i" 图标上查看。

![网页版 RTS Overlay](/readme/rts_overlay_web.webp)

* 有两种显示模式："画中画"（自动置顶）和"经典窗口"（需借助窗口置顶工具，推荐 [PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/)）。
* 也可以在"设计你的建造顺序"（**Design your own**）中在线设计流程（演示见[这里](https://youtu.be/dst2b8b4_fo)）。

![建造顺序设计](/readme/rts_overlay_aoe2_editor.gif)

## EXE 版（免 Python 环境）

**本中文版 EXE**：从本仓库的 [Releases](https://github.com/wizacro/RTS_Overlay/releases) 页面下载 `aoe2_overlay.zip`（目前提供帝国时代2，其余游戏请使用上方"从源码运行"），解压后**双击根目录的 `aoe2_overlay.exe`** 即开即用、无需安装 Python。内置"新手全流程（不拉野）"示例流程，首次启动自动启用。

流程与设置保存在工具目录的 `local_config` 文件夹内（便携式，不写入系统目录），整个文件夹拷走即可带走全部数据；首次运行会自动把旧版本存放在系统 AppData 的配置迁移过来（原数据保留）。

原项目也提供预编译 EXE（[原项目发布页](https://github.com/CraftySalamander/RTS_Overlay/releases)，含其他游戏），注意那是**旧版单窗口界面**（英文），不含本中文版的管理器界面。

## 故障排查

* **网页版问题**：换一个浏览器（Chrome、Edge）试试；就本悬浮窗而言，Edge 和 Chrome 通常比 Firefox 表现更好。
* **EXE 版**（原项目 EXE）：若提示 "cannot proceed because python38.dll was not found"，请在解压前解除 zip 压缩包的锁定（右键 → 属性 → 勾选"解除锁定"）；Windows 或杀毒软件可能将 *.exe* 识别为威胁，需添加 Defender 例外规则。
* **源码版（本中文版）**：
    * 悬浮窗已启动但看不到：可能是位置在屏幕外，检查工具目录下 `local_config\对应游戏\settings\` 中的设置文件；或先在管理器关闭再重新开启悬浮窗。
    * 全局快捷键失效：确认使用了 Python 3.8 环境（新版 Python 与 pynput 不兼容）。
* **首次运行 EXE 提示"Windows 已保护你的电脑"**：这是 SmartScreen 对无数字签名程序的常规拦截（原项目 EXE 同样如此，并非报毒）。点击"更多信息"→"仍要运行"即可，只会拦截第一次；或解压前先右键 zip → 属性 → 勾选"解除锁定"。
    * 更多问题可在 [原项目 Issues](https://github.com/CraftySalamander/RTS_Overlay/issues) 提交（英文），或在本 fork 的 Issues 提交（中文）。


# 路线图

当前开发聚焦**帝国时代2（AoE2）**的建造流程体验，以下为计划中的后续方向：

* 其余游戏（帝国时代4 / 神话时代 / 星际争霸2 / 魔兽争霸3）的管理器优化与图标数据完善
* 其余游戏的 EXE 打包发布
* 网页版界面中文化
* 文明 / 科技 / 兵种等数据名称的中文翻译
* 流程要点窗口支持其余游戏

# 补充说明

**RTS Overlay** 与上述游戏的开发商/发行商没有任何关联。

对于暴雪-微软系游戏，**RTS Overlay** 是依据微软"[Game Content Usage Rules](https://www.xbox.com/en-us/developers/rules)"（游戏内容使用规则）使用相应游戏素材创建的，未获得微软的认可，也与微软无从属关系。

## 本中文版的改动概览

基于原项目 v2.15.0 的主要改动（详见 [Changelog](Changelog.md)）：

* **界面全面汉化**（浅色/深色主题，默认浅色）。
* **管理器 + 悬浮窗双窗口**：管理器集中管理（导入/选择/外观/快捷键），悬浮窗只负责展示与步进。
* **移动/固定双模式**：布置时整窗拖动，游戏中按钮可点、其余区域穿透。
* **从剪贴板一键导入**，流程列表支持右键重命名/删除（删除=移入"弃用区"文件夹）。
* **显示行数设置**：手动模式按页推进，减少点击次数。
* **游戏下拉切换**：一个管理器管理全部支持的游戏。
