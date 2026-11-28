---
name: versenotch-language
description: 制作、校验和打包 VerseNotch macOS 客户端的界面语言插件。用于翻译菜单、界面标签、提示和无障碍文案，以及更新已有语言包。
---

# 制作 VerseNotch 语言插件

1. 复制 [日语示例](assets/ja/) 到新的工作目录。使用自己的反向域名 ID，在 `name` 填写目标语言的自称。更新已有插件时沿用 ID 并提高版本号。
2. 按 [v1 包规范](references/language-v1.md) 修改 `strings.json`。按包的 minAppVersion 从 [0.3.0 文案目录](references/strings-0.3.0.json) 或 [0.2.5 文案目录](references/strings-0.2.5.json) 选择键，保留原文中每个数字占位符。可按目标语言调整占位符顺序。优先翻译导航、插件操作、播放器控制与提示。
3. 运行随附脚本。命令接受插件目录或已打包的文件，并报告覆盖率。

   ```sh
   python3 scripts/vnlanguage.py validate /path/to/source
   python3 scripts/vnlanguage.py pack /path/to/source /path/to/language.vnplugin
   python3 scripts/vnlanguage.py validate /path/to/language.vnplugin
   ```

4. 打开 VerseNotch 0.2.5 或更高版本。通过「插件库 → 从文件导入」安装，再在「语言插件」中启用。检查主窗口、菜单栏、浮窗控制、包含动态数据的提示和无障碍标签。检查长译文在窄窗口的显示、遗漏文案的中文回退、重启恢复及卸载当前语言的行为。交付源目录、`.vnplugin` 和实测结果。
