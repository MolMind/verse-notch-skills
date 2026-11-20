---
name: versenotch-lyric-style
description: 为支持 lyric-style v1 的 VerseNotch 制作、校验和打包声明式歌词样式 .vnplugin。适用于文字、背景、高亮和过渡样式。
---

# 制作 VerseNotch 歌词样式

此技能生成适用于 VerseNotch 0.2.0 起的本地声明式歌词样式。先阅读 [v1 契约](references/lyric-style-v1.md)，用 [模板](assets/lyric-style/) 提供的清单和样式配置建立独立源目录。

1. 确认稳定的反向域名 ID、版本、作者、许可证和目标客户端版本。更新已有插件时保留 ID。模板许可证为 `UNLICENSED`，准备对外发布时使用作者确认的许可证和可分发素材。
2. 通过 `style.json` 选择文字、背景和高亮效果。配置只使用契约声明的字段和宿主能力。随包图片为 PNG 或 JPEG，置于 `assets/`，其余资源由宿主提供。
3. 使用 Python 3.10 或以上版本运行技能目录下的命令。先校验源目录，再打包和验证生成的包。

   ```sh
   python3 scripts/vnplugin.py validate /path/to/source
   python3 scripts/vnplugin.py pack /path/to/source /path/to/example.vnplugin
   python3 scripts/vnplugin.py validate /path/to/example.vnplugin
   ```

交付源目录、`.vnplugin`、插件 ID、版本和校验结果。如果有兼容客户端，在用户授权下用「插件库 → 从文件导入」检查预览和应用效果，并记录实测状态。发布和市场送审是独立操作。
